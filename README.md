# TylerScript

Script for combining videos together in a tiled view.

## Requirements

Requires python3 (3.5+), tkinter, numpy and OpenCV (version 3.3.1+ should be fine). 

- Tested on Ubuntu 18.04
- The compiled version of OpenCV was used, not a pip install, so pip may/may not work
- The Ubuntu package manager was used to install tkinter (apt install python3-tk)

## Usage

This script takes no arguments, call using (in the appropriate environment):

```
python3 tylerScript.py
```

After launching the script, the first prompt will ask the user to select a set of videos to use for the output video. Use shift + left click or ctrl + left click to select multiple videos. These will be stitched together left-to-right, top-to-bottom, and the script does not allow the user to change this (though renaming the files manually will alter the order!). 

The user is then prompted to enter the length (in minutes) of the output video, the videos will each be timelapsed/stretched to match this target length. 

Next, the user is asked for a framerate. The default is 30, but this can be lowered for smaller filesizes, assuming the choppier appearance isn't a concern.

The user is then asked how many columns to use for tiling. The number of rows will be calculated automatically to fit the number of videos. Blank frames will be placed in cases where there aren't enough videos to fill each tile.

Finally, the user is asked to enter the output video size. The default size is automatially generated to aim for a maximum of 1280 x 720, without altering the aspect ratio of the videos. The user can enter a custom size, but note that the size of the tiles cannot be directly changed, they are shared for all videos and are calculated automatically from the output size.

## TODOs

- Performance improvements (threaded frame reading, multiprocessing each video read)
- Option to add dividing line graphics to better separate the display of each video
- Better solution to handle videos with missing frames
