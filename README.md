# FlipperVideo
A helper to install video files on a Flipper Zero (Get yours now at shop.flipperzero.one)

# Credits

All credit for the script helper1.py goes to JacobTDC. Find the original script [here](https://gist.github.com/JacobTDC/524322a78bb0ba5008604d905ccd4270)

# Converting a YouTube video

To convert a YouTube video to a flipper file:

run the `yt2flip.py` file with no arguments.

# Converting an mp4

To skip the downloading and convert an mp4 file directly, 

run `helper1.py <inputfile.mp4> <outputfile.bnd>`

# Transfering to flipper

When your file is done, move it to the flippers sd card into apps_data/video_player (I advise that you remove the SD card from your Flipper and connect it to your PC/laptop somehow, or wait all the night when it uploads via qFlipper.)

# Things to note

I have included the .fap file but it is recommended to install unlshd firmware [here](https://github.com/DarkFlippers/unleashed-firmware) (If installing Unlshd firmware, remember to install the extra apps version or it will not install the vieo_player)

# For the future

| Task                  | Started | Done |
|-----------------------|:-------:|-----:|
| Publish to pypi       |   Yes   |  No  |
| Delete the batch file |   Yes   |  Yes |
| Post examples         |   No    |  No  |
