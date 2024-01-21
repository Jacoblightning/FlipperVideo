# Srsly just a replace thing since batch cant do it.
# *sigh* batch why can't you be more like bash?
import shutil
from sys import argv
import os

if len(argv) < 2:
    raise RuntimeError("NEED MORE ARGUMENTS, IM HUNGRY 4 THE ARGUMENTS")

b = False
if input("Would you like to boost the volume? Y/N").lower() == "y":
    b = True
short = argv[1].replace("youtube.com/watch?v=", "youtu.be/").replace("https://www.", "https://")
if "si=" in short:
    short = short.split("si=")[0][:-1]
# os.system("helper1.bat "+short+" "+b)
name = input("What should the file name be? ")
os.system(
    f"python -m yt_dlp {short} -f mp4 --recode-video mp4 --no-playlist --sponsorblock-remove sponsor,selfpromo -o vid.mp4"
)
if b:
    os.system('ffmpeg -i vid.mp4 -af "volume=3" -c:v copy output.mp4')
else:
    shutil.move("vid.mp4", "output.mp4")

os.system(f"python helper2.py output.mp4 {name}.bnd")
if input("Delete Intermediate File? [N/y]").strip().lower().startswith('y'):
    os.unlink('output.mp4')
