#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 15:13:27 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports

import os
import cv2
import datetime as dt

# ---------------------------------------------------------------------------------------------------------------------
#%% Define classes

class Video_Recorder:
    
    # .................................................................................................................
    
    def __init__(self, save_path, recording_FPS, recording_WH = None, codec="X264", enabled = True):
            
        # Store inputs
        self.save_path = save_path
        self.fps = recording_FPS
        self.frameWH = recording_WH
        self.codec = codec
        self._disabled = (not enabled)
    
        # Create derived variables
        self.save_name = os.path.basename(save_path)
        self.save_name_only, self.save_extension = os.path.splitext(self.save_name)
        self._fourcc = cv2.VideoWriter_fourcc(*codec)
        self._video_writer = None
        
        # Store start time
        self.start_time = dt.datetime.now()
        self.end_time = None
        
        # Create frame counting variables for timelapsing
        self._frame_count = 0
        self._timelapse_factor = 1
        self._timelapse_enabled = False
        
        # Create initial recorder if a frame size is given
        if recording_WH is not None:
            self._create_video_writer()
        
    # .................................................................................................................
    
    def set_timelapse(self, timelapse_factor):  
        self._frame_count = 0
        self._timelapse_enabled = True
        self._timelapse_factor = timelapse_factor
        
    # .................................................................................................................
        
    def write(self, frame, auto_resize = True):
        # Mimic OpenCV writer function, but with size checks and built-in timelapsing
        
        # Handle disabled case
        if self._disabled:
            return False
        
        # Perform timelapsing if enabled
        if self._timelapse_enabled:
            if (self._frame_count % self._timelapse_factor) != 0:
                return False
        
        # If we haven't set the frame size yet, take the sizing info from the incoming frame
        if self.frameWH is None:
            frame_height, frame_width = frame.shape[0:2]
            self.frameWH = (frame_width, frame_height)
            self._create_video_writer()
        
        # If desired, automatically resize incoming frames if they don't match the target frame size
        if auto_resize:
            frame_height, frame_width = frame.shape[0:2]
            if self.frameWH[0] != frame_width or self.frameWH[1] != frame_height:
                frame = cv2.resize(frame, dsize = self.frameWH)
        
        # Write the current frame
        self._video_writer.write(frame)
        self._frame_count += 1
        
        # Return a value of true if a frame was recorded
        return True
        
    # .................................................................................................................
        
    def release(self):        
        if self._video_writer is not None:
            self._video_writer.release()
            self.end_time = dt.datetime.now()
        
    # .................................................................................................................
    
    def close(self):
        self.release()
       
    # .................................................................................................................
        
    def report_start(self, 
                     message = "Recording started",
                     report_time = True,
                     report_path = True, 
                     report_name = False, 
                     report_codec = True,
                     prepend_separator = True,
                     append_separator = True,
                     prepend_newline = True,
                     separator = "*" * 36,
                     report_disabled_warning = True,
                     disabled_message = "RECORDING DISABLED",
                     print_string = True,
                     return_string = False):
        
        # Handle case where recording is disabled
        if self._disabled:
            if not report_disabled_warning:
                return 
            message = disabled_message
        
        # Get starting time string
        time_now = dt.datetime.now()
        time_str = time_now.strftime("%Y/%m/%d %H:%M:%S")
            
        # Build output string based on function args
        add_str = lambda true_false, text, var: [text.format(var)] if true_false else []
        out_string_list = []
        out_string_list += add_str(prepend_newline, "", "")
        out_string_list += add_str(prepend_separator, separator, "")
        out_string_list += add_str(True, message, "")
        out_string_list += add_str(report_time, "  Time: {}", time_str)
        out_string_list += add_str(report_path, "  Path: {}", self.save_path)
        out_string_list += add_str(report_name, "  Name: {}", self.save_name)
        out_string_list += add_str(report_codec, "  Codec: {}", self.codec)
        out_string_list += add_str(append_separator, separator, "")
        str_to_print = "\n".join(out_string_list)
        
        # Only print to the terminal if desired
        if print_string:
            print(str_to_print)
            
        # Allow for a return, in case we want to log this info
        if return_string:
            return str_to_print
        
    # .................................................................................................................
    
    def report_end(self, 
                   message = "Recording finished!",
                   report_time = True,
                   report_path = False,
                   report_name = False,
                   report_codec = False,
                   prepend_separator = True,
                   append_separator = True,
                   prepend_newline = True,
                   separator = "*" * 36,
                   report_disabled_warning = False,
                   disabled_message = "RECORDING DISABLED",
                   print_string = True,
                   return_string = False):
        
        str_to_print = self.report_start(message, 
                                         report_time, 
                                         report_path, 
                                         report_name, 
                                         report_codec, 
                                         prepend_separator,
                                         append_separator, 
                                         prepend_newline, 
                                         separator, 
                                         report_disabled_warning, 
                                         disabled_message,
                                         print_string, 
                                         return_string)
        
        if return_string:
            return str_to_print
        
    # .................................................................................................................
    
    def find_valid_codec(self):
        
        # Function that should try making a few videos with various codecs to see which one works
        # (different systems may support different codecs!)
        raise NotImplementedError("Sorry, not done yet!")
        
    # .................................................................................................................
        
    def _create_video_writer(self, is_color = True):
        
        # Handle disabled case
        if self._disabled:
            return
    
    
        # Make sure the save pathing is ok
        os.makedirs(os.path.dirname(self.save_path), exist_ok = True)
        
        if self.frameWH is None:
            raise AttributeError("Frame size not set!")
            
        if self.codec is None:
            raise AttributeError("Codec not set")
            
        if self.fps is None:
            raise AttributeError("FPS not set")
        
        self._video_writer = cv2.VideoWriter(self.save_path,
                                             self._fourcc,
                                             self.fps,
                                             self.frameWH,
                                             is_color)
        
    # .................................................................................................................
    
    # .................................................................................................................
    
    # .................................................................................................................
    
    
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================

