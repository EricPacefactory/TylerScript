#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 11:46:14 2018

@author: eo
"""

import os


# ---------------------------------------------------------------------------------------------------------------------
#%% Define classes


# ---------------------------------------------------------------------------------------------------------------------
#%% Define pathing functions

# Function that takes in a filename and checks if the file path exists (and if not, creates it)
def checkSavePath(fullFilePath, enablePrompt=True, autoOverwrite=True):
    
    # Check for file overwriting
    if os.path.exists(fullFilePath):        
        
        if enablePrompt:
            # Warn user if they are about to overwrite a file
            print("")
            print("File already exists!", fullFilePath)
            overwritePrompt = (input("Overwrite (y or n)? ").lower().strip() == 'y')
            return overwritePrompt
        else:
            # No prompt, so just overwrite the file!
            return autoOverwrite
        
    # Create the desired directory if it doesn't already exist
    isFolder = os.path.splitext(fullFilePath)[1] == ""
    savePath = fullFilePath if isFolder else os.path.dirname(fullFilePath)
    if not os.path.exists(savePath):
        os.makedirs(savePath)
        
    return True

# .....................................................................................................................

# Function for checking the existance of a file/directory
def checkLoadPath(fullPath, msg=None, printConfirmation=False, printMissing=True, raiseError=True):
    
    # Check if the path exists
    validPath = os.path.exists(fullPath)
    
    # Get a name to report back if one isn't given
    if msg is None:
        msg = os.path.basename(fullPath)
    
    # Print out a confirmation (if desired)
    if validPath and printConfirmation:
        print("")
        print(msg, "found!")
    
    # Print out a message about not finding the file (if desired)
    if not validPath and printMissing:
        print("")
        print(msg, "not found! Searched:")
        print(fullPath)
    
    # Raise an error (if desired)
    if not validPath and raiseError:
        print("")
        raise FileNotFoundError
    
    return validPath

# .....................................................................................................................
    
# Function for extracting handy file pathing info
def getFilePathingInfo(source):
    sourceFile = os.path.basename(source)
    fileName = os.path.splitext(sourceFile)[0]
    dirName = os.path.basename(os.path.dirname(source))
    return sourceFile, fileName, dirName

# .....................................................................................................................

# Function for generating a list of all target files in a folder (searched recursively)
def findTargetFiles(topWorkingDirectory, targetFileExtension, targetName=""):

    # First check that the top directory exists
    if not os.path.exists(topWorkingDirectory):
        print("")
        print("Top directory doesn't exist! Searched:")
        print(topWorkingDirectory)
        print("")
        raise NotADirectoryError

    # Get a list of every log file within the top directory
    targetFileList = []
    for parentDir, subDirs, subFiles in os.walk(topWorkingDirectory, topdown=True):

        # Debugging print outs
        # print("")
        # print("Working in", parentDir)

        # Search for target files in each parent directory
        for eachFileName in subFiles:

            # Check if the given file has the target extension type
            if eachFileName.endswith(targetFileExtension):

                # Finally, check if the file contains the target name
                if targetName in eachFileName:
                    filePath = os.path.join(parentDir, eachFileName)
                    targetFileList.append(filePath)

    # Quick check that some log files were found
    if len(targetFileList) < 1:
        print("")
        print("Target files (." + targetFileExtension + ") not found! Cancelling...")
        print("")
        raise FileNotFoundError
        
    # File list contains full path of every file with the target extension
    return targetFileList

# .....................................................................................................................

def build_folder_structure_from_dictionary(base_path, dictionary, make_folders = False):
    # Recursive function for creating file paths from a dictionary
    
    # If the dictionary is empty/not a dictionary, then we're done
    if not dictionary:
        return []
    
    # Allocate space for outputting generated paths
    path_list = []
    
    # Recursively build paths by diving through dictionary entries
    for each_key, each_value in dictionary.items():
        
        # Add the next dictionary key to the existing path
        create_path = os.path.join(base_path, each_key)
        path_list.append(create_path)
        
        new_path_list = build_folder_structure_from_dictionary(create_path, each_value)
        path_list += new_path_list
        
    # Create the folders, if needed
    if make_folders:
        for each_path in path_list:
            if not os.path.exists(each_path):
                os.makedirs(each_path)
        
    return path_list

# .....................................................................................................................

# Function for listing folders in a given folder
def get_folder_list(search_folder_path, 
                    show_hidden_folders = False,
                    create_missing_folder = False, 
                    return_full_path = False):
    
    # Make sure the search folder exists before trying to list it's contents!
    if not os.path.exists(search_folder_path):
        if create_missing_folder:
            os.makedirs(search_folder_path)
        return []
    
    # Take out only the files from the list of items in the search folder
    folder_list = sorted([each_entry for each_entry in os.listdir(search_folder_path) 
                          if os.path.isdir(os.path.join(search_folder_path, each_entry))])
    
    # Hide folders beginning with dots (i.e. hidden)
    if not show_hidden_folders:
        folder_list = [each_folder for each_folder in folder_list if each_folder[0] != "."]
    
    # Prepend the search folder path if desired
    if return_full_path:
        folder_list = [os.path.join(search_folder_path, each_folder) for each_folder in folder_list]

    return folder_list

# .....................................................................................................................
    
# Function for listing files in a given folder
def get_file_list(search_folder_path, 
                  show_hidden_files = False, 
                  create_missing_folder = False, 
                  return_full_path = False):
    
    # Make sure the search folder exists before trying to list it's contents!
    if not os.path.exists(search_folder_path):
        if create_missing_folder:
            os.makedirs(search_folder_path)
        return []
    
    # Take out only the files from the list of items in the search folder
    file_list = sorted([each_entry for each_entry in os.listdir(search_folder_path) 
                        if os.path.isfile(os.path.join(search_folder_path, each_entry))])
    
    # Hide files beginning with dots (i.e. hidden)
    if not show_hidden_files:
        file_list = [each_file for each_file in file_list if each_file[0] != "."]
    
    # Prepend the search folder path if desired
    if return_full_path:
        file_list = [os.path.join(search_folder_path, each_file) for each_file in file_list]
    
    return file_list

# .....................................................................................................................

# ---------------------------------------------------------------------------------------------------------------------
#%% GUI Functions

def guiLoad(searchDir=os.path.expanduser("~/Desktop"), windowTitle="Select a file", fileTypes=None, errorOut=True):
    
    import tkinter
    from tkinter import filedialog
    
    # Set general file types if none are specified
    if fileTypes is None:
        fileTypes = [["all", "*"]]
        
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Ask user to select file
    fileInSource = filedialog.askopenfilename(initialdir=searchDir, title=windowTitle, filetypes=fileTypes)
    
    # Get rid of UI elements
    root.destroy()    
    
    if len(fileInSource) < 1:
        
        # Hard crash if needed
        if errorOut:
            print("")
            print("Load cancelled!")
            print("")
            raise IOError
        else:
            return None
    
    return fileInSource

# .....................................................................................................................
    

def guiLoadMany(searchDir=os.path.expanduser("~/Desktop"), windowTitle="Select file(s)", fileTypes=None, errorOut=True):
    
    import tkinter
    from tkinter import filedialog
    
    # Set general file types if none are specified
    if fileTypes is None:
        fileTypes = [["all", "*"]]
        
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Ask user to select file
    fileList = filedialog.askopenfilenames(initialdir=searchDir, title=windowTitle, filetypes=fileTypes)
    
    # Get rid of UI elements
    root.destroy()    
    
    if len(fileList) < 1:
        
        # Hard crash if needed
        if errorOut:
            print("")
            print("Load cancelled!")
            print("")
            raise IOError
        else:
            return None
    
    return fileList

# .....................................................................................................................

def guiSave(searchDir=os.path.expanduser("~/Desktop"), windowTitle="Save file", fileTypes=None):
    
    import tkinter
    from tkinter import filedialog
    
    # Set general file types if none are specified
    if fileTypes is None:
        fileTypes = [["files", "*"]]
        
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    fileOutSource = filedialog.asksaveasfilename(initialdir=searchDir, title=windowTitle, filetypes=fileTypes)
    
    # Get rid of UI elements
    root.destroy()    
    
    if len(fileOutSource) < 1:
        print("")
        print("Save cancelled!")
        return None
    
    return fileOutSource

# .....................................................................................................................

def guiFolderSelect(searchDir=os.path.expanduser("~/Desktop"), windowTitle="Select a folder", errorOut=True):
    
    import tkinter
    from tkinter import filedialog
        
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Ask user to select a folder
    folderInSource = filedialog.askdirectory(initialdir=searchDir, title=windowTitle)
    
    # Get rid of UI elements
    root.destroy()    
    
    if len(folderInSource) < 1:
        print("")
        print("Folder select cancelled!")
        
        # Hard crash if needed
        if errorOut:
            print("")
            raise IOError
        else:
            return None
    
    return folderInSource

# .....................................................................................................................

def guiConfirm(confirmText, windowTitle="Confirmation"):
    
    import tkinter
    from tkinter import messagebox
    
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Get user response
    userResponse = messagebox.askyesno(windowTitle, confirmText)
    
    # Get rid of UI elements
    root.destroy()    
    
    return userResponse

# .....................................................................................................................
    
def guiDialogEntry(dialogText, windowTitle="Entry", retType=str):
    
    import tkinter
    from tkinter import simpledialog
    
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Get user response
    userResponse = simpledialog.askstring(windowTitle, dialogText)
    
    # Get rid of UI elements
    root.destroy() 
    
    # Handle cancel case
    if userResponse is None:
        return None
    
    # Handle empty input
    if userResponse.strip() == "":
        return None
    
    return retType(userResponse)

# .....................................................................................................................


# ---------------------------------------------------------------------------------------------------------------------
#%% CLI Functions
    
# .....................................................................................................................

def cliConfirm(confirm_text, 
               yes_is_default = True, 
               append_default_indicator = True, 
               response_on_newline = False,
               prepend_newline = True):
    
    # Set up convenient prompt add-ons
    prefix_1 = "\n" if prepend_newline else ""
    default_indicator = " ([y]/n) " if yes_is_default else " (y/[n]) "
    suffix_1 = default_indicator if append_default_indicator else ""
    suffix_2 = "\n" if response_on_newline else ""
    
    # Build full display message
    full_message = "".join([prefix_1, confirm_text, suffix_1, suffix_2])
    
    # Update confirmation based on user input
    user_response = input(full_message).strip().lower()
    confirm_response = yes_is_default
    if yes_is_default:
        if user_response == "n":
            confirm_response = False
    else:
        if user_response == "y":
            confirm_response = True
    
    return confirm_response

# .....................................................................................................................
     
def cli_prompt_with_defaults(prompt_message, 
                             default_value = None, 
                             return_type = None,
                             response_on_newline = False,
                             prepend_newline = True,
                             align_default_with_input = True):
    
    # Set up helper add-ons
    prefix_1 = "\n" if prepend_newline else ""
    default_msg = "(default: {})\n".format(default_value) if default_value is not None else ""
    suffix_1 = "\n" if response_on_newline else ""
    
    # Modify default text to line up with user input (if desired)
    if align_default_with_input:
        
        # Don't bother with alignment if a default value isn't even given or the user enters on a newline
        if (default_value is not None) and (not response_on_newline):
            shift_length = len(prompt_message) - len("(default: ")
            default_shift = max(0, shift_length)
            prompt_shift = max(0, -shift_length)
            default_msg = " " * default_shift + default_msg
            prompt_message = " " * prompt_shift + prompt_message
    
    # Build full message string
    full_message = "".join([prefix_1, default_msg, prompt_message, suffix_1])

    # Get user input or use default if nothing is provided
    user_response = input(full_message).strip()
    if user_response == "":
        user_response = default_value
        
    # Convert response in function for convenience (if desired!)
    if return_type is not None:
        user_response = return_type(user_response)
        
    return user_response
    
# .....................................................................................................................
    
# .....................................................................................................................

# ---------------------------------------------------------------------------------------------------------------------
#%% Define history/logging functions

def saveHistoryFile(fileSource, historyDict, asPickle=False, verbose=False):
    
    # Load in the existing history file if it exists, so we can merge in new data
    prevHistory = {}
    if os.path.exists(fileSource):
        prevHistory = loadHistoryFile(fileSource, asPickle=asPickle)
        
    # Switch between different saved file types
    if asPickle:
        import pickle as filewriter
        writeType = 'wb'
    else:
        import json as filewriter
        writeType = 'w'
    
    # Create directory to store history file if it doesn't already exist
    sourceDir = os.path.dirname(fileSource)
    if not os.path.exists(sourceDir):
        os.makedirs(sourceDir)
    
    # Merge the old history with the new data and save
    mergedDict = {**prevHistory, **historyDict}
    with open(fileSource, writeType) as outFile:
        filewriter.dump(mergedDict, outFile)
        
    # Some feedback, if necessary
    if verbose:
        print("")
        print("Saved history file:")
        print(fileSource)

# .....................................................................................................................

def loadHistoryFile(fileSource, searchFor=None, asPickle=False, verbose=False):
    
    # Check if a file even exists before trying to load it
    if not os.path.exists(fileSource):
        if verbose:
            print("")
            print("No history file found. Searched:")
            print(fileSource)
        return None
    
    # Switch between different saved file types
    if asPickle:
        import pickle as filereader
        readType = 'rb'
    else:
        import json as filereader
        readType = 'r'
    
    # Open the file
    with open(fileSource, readType) as inFile:
        fileData = filereader.load(inFile)
    
    # Search for a target dictionary key, if one is provided
    if searchFor is not None:
        
        keyInDict = (searchFor in fileData)
        
        # Some feedback if the key isn't found
        if not keyInDict:
            if verbose:
                print("")
                print("Key", searchFor, "not found in history file!")
            return None
        
        # Ask user if they want to load in a history file based on finding a target dictionary key
        print("")
        print("Found previously loaded history file with key:", searchFor)
        print(fileData[searchFor])
        userResponse = input("Re-use data? (y/n):\n") 
        if userResponse.lower().strip() == 'n':
            return None
        
    return fileData

# .....................................................................................................................
    
# .....................................................................................................................


# ---------------------------------------------------------------------------------------------------------------------
#%% Define RTSP functions
    
def rtspString(ip, username="", password="", port=554, command=""):
    
    rtspSource = "".join(["rtsp://", username, ":", password, "@", ip, ":", str(port), "/", command])
    
    splitIP = ip.split(".")
    padIP = [eachNumber.zfill(3) for eachNumber in splitIP]
    blockIP = "".join(padIP)
    
    return rtspSource, blockIP

# .....................................................................................................................
    
def rtspFromCommandLine(errorOut=True):
        
    # Ask user for RTSP settings
    print("")
    print("****************** GET RTSP ******************")
    ipAddr = input("Enter IP address:\n")
    
    # If ip address is skipped, raise an error or exit function
    if ipAddr.strip() == "":        
        if errorOut:
            print("Bad IP!")
            print("")
            print("**********************************************")
            print("")
            raise ValueError
        else:
            return None
    
    def defaultInput(inputString, defaultValue):
        inputValue = input(inputString).strip()
        if inputValue == "":
            return defaultValue
        return inputValue

    # Get rtsp settings from user
    rtspUser = defaultInput("Enter username \t(default None):\n", "")
    rtspPass = defaultInput("Enter password \t(default None):\n", "")
    rtspPort = defaultInput("Enter port \t\t(default 554):\n", "554")
    rtspComm = defaultInput("Enter command \t(default None):\n", "")
        
    # Finish off blocking gfx
    print("")
    print("**********************************************")
    
    # Build dictionary for convenient output
    outRecord = {"username": rtspUser, 
                 "password": rtspPass,
                 "ip": ipAddr,
                 "port": rtspPort,
                 "command": rtspComm}
        
    return outRecord

# .....................................................................................................................

