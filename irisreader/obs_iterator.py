#!/usr/bin/env python

# import libraries
import os, re
from irisreader import observation

class obs_iterator:
    """This class implements a generator class to iterate over a set of 
    observations that is given as a path. In case of a reading error, the
    iterator automatically jumps to the next valid observation.
    As this iterator is not a regular list, it can only be iterated once.
    
    Parameters
    ----------
    
    path : string
        Path to the directory holding all the observations. This function assumes
        IRIS data structure where observations are stored in directories with the
        format <DATE>_<TIME>_<OBSID>.
    keep_null : boolean
        Controls whether images that are NULL (-200) everywhere are removed from the data cube. keep_null=True keeps NULL images and keep_null=False removes them.
    read_42 : boolean
        Whether to read observations with an OBSID starting with 42 (mostly for tests and maintenance).
    
    Attributes
    ----------
    
    path : string
        Path that has been passed as a parameter.
    directories : string
        List of valid IRIS data directories that have been found during the traversal.
    """
    
    # constructor
    def __init__( self, path="", keep_null=False, read_42=False ):
        
        # set variables
        self._keep_null = keep_null
        self.path = path
        self.directories = []
        self._n = 0
        self._i = 0
        self._current_obs = None
        
        # get a list of directories containing a date_time_obsid string
        if path != "":
            if os.path.exists( path ):
                print( "Reading directories [this can take a while].. " ),
                for root, dirs, files in os.walk( path ):
                    for dir in dirs:
                        if re.search('[\d]{6}_[\d]{6}_[\d]{10}', dir):
                            if read_42 or not '_42' in dir: # exclude OBSIDs starting with 42
                                self.directories.append( os.path.join(root, dir) ) 
                                
            else:
                raise ValueError( "Path " + path + " does not exist!" )
                
            self.directories.sort()

              
        # set number of directories to iterate on
        self._n = len( self.directories )
        print( "done [" + str( self._n ) + " directories]" )

    # return length to len function
    def __len__(self):
        return self._n
    
    # return iteration on demand
    def __iter__(self):
        return self

    # return next observation
    def next(self):
        try:
            self._i += 1
            try:
                # close previous observation
                if not self._current_obs is None:
                    self._current_obs.close() # TODO: why does this not work??
                    
                # open next observation
                self._current_obs = observation( self.directories[self._i-1], keep_null=self._keep_null )
                return self._current_obs
            
            # Continue with the next observation if there was an error in the current one
            except Exception as e:
                print( '\033[91m' + "Error reading directory " + self.directories[self._i-1] + ": " + str(e) + " Returning the next valid observation." + '\033[0m' )
                return self.next()
        
        # Stop iteration if no observations are left
        except IndexError:
            self._i = 0
            raise StopIteration
            
    # add support for python 3
    __next__ = next


