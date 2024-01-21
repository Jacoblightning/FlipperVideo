#!/usr/bin/env python3
import argparse
import locale
import math
import struct
import subprocess
import sys
import textwrap
import tqdm

from fractions import Fraction
from pathlib import Path

import ffmpeg

# set locale to user default
locale.setlocale(locale.LC_ALL, "")

# just some "constants"
BUNDLE_SIGNATURE = "BND!VID"
BUNDLE_VERSION = 1
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64


# a class to make sure a valid scale is given in args
class VideoScale:
    def __init__(self, scale):
        [self.width, self.height] = list(map(int, scale.split("x")))
        if not (1 <= self.width <= SCREEN_WIDTH and 1 <= self.height <= SCREEN_HEIGHT):
            raise ValueError(f"{scale} not in range 1x1 to 128x64")

    def __str__(self):
        return f"{self.width:d}x{self.height:d}"


# a function to make sure a valid threshold is given in args
def Threshold(t):
    t = int(t)
    if not (0 <= t <= 255):
        raise ValueError(f"{t:d} not in range 0 to 255")
    return t


# python uses half round even, but we need to use half round up
# in order to get an accurate frame count, because that's what
# ffmpeg uses when changing frame rates
def fraction_half_round_up(fraction):
    if fraction % 1 < Fraction(1, 2):
        return math.floor(fraction)
    return math.ceil(fraction)


# setup the argument parser
parser = argparse.ArgumentParser(
    description="A utility to convert videos to a format playable on the Flipper Zero."
)

parser_exclusive_1 = parser.add_mutually_exclusive_group()

parser.add_argument(
    "source",
    type=Path,
    help="the source file; must contain exactly one video and one audio stream",
)
parser.add_argument("output", type=Path, help="the resulting bundle")
parser_exclusive_1.add_argument(
    "-d",
    "--dither",
    choices=[
        "bayer",
        "heckbert",
        "floyd_steinberg",
        "sierra2",
        "sierra2_4a",
        "sierra3",
        "burkes",
        "atkinson",
        "none",
    ],
    default="sierra3",
    metavar="ALGORITHM",
    help="the dithering algorithm to use, or 'none' to disable; defaults to 'sierra3'",
)
parser_exclusive_1.add_argument(
    "-t",
    "--threshold",
    type=Threshold,
    help="the threshold to apply when converting to black and white, from 0 to 255; cannot be used with dithering",
)
parser.add_argument(
    "-f",
    "--frame-rate",
    type=Fraction,
    dest="frame_rate",
    help="the desired video frame rate, may be a fraction; defaults to source frame rate",
)
parser.add_argument(
    "-s",
    "--scale",
    type=VideoScale,
    dest="scale",
    help=f"the desired video size, cannot be larger than {SCREEN_WIDTH:d}x{SCREEN_HEIGHT:d}; default best fit",
)
parser.add_argument(
    "-r",
    "--sample-rate",
    type=int,
    dest="sample_rate",
    help="the desired audio sample rate; defaults to the source sample rate",
)
parser.add_argument(
    "-q", "--quiet", action="store_true", help="don't output info to stdout"
)

args = parser.parse_args()

# get media information
ffprobe_result = ffmpeg.probe(args.source, count_packets=None)
for stream in ffprobe_result["streams"]:
    if stream["codec_type"] == "video":
        source_frame_count = int(stream["nb_read_packets"])
        source_width = int(stream["width"])
        source_height = int(stream["height"])
        source_frame_rate = Fraction(stream["r_frame_rate"])
    if stream["codec_type"] == "audio":
        source_sample_rate = int(stream["sample_rate"])

# get the video dimensions before padding
if args.scale == None:
    # default: maintain aspect ratio and scale to fit screen
    scale_factor = max(source_width / 128, source_height / 64)
    pre_pad_width = math.floor(source_width / scale_factor)
    frame_height = math.floor(source_height / scale_factor)
else:
    # user defined dimensions
    pre_pad_width = args.scale.width
    frame_height = args.scale.height

# get width after padding and final frame size
frame_width = pre_pad_width + 8 - (pre_pad_width % 8)
frame_size = int(frame_width * frame_height / 8)

# calculate stream rates and sizes
sample_rate = args.sample_rate or source_sample_rate
frame_rate = args.frame_rate or source_frame_rate
audio_chunk_size = int(sample_rate / frame_rate)
frame_count = fraction_half_round_up(
    source_frame_count * frame_rate / source_frame_rate
)
estimated_file_size = int(
    (((frame_width * frame_height) / 8) + audio_chunk_size) * frame_count
    + len(BUNDLE_SIGNATURE)
    + 11
)

