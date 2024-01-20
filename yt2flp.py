#Srsly just a replace thing since batch cant do it. 
#*sigh* batch why can't you be more like bash?
from sys import argv
import os
b="NO"
if input("Would you like to boost the volume? Y/N").lower()=="y":
    b="BOOST"
short = argv[1].replace("youtube.com/watch?v=", "youtu.be/").replace("https://www.", "https://")
if "si=" in short:
    short = short.split("si=")[0][:-1]
os.system("helper1.bat "+short+" "+b)
