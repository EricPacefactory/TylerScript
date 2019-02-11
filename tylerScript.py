#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 14:26:42 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports

import os
import cv2
import numpy as np

from local.eolib.utils.files import guiLoadMany, guiSave
from local.eolib.utils.cli_tools import cli_prompt_with_defaults
from local.eolib.video.windowing import SimpleWindow, Progress_Bar, breakByKeypress, center_window
from local.eolib.video.read_write import Video_Reader, Video_Recorder

    
# ---------------------------------------------------------------------------------------------------------------------
#%% Define functions

# .....................................................................................................................

def get_target_frames(video_object_list, current_index, frame_index_lists):
    
    target_frames = []
    for v_idx, each_video_object in enumerate(video_object_list):
        
        # Figure out what frame (index) we want from the given video object and what frame we're currently on
        target_idx = frame_index_lists[v_idx][current_index]
        current_idx = each_video_object.current_frame()
        
        while True:
            
            # Get another frame from the given video
            (request_break, new_frame) = each_video_object.read()
            if request_break:
                print("Bad frame! Video {} frame {} / {}".format(v_idx, current_idx, target_idx))
                new_frame = None
                break
            current_idx += 1
            
            # Once we get the target frame (based on frame index), stop the loop and move on
            if current_idx >= target_idx:
                break
            
        # Finally, add the frame to the output list
        target_frames.append(new_frame)
    
    return target_frames

# .....................................................................................................................

def get_scaled_frames(frame_list, num_blank_frames, tileWH):
    
    # Replace any bad frames with blanks
    bad_frames = [each_frame is None for each_frame in frame_list]
    if any(bad_frames):
        bad_frame = np.zeros((tileWH[1], tileWH[0], 3), dtype=np.uint8)
        frame_list = [each_frame if not bad else bad_frame for each_frame, bad in zip(frame_list, bad_frames)]
        
    # Scaled down each frame, so that the resulting stacked image won't be too large
    scaled_frames = [cv2.resize(each_frame, dsize = tileWH) for each_frame in frame_list]
    
    # Append blank frames if needed
    if num_blank_frames > 0:   
        blank_frame = np.zeros((tileWH[1], tileWH[0], 3), dtype=np.uint8)
        for k in range(num_blank_frames):
            scaled_frames.append(blank_frame.copy())
    
    return scaled_frames

# .....................................................................................................................

def get_stacked_image(scaled_frames, num_rows, num_cols):

    row_image_list = []
    for row_idx in range(num_rows):
        col_stack = []
        for col_idx in range(num_cols):
            vid_idx = row_idx * num_cols + col_idx
            col_stack.append(scaled_frames[vid_idx])
        
        col_stack_image = np.hstack((col_stack))
        row_image_list.append(col_stack_image)
        
    return np.vstack(row_image_list)

# .....................................................................................................................

def get_videos(video_path_list):
    video_objects = [Video_Reader(each_path) for each_path in video_path_list]
    return video_objects

# .....................................................................................................................

def get_frame_indices(video_object_list, num_output_frames):
    
    frame_index_lists = []
    for each_video_object in video_object_list:
        each_frame_count = each_video_object.info("frame_count")
        raw_frame_idx = np.linspace(0, each_frame_count - 1, num_output_frames)
        each_index_list = np.int32(np.round(raw_frame_idx))
        frame_index_lists.append(each_index_list)
        
    return frame_index_lists

# .....................................................................................................................

def get_tiling_size(video_object_list, num_rows, num_cols, target_max_size = (1280, 720)):
    
    # First figure out the sizing of all the videos
    video_widths = [each_video.info("width") for each_video in video_object_list]
    video_heights = [each_video.info("height") for each_video in video_object_list]
    video_areas = [each_width * each_height for each_width, each_height in zip(video_widths, video_heights)]
    
    # Use the largest video to decide on scaling factors to best fit target_max_size
    biggest_idx = np.argmax(video_areas)
    biggest_width = video_widths[biggest_idx]
    biggest_height = video_heights[biggest_idx]
    scale_x = target_max_size[0] / (biggest_width * num_cols)
    scale_y = target_max_size[1] / (biggest_height * num_rows)
        
    # Calculate the target scale (for each tiled video)
    scale_factor = min(scale_x, scale_y)
    tiled_width = int(round(scale_factor * biggest_width))
    tiled_height = int(round(scale_factor * biggest_height))
    tiledWH = (tiled_width, tiled_height)
    
    # Calculate the size of the tiled output image
    outputWH = (tiled_width * num_cols, tiled_height * num_rows)

    return outputWH, tiledWH

# .....................................................................................................................
    
def interpret_target_dimensions(dim_string, defaultWH):
    
    try:
        
        # Try to parse the string for two numbers
        split_num_strs = [each_str.strip() for each_str in dim_string.split("x")]
        split_nums = [int(each_num_str) for each_num_str in split_num_strs]
        
        # Decide on how to represent the dimensions if either 1 or 2 numbers were found
        num_numbers = len(split_nums)
        if num_numbers == 1:
            targetWH = (split_nums[0], split_nums[0])
        elif num_numbers == 2:
            targetWH = split_nums
        else:
            raise Exception
    
    except Exception:
        # If we get an error, call this function again with the default string for parsing
        print("Couldn't parse dimensions: {}".format(dim_string))
        print("Using: {} x {}".format(*defaultWH))
        targetWH = defaultWH
        
    return targetWH

