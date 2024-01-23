import shutil
from sys import argv
import os
from yt_dlp import YoutubeDL
import argparse

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


def startup_and_options(sysargs):
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The youtube url to download and convert")
    parser.add_argument("--debug", action='store_true', help="Activate debug mode which asks for no input")
    args = parser.parse_args(sysargs)
    if not args.debug:
        if input("Would you like to boost the volume? Y/N").lower() == "y":
            boost = True
            name = input("What should the file name be? ")
    else:
        name = "DEBUGoutput"
        boost = False
    return {"boost": boost, "debug": args.debug, "name": name, "url": args.url}


def stripurl(url):
    short = url.replace("youtube.com/watch?v=", "youtu.be/").replace(
        "https://www.", "https://"
    )
    if "si=" in short:
        short = short.split("si=")[0][:-1]
    return short


def download(url):
    shorturl = stripurl(url)
    with YoutubeDL(yt_options) as ydl:
        ydl.download([shorturl])


def boost(doIt):
    if doIt:
        os.system('ffmpeg -i vid.mp4 -af "volume=3" -c:v copy output.mp4')
        os.unlink("vid.mp4")
    else:
        shutil.move("vid.mp4", "output.mp4")


def convert(toName):
    os.system(f"python helper1.py output.mp4 {toName}.bnd")


def main():
    options = startup_and_options(argv[1:])
    boo = options["boost"]
    debug = options["debug"]
    name = options["name"]
    url = options["url"]
    download(url)
    boost(boo)
    convert(name)
    if debug or input("Delete Intermediate File? [N/y]").strip().lower().startswith(
            "y"
    ):
        os.unlink("output.mp4")


if __name__ == "__main__":
    main()