# print final bundle info
if not args.quiet:
    print(
        textwrap.dedent(
            f"""\
        Frame rate:                   {float(frame_rate):g} fps
        Frame count:                  {frame_count:d} frames
        Video scale (before padding): {pre_pad_width:d}x{frame_height:d}
        Video scale (after padding):  {frame_width:d}x{frame_height:d}
        Audio sample rate:            {sample_rate:d} Hz
        Audio chunk size:             {audio_chunk_size:d} bytes
        Estimated file size:          {estimated_file_size:n} bytes
        """
        )
    )

    if frame_rate > 30:
        print("warning: frame rate is greater than maximum recommended 30 fps\n")

    if frame_count > source_frame_count:
        print(
            f"warning: {frame_count - source_frame_count:d} frames will be duplicated\n"
        )

    if frame_count < source_frame_count:
        print(f"warning: {source_frame_count - frame_count:d} frames will be dropped\n")

    if sample_rate > 48000:
        print("warning: sample rate is greater than maximum recommended 48 kHz\n")

    if (sample_rate / frame_rate).denominator != 1:
        # TODO: calculate desync
        print(
            "warning: sample rate is not cleanly divisible by frame rate, this may result in a (usually imperceptible) desync\n"
        )

# open the output file for writing
output = open(args.output, "wb")

# specify the input file
input = ffmpeg.input(args.source)

audio_process = (
    input.audio
    # normalize audio to prevent peaking
    .filter("loudnorm")
    # output raw 8-bit audio
    .output("pipe:", format="u8", acodec="pcm_u8", ac=1, ar=sample_rate)
    # only display errors
    .global_args("-v", "error").run_async(pipe_stdout=True)
)

scaled_video = (
    input.video
    # scale the video
    .filter("scale", pre_pad_width, frame_height)
    # convert to grayscale
    .filter("format", "gray")
    # set the frame rate
    .filter("fps", frame_rate)
)

if args.threshold != None:
    # convert to black and white with threshold
    video_input = scaled_video.filter(
        "maskfun", low=args.threshold, high=args.threshold, sum=256, fill=255
    )
else:
    # the palette used for dithering
    palette = ffmpeg.filter(
        [
            ffmpeg.input("color=c=black:r=1:d=1:s=8x16", f="lavfi"),
            ffmpeg.input("color=c=white:r=1:d=1:s=8x16", f="lavfi"),
        ],
        "hstack",
        2,
    )

    # convert to black and white with dithering
    # TODO: add option for setting bayer_scale
    video_input = ffmpeg.filter(
        [scaled_video, palette], "paletteuse", new="true", dither=args.dither
    )

video_process = (
    video_input
    # pad the width to make sure it is a multiple of 8
    .filter("pad", frame_width, frame_height, 0, 0, "white")
    # output raw video data, one bit per pixel, inverted, and
    # disable dithering (we've already handled it)
    .output("pipe:", sws_dither="none", format="rawvideo", pix_fmt="monow")
    # only display errors
    .global_args("-v", "error").run_async(pipe_stdout=True)
)

# header format:
#  signature (char[7] / 7s): "BND!VID"
#  version (uint8 / B): 1
#  frame_count (uint32 / I)
#  audio_chunk_size (uint16 / H): sample_rate / frame_rate
#  sample_rate (uint16 / H)
#  frame_height (uint8 / B)
#  frame_width (uint8 / B)
header = struct.pack(
    f"<{len(BUNDLE_SIGNATURE):d}sBIHHBB",
    BUNDLE_SIGNATURE.encode("utf8"),
    BUNDLE_VERSION,
    frame_count,
    audio_chunk_size,
    sample_rate,
    frame_height,
    frame_width,
)

# write the header to the file
output.write(header)
bytes_written = len(header)

for frame_num in tqdm.tqdm(range(1, frame_count + 1), unit="frame"):
    # read a single frame and audio chunk
    frame = video_process.stdout.read(frame_size)
    audio_chunk = audio_process.stdout.read(audio_chunk_size)

    frame_data = bytearray()
    for byte in frame:
        # reverse the bit-order of each byte in the frame
        frame_data.append(int(f"{byte:08b}"[::-1], 2))

    # write frame and audio data
    output.write(frame_data)
    output.write(audio_chunk)
    bytes_written += len(frame_data) + len(audio_chunk)

# close the file descriptor
output.close()

# wait for ffmpeg processes to finish
video_process.wait()
audio_process.wait()

if not args.quiet:
    print()
    print(f"{bytes_written:n} bytes written to {args.output}\n")

    if bytes_written != estimated_file_size:
        print(
            f"warning: number of bytes written does not match estimated file size, something may have gone wrong\n"
        )
