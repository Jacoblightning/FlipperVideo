
@echo off
set /p name= What should the file name be?
echo %1
python -m yt_dlp %1 -f mp4 --recode-video mp4 --no-playlist --sponsorblock-remove sponsor,selfpromo -o vid.mp4
if "%2" == "BOOST" (
    ffmpeg -i vid.mp4 -af "volume=3" -c:v copy output.mp4
) ELSE (
    move vid.mp4 output.mp4
)
rm vid.mp4
python helper2.py output.mp4 %name%.bnd
if ERRORLEVEL 1 exit /B
REM rm output.mp4
exit /B