class Video_Reader:
    
    def __init__(self, source_path):
        
        # Check that source path is valid
        if not os.path.exists(source_path):
            raise FileNotFoundError("Couldn't find video: {}".format(source_path))
        
        # Get basic info about the video before opening
        self.video_source = source_path
        # figure out type of video
        # figure out naming (should be different for webcam, rtsp or files)
        self.video_folder = os.path.dirname(source_path)
        self.video_name = os.path.basename(source_path)
        self.video_name_only, self.video_extension = os.path.splitext(self.video_name)
        
        # Open the video
        self.video_object = cv2.VideoCapture(source_path)
        
        # Get the video info
        self.video_info = self._get_video_info()
    
    # .................................................................................................................
    
    def __repr__(self):
        out_string = ["********** Video Reader **********"]
        out_string += ["File: {}".format(self.video_name)]
        out_string += ["From: {}".format(self.video_folder)]
        out_string += ["Dimensions: {} x {}".format(*self.info("vidWH"))]
        out_string += ["Framerate: {}".format(self.info("framerate"))]
        out_string += ["Frame count: {}".format(self.info("frame_count"))]
        out_string += ["**********************************"]
        return "\n".join(out_string)
    
    # .................................................................................................................
    
    def read(self):
        
        received_frame, frame = self.video_object.read()
        request_break = (not received_frame)
        
        return request_break, frame
    
    # .................................................................................................................
    
    def release(self):
        
        try:
            self.video_object.release()
        except Exception:
            pass
        
    # .................................................................................................................
        
    def close(self):
        self.release()
        
    # .................................................................................................................
        
    def reopen(self):
        
        # Close the video if it is currently open
        if self.is_open():
            self.close()
            
        # Re-open the video
        self.video_object = cv2.VideoCapture(self.video_source)
    
    # .................................................................................................................
    
    def set_current_frame(self, frame_index):
        self.video_object.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
    # .................................................................................................................
    
    def set_current_progress(self, progress_fraction):
        frame_index = int(round((self.info("total_frames") - 1) * progress_fraction))
        self.video_object.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
    # .................................................................................................................
    
    def current_frame(self):
        return int(self.video_object.get(cv2.CAP_PROP_POS_FRAMES))
    
    # .................................................................................................................
    
    def current_time_ms(self):
        return self.video_object.get(cv2.CAP_PROP_POS_MSEC)
    
    # .................................................................................................................
    
    def current_time_sec(self):
        return 1000*self.current_time_ms()
    
    # .................................................................................................................
    
    def current_progress(self):
        return self.current_frame() / (self.info("total_frames" - 1))
    
    # .................................................................................................................
    
    def is_open(self):
        try:
            return self.video_object.isOpened()
        except AttributeError:
            return False
    
    # .................................................................................................................
    
    def _get_naming(self):
        pass
    
    # .................................................................................................................
    
    def _get_source_type(self):
        pass
    
    # .................................................................................................................
    
    def _get_video_info(self):

        total_frames = int(self.video_object.get(cv2.CAP_PROP_FRAME_COUNT))
        framerate = self.video_object.get(cv2.CAP_PROP_FPS)
        vid_width = int(self.video_object.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_height = int(self.video_object.get(cv2.CAP_PROP_FRAME_HEIGHT))
        vidWH = (vid_width, vid_height)
        vidHWC = (vid_height, vid_width, 3)
        
        info_dict = {"frame_count": total_frames,
                     "total_frames": total_frames,
                     "fps": framerate,
                     "framerate": framerate,
                     "width": vid_width,
                     "height": vid_height,
                     "vid_width": vid_width,
                     "vid_height": vid_height,
                     "vidWH": vidWH,
                     "WH": vidWH,
                     "vidHWC": vidHWC,
                     "name": self.video_name,
                     "source": self.video_source}
        
        return info_dict
    
    # .................................................................................................................

    def info(self, select = None):
        
        if select is None:
            return self.video_info
        else:
            return self.video_info[select]
        
    # .................................................................................................................
    
    # .................................................................................................................

'''
class Read_Video:
    
    def __init__(self, video_source):
        
        # Record video source and get it's type
        self.video_source = video_source
        self._figure_out_source_type()
        
        # Get naming (depends on source type)
        self._get_video_naming()
        
        # Create video object
        self.video_object = cv2.VideoCapture(video_source)
        
        # Get useful video info
        self._video_info_dict = self._get_video_info()
    
    # .................................................................................................................
    
    def source_type(self, target_type = None):
        
        if target_type is None:
            return self._source_type_dict
        else:
            return self._source_type_dict[target_type]
    
    # .................................................................................................................
    
    def _figure_out_source_type(self):
        
        # Store defaults
        is_rtsp = False
        is_webcam = False
        is_file = False
        is_unknown = True
        
        # Do simple source type checks
        is_rtsp = "rtsp://" in self.video_source.lower()
        is_webcam = type(self.video_source) is int
        
        # Check for file if we don't tag one of the easier types
        if not is_rtsp and not is_webcam:
            full_filename = os.path.basename(self.video_source)
            name_only, ext = os.path.splitext(full_filename)
            
            known_file_ext_list = [".avi", ".mp4", ".mpg", ".mpeg", ".mov", ".mkv", ".webm", "wmv"]
            is_file = ext.lower() in known_file_ext_list
            
        # Finally set unknown flag
        is_unknown = not any([is_rtsp, is_webcam, is_file])
        
        # Store results in dictionary for most compact reference
        self._source_type_dict = {"rtsp": is_rtsp,
                                  "webcam": is_webcam,
                                  "file": is_file,
                                  "unknown": is_unknown}
    
    # .................................................................................................................
    
    def _get_video_naming(self):
        
        # Allocate space for outputs
        full_filename = ""
        name_only = ""
        extension = ""
        
        if self.source_type("rtsp"):
            # Make up a name
            full_filename = "RTSP.stream"
        elif self.source_type("webcam"):
            # Make up a name
            full_filename = "Webcam.{}".format(self.video_source)
        elif self.source_type("file"):
            # Most straightforward
            full_filename = os.path.basename(self.video_source)
        else:
            # Don't know what we're dealing with, so assume it's some kind of file
            full_filename = os.path.basename(self.video_source)
        
        # Split the name and extension
        name_only, extension = os.path.splitext(full_filename)
        
        # Store results
        self.full_filename = full_filename
        self.name_only = name_only
        self.extension = extension
    
    # .................................................................................................................
    
    def video_info(self, info = None):
        
        if info is None:
            return self._video_info_dict
        else:
            return self._video_info_dict[info]
    
    # .................................................................................................................
    
    # .................................................................................................................
'''
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
        
'''
class Read_Video_Threaded:
    
    def __init__(self, video_source):
        
        pass
'''

    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
        

# ---------------------------------------------------------------------------------------------------------------------
#%% Define functions

# .....................................................................................................................
        
# .....................................................................................................................
        

# .....................................................................................................................
        

# ---------------------------------------------------------------------------------------------------------------------
#%% Demo
        
if __name__ == "__main__":
    
    pass



# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap


