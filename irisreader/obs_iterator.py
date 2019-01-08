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
    read_v4 : boolean
        Whether to read observations with an OBSID starting with 4 (obs table generation v4, mostly for tests and maintenance, see ITN 31).
    display_errors : boolean
        Whether to show errors that occured in opening individual observations or just to ignore them
    error_log: str
        Path to logfile for errors (will be appended, clear the file if necessary)
    
    Attributes
    ----------
    
    path : string
        Path that has been passed as a parameter.
    directories : string
        List of valid IRIS data directories that have been found during the traversal.
    """
    
    # constructor
    def __init__( self, path="", keep_null=False, read_v4=False, display_errors=True, error_log=None ):
        
        # set variables
        self._keep_null = keep_null
        self.path = path
        self.directories = []
        self._n = 0
        self._i = 0
        self._current_obs = None
        self._display_errors = display_errors
        self._error_log = error_log
        
        # check whether path to logfile is writeable
        if error_log is not None:
            f = open( error_log, 'a+' ) 
            f.close()
        
        # get a list of directories containing a date_time_obsid string
        if path != "":
            if os.path.exists( path ):
                print( "Reading directories [this can take a while].. " ),
                for root, dirs, files in os.walk( path ):
                    for dir in dirs:
                        if re.search('[\d]{6}_[\d]{6}_[\d]{10}', dir):
                            if read_v4 or not '_4' in dir: # exclude obs table generation v4 observations (ITN 31)
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
    def __next__(self):
        self._i += 1
        try:
            # close previous observation
            if not self._current_obs is None:
                self._current_obs.close()
                    
            # open next observation and stop iteration if no observations are left
            try:
                self._current_obs = observation( self.directories[self._i-1], keep_null=self._keep_null )
                    
            except IndexError:
                self._i = 0
                raise StopIteration
                    
            return self._current_obs
            
        # Continue with the next observation if there was an error in the current one
        except Exception as e:
        
            # pass StopIteration through
            if e.__class__ == StopIteration:
                raise StopIteration
                
            # display error if desired
            if self._display_errors:
                print( '\033[91m' + "Error reading directory " + self.directories[self._i-1] + ": " + str(e) + " Returning the next valid observation." + '\033[0m' )
            
            # write error to log if error_log is set
            if self._error_log is not None:
                with open( self._error_log, 'a+' ) as f:
                    f.write( "Error reading directory " + self.directories[self._i-1] + ": " + str(e) + " Returning the next valid observation.\n" )
            
            # return next valid observation
            return self.__next__()


# MOVE TO TEST
if __name__ == "__main__":
    obsit = obs_iterator( "/home/chuwyler/Desktop/FITS/", error_log="/home/chuwyler/error.log" )
    for obs in obsit:
        print( "------ " + obs.path + " ------"  )
        obs.sji[0].plot(0)
        #obs.raster[0].plot(0)

