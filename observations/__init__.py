import math
import os
import exifread

# special pure-Python CSV wrapper written by jeff for
# annotation quasi-data structure
import csvdata

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768

class Image:
    def __init__(self, fname, path):
        self.fname = fname
        self.path = path
        self.pathname = os.path.join(path, fname)
        self.datetime = ''
        self.width = -1
        self.height = -1
        self.camera = ''
        self.getEXIF()
    
    def getEXIF(self):
        # EXIF reading
        f = open(self.pathname, 'rb') 
        tags = exifread.process_file(f)
        self.datetime = tags.get('EXIF DateTimeOriginal')
        self.width = int(str(tags.get('EXIF ExifImageWidth','0')))
        self.height = int(str(tags.get('EXIF ExifImageLength','0')))
        # fix this for Madeleine's camera IDs
        self.camera = str(tags.get('Image Software'))
        
    def show(self, canvas):
        canvas.clear()
        canvas.image(0, 0, self.pathname, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        canvas.show()
        
class Observation:
    """Observation is a class object that represents a single observation
    The __init__ method allows instatiation from image, species, x, y
    or a "serial" that comes from a CSV file.
    
    This method allows maximum flexibility to redefine the Observation Object below
    """
    def __init__(self, image=None, species=None, x=None, y=None, serial=None):
        """__init__(self, image=<Image obj>, species=<string>, x=<numeric>, y=<numeric>"""
        if serial:
            # initialize from a serial object
            self.image = Image(serial['fname'], serial['path'])
            self.species = serial['species']
            # coerce to int
            self.x = int(serial['x'])
            self.y = int(serial['y'])
        else:
            # initialize from parameters
            if (image is None) or (species is None) or (x is None) or (y is None):
                # don't let user get away with lazy instantiation
                raise ValueError("Observation requires ALL parameters e.g. image, species, x, y (or serial object)")
            if not(isinstance(image, Image)):
                raise ValueError("Observation intantiation REQUIRES image be of Image type")
            
            self.image = image
            self.species = species
            # corece to int
            self.x = int(x)
            self.y = int(y)
        
    def serialize(self):
        """serialize Observation"""
        serial = vars(self).copy()
        del serial['image']
        image_serial = vars(self.image)
        for k,v in image_serial.items():
            serial[k] = v
        return serial

    def distance(self, x, y):
        """distance(self, x, y) - returns distance of current observation to (x,y)"""
        return math.sqrt((self.x-x)**2 + (self.y-y)**2)
        
    def show_marker(self, canvas):
        """show_marker(self, canvas) the current marker on the specified canvas"""
        size = 10
        mark_id = canvas.oval(self.x-size,self.y,
                              self.x+size,self.y+size,
                              color="red")
        canvas.show()
        
        
class Observations:
    """Observations is a class to encapsulate a list of Observation datapoints for
    a folder
    
    it is expected that...
    filename = "annotations.csv" (default?)
    path = selected folder where images reside
    """
    def __init__(self, filename, path):
        """__init__(self, filename, path) initializes observations object and loads if it can"""
        self.filename = filename
        self.path = path
        self.pathname = os.path.join(path, filename)
        self.items = []
        self.load(self.pathname)
        if self.items is None:
            self.items = []
        
    def append(self, observation):
        """append(self, observation) - appends a new observation onto observation list"""
        self.items.append(observation)
        
    def remove_at_index(self, index):
        """remove_at_index(self, index) - purges an observation
        BE CAREFUL - since once the item at the index is removed any "remembered"
        indices might be wrong!!
        """
        del self.items[index]
        
    def load(self, pathname=None):
        """load(self, pathname=None) - loads observation objects from a CSV file
        Note, pathname is COMPLETE pathname not just a filename in the local directory
        (following convention consistency)
        """
        if pathname is None:
            pathname = self.pathname
            
        items = csvdata.read_csv(pathname)
        for item in items:
            # Go through all observations and serialize into self (items)
            # (FIX THIS) a "brittle" way to do this, because the definition of observation
            # should be handled at the Observation object level
            #image = Image(item['fname'], item['path'])
            #observation = Observation(image, item['species'], int(item['x']), int(item['y']))
            # make observation from serialized object
            observation = Observation(serial=item)
            self.append(observation)
        return self.items
    
    def serialize(self):
        """serialize(self) - return serialized version of observations
        this equates to the idea of rows of dictionaries (each observation is a dictionary)
        """
        # serialize into rows of dictionaries
        serials = []
        for item in self.items:
            serial = item.serialize()
            serials.append(serial)
        return serials
        
    def save(self, pathname=None):
        """save(self, pathname=None) - save the serialized data to a CSV file
        a complete pathname can override the objects pathname
        """
        if pathname is None:
            pathname = self.pathname
        serials = self.serialize()
        csvdata.write_csv(serials, pathname)
        
    def find_by_filename(self, filename):
        """find_by_filename(self, filename) - find all observation indices
        which match the filename
        if NONE are found, return an empty list
        """
        indices = []
        for index, item in enumerate(self.items):
            if item.image.fname == filename:
                indices.append(index)
        return indices
    
    def find_by_filename_location(self, filename, x, y, pixel_tolerance=15):
        """find_by_filename_location(self, filename, x, y, pixel_tolerance=15)
        returns indices of first observation to match the filename and x,y location within
        the pixel (distance) tolerance.
        If NONE are found, returns a -1
        (since this returns an integer, the -1 maintains consistency of type)
        """
        found_indices = self.find_by_filename(filename)
        for index in found_indices:
            current_observation = self.items[index]
            this_distance = current_observation.distance(x,y)
            if this_distance <= pixel_tolerance:
                return index
        return -1
            
            
    
    def show_markers_by_filename(self, canvas, filename):
        """show_markers_by_filename(self, canvas, filename)
        this streamlines the process of displaying current markers associated with a filename
        return True if it succeeds showing markers, False if nothing to show
        """
        indices = self.find_by_filename(filename)
        if indices:
            first = indices[0]
            # show the image
            self.items[first].image.show(canvas)
            # impose markers from observations
            for idx in indices:
                self.items[idx].show_marker(canvas)
            return True
        else:
            return False
        
    def show_image_observations_by_filename(self, canvas, filename):
        """show_image_observations_by_filename(self, canvas, filename)
        this streamlines the process of displaying the image and current markers associated with a filename
        returns current_image displayed.
        """
        indices = self.find_by_filename(filename)
        if indices:
            # show the current image
            current_image = self.items[indices[0]].image
            current_image.show(canvas)
            self.show_markers_by_filename(canvas, filename)
        else:
            # no observations on image!
            current_image = Image(filename, self.path)
            current_image.show(canvas)
        return current_image
                
    
if __name__ == '__main__':
    print("support module only")