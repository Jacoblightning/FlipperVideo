import shutil
from sys import argv
import os
from yt_dlp import YoutubeDL

yt_options = {
    "extract_flat": "discard_in_playlist",
    "final_ext": "mp4",
    "format": "mp4",
    "fragment_retries": 10,
    "ignoreerrors": "only_download",
    "noplaylist": True,
    "outtmpl": {"default": "vid.mp4"},
    "postprocessors": [
        {
            "api": "https://sponsor.ajay.app",
            "categories": {"selfpromo", "sponsor"},
            "key": "SponsorBlock",
            "when": "after_filter",
        },
        {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        {
            "force_keyframes": False,
            "key": "ModifyChapters",
            "remove_chapters_patterns": [],
            "remove_ranges": [],
            "remove_sponsor_segments": {"selfpromo", "sponsor"},
            "sponsorblock_chapter_title": "[SponsorBlock]: " "%(category_names)l",
        },
        {"key": "FFmpegConcat", "only_multi_video": True, "when": "playlist"},
    ],
    "retries": 10,
}


if len(argv) < 2:
    raise RuntimeError("NEED MORE ARGUMENTS, IM HUNGRY 4 THE ARGUMENTS")

b = False
if input("Would you like to boost the volume? Y/N").lower() == "y":
    b = True
short = (
    argv[1]
    .replace("youtube.com/watch?v=", "youtu.be/")
    .replace("https://www.", "https://")
)
if "si=" in short:
    short = short.split("si=")[0][:-1]
name = input("What should the file name be? ")

with YoutubeDL(yt_options) as ydl:
    ydl.download([short])
if b:
    os.system('ffmpeg -i vid.mp4 -af "volume=3" -c:v copy output.mp4')
    os.unlink("vid.mp4")
else:
    shutil.move("vid.mp4", "output.mp4")

os.system(f"python helper1.py output.mp4 {name}.bnd")
if input("Delete Intermediate File? [N/y]").strip().lower().startswith("y"):
    os.unlink("output.mp4")
