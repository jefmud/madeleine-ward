# maddy3

# GUIZero is a simplified wrapper on Tkinter
from guizero import (App, Text, Picture,
                     MenuBar, TextBox, Window,
                     PushButton, warn, info, askstring,
                     Drawing)
import os

from observations import Observations, Observation, Image

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768

# note we can import Tkinter widget
from tkinter import filedialog, messagebox, simpledialog

# set a default folder and files
folder_selected = './jeff_empty_model/zebra'
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
    GLOB_KEYCODE = keycode
    if DEBUG: print('keypressed:', keycode, '=', event_data.key)
    if keycode == 39:
        # RIGHT arrow
        observations.save()
        file_pointer += 1
        file_pointer = show_file(file_pointer)
    if keycode == 37:
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
        annotations_filename = os.path.join(folder_selected, 'annotations.csv')
        # load observations if these exist
        observations = Observations(annotations_filename)
    else:
        info("Information", "You cancelled folder selection")
        
    
def file_function():
    """file function stub"""
    if DEBUG: print("File function selected.")
    messagebox.showinfo("File Function", "File function selected!")

def canvas_right_click(event_data):
    """canvas_right_click event handler
    action - the canvas right-click event will reset NEAREST
    observation mark
    """
    global canvas, observations, current_image
    # click data
    x = event_data._tk_event.x
    y = event_data._tk_event.y
    
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
    
    
    
    
def canvas_left_click(event_data):
    """canvas_left_click event handler
    action - the left click imposes a red line in the canvas which should
    scale up to the actual resolution.
    """
    global canvas, observations
    size = 10
    x = event_data._tk_event.x
    y = event_data._tk_event.y
    
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
        if DEBUG: print("displaying {}".format(pathname))
        
        # find existing observations
        image_observation_indices = observations.find_by_filename(fname)
        # if there is a non empty list,
        if image_observation_indices:
            # first index
            first = image_observation_indices[0]
            # show the current image
            current_image = observations.items[first].image
            current_image.show(canvas)
            # step through the individual observations and display the marker
            for index in image_observation_indices:
                current_observation = observations.items[index]
                current_observation.show_marker(canvas)
        else:
            # no observations yet, instantiate a new image and show on canvas
            current_image = Image(fname, folder_selected)
            current_image.show(canvas)
        
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
            warn("Error", "This folder contains no image files")
        else:
            file_pointer = 0
            # get observations!
            observations = Observations(annotations_filename, folder_selected)
            show_file(file_pointer)
            
    except Exception as e:
        warn("Exception thrown", "Invalid folder.  Please select valid folder.")
    

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
                  toplevel=["File", "Mark Images"],
                  options=[
                      [ ["Pick Directory", pick_directory] ],
                      [ ["Mark Images", mark_function]]
                  ])

# hook the arrow keys (for now, might want to change this to local hook if permitted)
app.when_key_pressed = keypress_hook

app.display()