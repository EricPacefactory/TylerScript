#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 15:42:22 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports


import os




# ---------------------------------------------------------------------------------------------------------------------
#%% Define Classes



# ---------------------------------------------------------------------------------------------------------------------
#%% Define Functions

# .....................................................................................................................

def cli_select_from_list(entry_list, 
                         prompt_heading = "Select entry:",
                         default_selection = None, 
                         prepend_newline = True, 
                         allow_entry_creation = False,
                         creation_prompt_text = "(or create new entry)"):
    # Set default outputs
    selected_index = None
    entry_select = None
    
    # Build the top part of the prompt message
    prompt_msg = []
    prompt_msg += [""] if prepend_newline else []
    prompt_msg += [prompt_heading]
    prompt_msg += [creation_prompt_text] if allow_entry_creation else []
    prompt_msg += [""]
    
    # Use only entry as default if the entry list contains only 1 entry
    default_selection = entry_list[0] if len(entry_list) == 1 else default_selection
    
    # Build entry list part of the prompt message
    default_index = None
    for idx, each_entry in enumerate(entry_list):
        # Build the entry list by adding numbers to each entry as well as a default indicator if present
        file_string = "  {} - {}".format(1 + idx, each_entry)
        if each_entry == default_selection:
            file_string += " >> (default)"
            default_index = (1 + idx)
        prompt_msg += [file_string]
    
    # Print out selection entries and prompt user for input
    print("\n".join(prompt_msg))
    user_response = input("Selection: ").strip()
    
    # If there is no user response (i.e. empty) assume a default entry, if present
    if not user_response:
        if default_index is None:
            raise Exception("Not a valid selection! (No default available)")
        user_response = str(default_index)
        
    # If response is a number, check if it's in the list (if so, that's our selection!)
    if user_response.isdigit(): 
        user_index_selection = int(user_response) - 1
        if user_index_selection < len(entry_list):
            selected_index = user_index_selection
            entry_select = entry_list[selected_index]
        else:
            raise IndexError("Selection ({}) is not in the entry list!".format(user_index_selection))
            
    elif allow_entry_creation:
        # User entered a non-digit, so create a new entry if possible
        selected_index = None
        entry_select = user_response 
    
    else:
        # User entered something other than a digit, and creation is disabled, so raise an error
        raise LookupError("(Creation disabled) Unrecognized entry: {}".format(user_response))
        
    return selected_index, entry_select
        
# .....................................................................................................................

def cli_file_list_select(search_path, 
                         default_selection = None,
                         extra_entries = [],
                         show_file_ext = True,
                         show_hidden_files = False,
                         prompt_heading = "Select a file:",
                         prepend_newline = True, 
                         allow_entry_creation = False,
                         creation_prompt_text = "(or create new entry)"):

    # Take out only the files from the list of items in the search folder
    file_list = sorted([each_entry for each_entry in os.listdir(search_path) 
                        if os.path.isfile(os.path.join(search_path, each_entry))])
    
    # Remove hidden files if desired
    if not show_hidden_files:
        file_list = [each_file for each_file in file_list if each_file[0] != "."]
    
    # Add any extra entries (to the bottom of the list)
    file_list += extra_entries
    
    # Create full file paths for later use
    file_path_list = [os.path.join(search_path, each_file) for each_file in file_list]
    
    # Remove file extensions if needed
    if not show_file_ext:
        file_list = [os.path.splitext(each_file)[0] for each_file in file_list]
    
    # Have the user select from the file list
    selected_index, entry_select = cli_select_from_list(file_list,
                                                        prompt_heading,
                                                        default_selection,
                                                        prepend_newline, allow_entry_creation,
                                                        creation_prompt_text)
    
    # Check if a new entry was created and build the outputs depending on the result
    created_entry = (selected_index is None)    
    if created_entry:
        full_path = os.path.join(search_path, entry_select)
        file_name = entry_select
    else:
        full_path = file_path_list[selected_index]
        file_name = file_list[selected_index]
        
    return full_path, file_name, created_entry

# .....................................................................................................................

def cli_folder_list_select(search_path, 
                           default_selection = None,
                           extra_entries = [],
                           show_hidden_folders = False,
                           prompt_heading = "Select a folder:",
                           prepend_newline = True, 
                           allow_entry_creation = False,
                           creation_prompt_text = "(or create new entry)"):

    # Take out only the folders from the list of items in the search folder
    folder_list = sorted([each_entry for each_entry in os.listdir(search_path) 
                          if os.path.isdir(os.path.join(search_path, each_entry))])
    
    # Remove hidden folders if desired
    if not show_hidden_folders:
        folder_list = [each_folder for each_folder in folder_list if each_folder[0] != "."]
    
    # Add any extra entries (to the bottom of the list)
    folder_list += extra_entries
    
    # Create full folder paths for later use
    folder_path_list = [os.path.join(search_path, each_file) for each_file in folder_list]
    
    # Have the user select from the folder list
    selected_index, entry_select = cli_select_from_list(folder_list,
                                                        prompt_heading,
                                                        default_selection,
                                                        prepend_newline, allow_entry_creation,
                                                        creation_prompt_text)
    
    # Check if a new entry was created and build the outputs depending on the result
    created_entry = (selected_index is None)    
    if created_entry:
        full_path = os.path.join(search_path, entry_select)
        folder_name = entry_select
    else:
        full_path = folder_path_list[selected_index]
        folder_name = folder_list[selected_index]
        
    return full_path, folder_name, created_entry
        
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

def cli_confirm(confirm_text, 
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


# ---------------------------------------------------------------------------------------------------------------------
#%% Demo
    
if __name__ == "__main__":
    
    desktop_path = os.path.expanduser("~/Desktop")
    a,b,c = cli_file_list_select(desktop_path)    
    x,y,z = cli_folder_list_select(desktop_path)