# .....................................................................................................................

# .....................................................................................................................

# ---------------------------------------------------------------------------------------------------------------------
#%% Initialize variables

default_fps = 30.0
default_columns = 2
progress_bar_update_rate = 16

# ---------------------------------------------------------------------------------------------------------------------
#%% Select videos

# Get video list and name of videos for selection
video_list = guiLoadMany(windowTitle = "Select video files")
video_name_list = [os.path.basename(each_file) for each_file in video_list]
number_videos = len(video_list)

# Open all videos for initial info and then close them (untl we start recording)
video_objects = get_videos(video_list)
for each_video_object in video_objects:
    each_video_object.close()

# ---------------------------------------------------------------------------------------------------------------------
#%% Get output timing

# Have the user specify the output time
runtime_minutes = cli_prompt_with_defaults(prompt_message = "Enter output video length in minutes: ",
                                           return_type = float, 
                                           response_on_newline = False)

# Have the user specify the framerate of the output video
output_fps = cli_prompt_with_defaults(prompt_message = "Enter the output framerate: ",
                                      default_value = default_fps,
                                      return_type = float, 
                                      response_on_newline = False)

# Calculate the number of frames needed for the output video
runtime_seconds = runtime_minutes * 60
number_output_frames = int(round(1 + (output_fps * runtime_seconds)))


# ---------------------------------------------------------------------------------------------------------------------
#%% Configure tiling

# Have the user specify the number of columns to tile
number_columns = cli_prompt_with_defaults(prompt_message = "Enter the number of columns for tiling: ",
                                          default_value = default_columns,
                                          return_type = int, 
                                          response_on_newline = False)

# Calculate the required number of rows, based on the number of columns and how many blank cells there will be
number_rows = int(np.ceil(number_videos / number_columns))
number_blank = int(number_rows*number_columns - number_videos)

# Try to automatically figure out the tiling size
defaultWH, default_tiledWH = get_tiling_size(video_objects, number_rows, number_columns)

# Have the user specify the output video dimensions
defaultWH_str = "{} x {}".format(*defaultWH)
targetWH_str = cli_prompt_with_defaults("Enter output video size (w x h): ", 
                                        default_value = defaultWH_str,
                                        return_type = str)
outputWH = interpret_target_dimensions(targetWH_str, defaultWH)

# Calculate the tiled width/height
tiled_width = int(round(outputWH[0] / number_columns))
tiled_height = int(round(outputWH[1] / number_rows))
tiledWH = (tiled_width, tiled_height)


# ---------------------------------------------------------------------------------------------------------------------
#%% Set up recording
    
# Set up pathing
output_path = None
output_path = guiSave(windowTitle = "Save tiled video", fileTypes=[["video", ".avi"]])
enable_recording = (output_path is not None)

# Create recorder
video_out = Video_Recorder(save_path = output_path,
                           recording_FPS = output_fps,
                           enabled = enable_recording)
video_out.report_start()

# ---------------------------------------------------------------------------------------------------------------------
#%% Display setup

# Get frame indices
frame_index_lists = get_frame_indices(video_objects, number_output_frames)

# Set up display windows
dispWindow = SimpleWindow("Tiled Frame")
center_window(dispWindow, frameWH = outputWH)
prog_bar = Progress_Bar(total_iterations = number_output_frames, 
                        window_label = "Recording Progress",
                        update_rate = progress_bar_update_rate)

# Restart video objects so we can start grabbing frames for recording
for each_video_object in video_objects:
    each_video_object.reopen()


# ---------------------------------------------------------------------------------------------------------------------
#%% Recording loop

for k in range(number_output_frames):
    
    # Get target frame for each video object
    frame_list = get_target_frames(video_objects, k, frame_index_lists)
    
    # Resize each frame
    scaled_frame_list = get_scaled_frames(frame_list, number_blank, tiledWH)
    
    # Stack frames into tiled output image
    combined_frame = get_stacked_image(scaled_frame_list, number_rows, number_columns)
    
    # Record video!
    video_out.write(combined_frame, auto_resize = False)
    
    # Provide user feedback about recording progress
    dispWindow.imshow(combined_frame)
    prog_exists = prog_bar.update()
    if not prog_exists:
        break
    
    reqBreak, keypress = breakByKeypress(1)
    if reqBreak:
        break


# ---------------------------------------------------------------------------------------------------------------------
#%% Clean-up
    
# Close recorder
video_out.close()
video_out.report_end()
    
# Close video reading objects
for each_video_object in video_objects:
    each_video_object.close()
    
cv2.destroyAllWindows()


# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap


# TODOs
# - Use threaded frame grabbing
# - Use multiprocessing on each video while getting frames
# - Consider performing grab/retrieve steps separately when getting frames (so decoding can be skipped if needed)
# - Come up with better solution for videos that do not have all of 'total_frames'
# - Add option to include dividing lines when displaying tiled videos


