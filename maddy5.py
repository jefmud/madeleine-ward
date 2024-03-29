# maddy5
# Version 5, Beta
# Madeleine Ward's species marker program

import tkinter
# GUIZero is a simplified wrapper on Tkinter
from guizero import (App, Text, Picture,
                     MenuBar, TextBox, Window,
                     PushButton, warn, info, askstring,
                     Drawing)

import os

from observations import Observations, Observation, Image

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768
RIGHT_ARROW = 38
RIGHT_ARROW_OSX = 8189699
LEFT_ARROW = 39
LEFT_ARROW_OSX = 8124162

# note we can import Tkinter widget
from tkinter import filedialog, messagebox, simpledialog

# set a default folder and files
folder_selected = '.'
files = []
file_pointer = 0
DEBUG = False
    
# ANNOTATIONS FOR THE IMAGE DATA are stored in a local CSV file
annotations_filename = 'annotations.csv'
observations = Observations(annotations_filename, folder_selected)
current_observation_indices = []
print("Loaded {} observations".format(len(observations.items)))
current_image = None
    
def keypress_hook(event_data):
    """if a key is pressed in the app, do corresponding function"""
    # it is not state aware yet, I will want to change that later.
    global file_pointer
    keycode = event_data._tk_event.keycode
    if DEBUG: print('keypressed:', keycode, '=', event_data.key)
    if keycode == RIGHT_ARROW or keycode == RIGHT_ARROW_OSX:
        # RIGHT arrow
        observations.save()
        file_pointer += 1
        file_pointer = show_file(file_pointer)
    if keycode == LEFT_ARROW or keycode == LEFT_ARROW_OSX:
        # LEFT arrow
        observations.save()
        file_pointer -= 1
        file_pointer = show_file(file_pointer)


def pick_directory():
    """allows a user to pick the directory of images on which to work"""
    global folder_selected, annotations_filename, observations
    if DEBUG: print("Pick a Directory of Images")
    user_selected = filedialog.askdirectory()
    if user_selected:
        folder_selected = user_selected
        messagebox.showinfo("Information","You picked: {}".format(folder_selected))
        # load observations if these exist
        observations = Observations(filename=annotations_filename, path=folder_selected)
    else:
        info("Information", "You cancelled folder selection")
        
    
def file_function():
    """file function stub"""
    if DEBUG: print("File function selected.")
    messagebox.showinfo("File Function", "File function selected!")


def attempt_remove_mark(x,y):
    """attempt to remove a mark at x,y if it exists
    return True if an image was found
    return False if nothing was nearby
    """
    global canvas, observations, current_image
    found_index = observations.find_by_filename_location(current_image.fname, x, y)
    if found_index >= 0:
        # found the observation!
        current_observation = observations.items[found_index]
        species = askstring("Observation",
                            "Click OK to KEEP marker/species, CANCEL to delete",
                            initialvalue=current_observation.species)
        if (species is None) or (species == ''):
            # user wants to DELETE the observation
            observations.remove_at_index(found_index)
            current_image.show(canvas)
            observations.show_markers_by_filename(canvas, current_image.fname)
        return True
    else:
        return False
    
    
def canvas_right_click(event_data):
    """canvas_right_click event handler
action - the canvas right-click event will reset NEAREST
observation mark
"""
    # click data
    x = event_data._tk_event.x
    y = event_data._tk_event.y
    attempt_remove_mark(x,y)   
    
def canvas_left_click(event_data):
    """canvas_left_click event handler
    action - the left click imposes a red line in the canvas which should
    scale up to the actual resolution.
    """
    global canvas, observations
    size = 10
    x = event_data._tk_event.x
    y = event_data._tk_event.y

    # attempt to remove the mark is NEAR to an existing mark
    if attempt_remove_mark(x,y):
        # just exit if this returns True
        return None

    # make a temporary mark
    mark_id = canvas.oval(x-size,y,x+size,y+size,color="red")
    canvas.show()
    
    # ask user what species they saw
    species = askstring("Species", "Species name")
    
    if (species is None) or (species == ''):
        # they hit cancel or blank species
        canvas.delete(mark_id)
    else:
        # record as an observation!
        observation = Observation(current_image, species, x, y)
        observations.append(observation)
    
def show_file(file_pointer):
    """show_file(file_pointer) shows a file in the global file list"""
    global canvas, current_image
    
    # in case they forgot to select directory
    if len(files) == 0:
        warn("Error", "No files selected")
        return 0
    
    if file_pointer >= len(files):
        file_pointer = 0
    if file_pointer < 0:
        file_pointer = len(files)-1
        
    fname = files[file_pointer]
    pathname = os.path.join(folder_selected, fname)
    try:
        # try to show a picture and associated observations
        if DEBUG:
            print("displaying {}".format(pathname))
        
        current_image = observations.show_image_observations_by_filename(canvas, fname)
        
    except Exception as e:
        # in case of an error, flag it and show user
        msg = "Exception show_image(): {} (on attempt to render {})".format(str(e), pathname)
        warn("Exception", msg)
        
    # return the file_pointer
    return file_pointer

def get_image_filenames(imagepath):
    """get_image_filenames(imagepath) - return a list of image filenames"""
    image_files = []
    valid_extensions = ['jpg','jpeg','png']
    for fn in os.listdir(imagepath):
        if fn[0]=='.':
            # skip Mac thumbs
            continue
        parts = fn.split('.')
        for ext in valid_extensions:
            if parts[-1].lower() == ext:
                image_files.append(fn)
    return image_files
    
def mark_function():
    """initates marking operation"""
    global files
    global filename
    global file_pointer
    global observations
    if DEBUG: print("Mark Images")
    try: 
        # get files from current directory
        files = get_image_filenames(folder_selected)
                
        if len(files) == 0:
            warn("Error", "This folder contains no image files.\nPick another folder.")
        else:
            file_pointer = 0
            # get observations!
            observations = Observations(annotations_filename, folder_selected)
            show_file(file_pointer)
            
    except Exception as e:
        warn("Exception thrown", "Invalid folder.  Please select valid folder.")

def show_help():
    msg = """1. To select a Directory choose File->Pick Directory menu.

2. To begin marking up images choose Mark Images menu

RIGHT KEYBOARD ARROW moves to next picture in the directory.

LEFT KEYBOARD ARROW moves back one picture in the directory.

LEFT MOUSE CLICK allows marking the species location.
LEFT MOUSE CLICK on existing mark allows you to EDIT the mark.
"""
    info("Welcome", msg)

# declare our main app    
app = App(
    title="Madeleine Ward Marker Prototype",
    width=IMAGE_WIDTH,
    height=IMAGE_HEIGHT,
)

# CANVAS contains an image with lines that indicate species present
canvas = Drawing(app, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)

# hook the events to the canvas object
canvas.when_left_button_pressed = canvas_left_click
canvas.when_right_button_pressed = canvas_right_click

# define the menu bar
menubar = MenuBar(app,
                  toplevel=["File", "Mark Images","Help"],
                  options=[
                      [ ["Pick Directory", pick_directory] ],
                      [ ["Mark Images", mark_function]],
                      [ ["Help", show_help]]
                  ])

# hook the arrow keys (for now, might want to change this to local hook if permitted)
app.when_key_pressed = keypress_hook
show_help()

app.display()
