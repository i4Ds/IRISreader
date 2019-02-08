#!/usr/bin/env python3

"""
file_hub class: 
Manages access to FITS files with a stack, making sure that the open file limit
of the host system is never reached.
"""

# file method to open fits files
from astropy.io import fits

# access to verbosity_level and use_mmmap
import irisreader as ir

# handler for warnings
import warnings

def ASTROPY_FILE_METHOD( path ):
    """
    Astropy method to open a FITS file.
    This method is controlled through ir.config
    """
    handle = fits.open( path, memmap=ir.config.use_memmap )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        handle.verify('fix')
        
    return handle

# class for a simple stack
class file_stack:
    """
    Class that models a file stack with special features for the problem at hand.
    Only intended for use by file_hub.
    """
    
    def __init__( self, file_method, max_size ):
        
        # stack variables
        self._paths = []
        self._handles = []
        self._modes = []
        
        # properties
        self.max_size = max_size
        self._file_method = file_method
        
    def get_by_index( self, idx ):
        """
        Gets an object from the stack by index.
        
        Parameters
        ----------
        idx : int
            stack index
        
        Returns
        -------
        dict :
            layer of the stack with file information: path, handle and mode
        """
        return  { 'path': self._paths[idx], 'handle': self._handles[idx], 'mode': self._modes[idx] }
    
    def push( self, path, mode="volatile" ):
        """
        Pushes an item onto the stack.
        
        Paramters
        ---------
        path : str
            file path
        mode : str
            open mode: volatile (default) or persistent
            
        Returns
        -------
        dict :
            layer of the stack with information on the file: path, handle and mode
        """
        
        # check mode
        if not mode in ['persistent', 'volatile']:
            raise ValueError( "Please specify a valid mode, either 'persistent' or 'volatile'" )
        
        # object is already on the stack: return it
        if path in self._paths:
            if ir.config.verbosity_level >= 3: print( "[file hub] item is already on stack" )
            idx = self._paths.index( path )
            
            # mode might have changed, update it
            self._modes[ idx ] = mode
            
            # return item from the stack
            return self.get_by_index( idx )
            
        # object is not yet on the stack: open file and put it there
        else:
            
            # drop the oldest item from the stack if maximum size reached
            if len( self._paths ) >= self.max_size:
                self.drop()
            
            # open file handle and catch too many files errors
            handle = self._file_method( path )
            
            if ir.config.verbosity_level >= 3: print( "[file hub] opening and pushing {} to stack".format( path ) )           
            self._paths.append( path )
            self._handles.append( handle )
            self._modes.append( mode )
            
            # return the item (last on stack)
            return self.get_by_index( -1 )

    
    def drop_by_idx( self, idx ):
        """
        Drops an item from the stack by index.
        
        Parameters
        ----------
        idx : int
            stack index
        """

        if ir.config.verbosity_level >= 3: print( "[file hub] dropping {} from stack".format( self._paths[idx] ) )
        
        # close file
        self._handles[idx].close()
        
        # remove file from stack
        del self._paths[idx]
        del self._handles[idx]
        del self._modes[idx]    
            
    def drop( self, path=None ):
        """
        Drops an item from the stack: pops the oldest non-persistent if file path not specified.
        
        Parameters
        ----------
        path : str
            Path to a file to drop (defaults to None: pop oldest non-persistent file)
        """
        
        # remove the oldest file from the stack
        if path is None:
        
            # find the oldest item that is not persistent and drop it
            dropped_item = False
            for i in range( len( self._paths ) ):
                if self._modes[i] == 'volatile':
                    self.drop_by_idx( i )
                    dropped_item = True
                    break
        
            # if no item could be dropped, dropped the oldest persistent one and raise warning
            if dropped_item == False:
                self.drop_by_idx( 0 )              
                warnings.warn( "Stack is full of persistent files, dropping the oldest persistent file. You might want to change your file handling strategy." )
        
        # remove a particular file from the stack
        else:
            if path in self._paths:
                idx = self._paths.index( path )
                self.drop_by_idx( idx )
            
    def reset( self ):
        """
        Resets the stack: closes all file handles and drops all layers
        """
        
        # close all files
        for i in range( len( self._handles ) ):
            self._handles[i].close()
        
        # reset stack variables
        self._paths = []
        self._handles = []
        self._modes = []
            
    def peek( self ):
        """
        Returns the content of the stack in a neatly formatted way.
        """
        peek_str = "{} open files (maximum is {})".format( self.size(), self.max_size )
        peek_str += "\n\n{:10}\t{}".format( "mode", "path" )
        for i in range( len( self._paths ) ):
            peek_str += "\n{:10}\t{}".format( self._modes[i], self._paths[i] ) 
            
        return peek_str
    
    
    def size( self ):
        """Returns the size of the stack"""
        return len( self._paths )


# file hub class that builds on file_stack
class file_hub:
    """
    File Hub: Abstracts access to FITS files, thereby making sure that the maximum
    open files limit of the host system is not reached while keeping as much data
    as possible in memory.
    """
    
    def __init__( self, file_method ):
        
        # stack of open files
        self._file_stack = file_stack( file_method, max_size=ir.config.max_open_files )

    # open a file and push it to the stack
    def open( self, path, mode="volatile" ):
        """
        Open a file and push it to the stack.
        
        Parameters
        ----------
        path : str
            file path
        mode : str
            open mode: volatile (default) or persistent
            
        Returns
        -------
        astropy.io.fits.hdu :
            Handle to open file.
        """
        
        # try to push path to stack and retrieve and return handle
        item = self._file_stack.push( path, mode )
        return item['handle']
    
    # close a file and drop it from the stack
    def close( self, path ):
        """
        Close a file handle and remove the file from the stack.
        
        Parameters
        ----------
        str :
            file path
        """
        
        # manually delete data objects, otherwise memory mapping will keep file open
        # (http://docs.astropy.org/en/stable/io/fits/appendix/faq.html#id18)
        if path in self._file_stack._paths:
            idx = self._file_stack._paths.index( path )
            for i in range( len( self._file_stack._handles[idx] ) ):
                del self._file_stack._handles[idx][i].data
    
        # drop file from stack
        self._file_stack.drop( path )
        
    def reset( self ):
        """Resets the file hub"""
        self._file_stack.reset()
        self._file_stack.max_size = ir.config.max_open_files
        
    # display stack  
    def __repr__( self ):
        return self._file_stack.peek()
    
    # get number of open files
    def __len__( self ):
        return self._file_stack.size()
        

# MOVE TO TEST            
if __name__ == "__main__":

    # do tests with other files and the open function
    
    PATHS = [ "/home/chuwyler/Desktop/FITS/20140202_210830_3880012095/iris_l2_20140202_210830_3880012095_SJI_1330_t000.fits",
              "/home/chuwyler/Desktop/FITS/20140301_045524_3882010194/iris_l2_20140301_045524_3882010194_SJI_2796_t000.fits",
              "/home/chuwyler/Desktop/FITS/20140301_045524_3882010194/iris_l2_20140301_045524_3882010194_SJI_2832_t000.fits",
              "/home/chuwyler/Desktop/FITS/20140301_045524_3882010194/iris_l2_20140301_045524_3882010194_SJI_1330_t000.fits",
              "/home/chuwyler/Desktop/FITS/20140202_210830_3880012095/iris_l2_20140202_210830_3880012095_raster_t000_r00000.fits", 
              "/home/chuwyler/Desktop/FITS/20140202_210830_3880012095/iris_l2_20140202_210830_3880012095_SJI_2796_t000.fits", 
              "/home/chuwyler/Desktop/FITS/20140202_210830_3880012095/iris_l2_20140202_210830_3880012095_SJI_1400_t000.fits", 
              "/home/chuwyler/Desktop/FITS/20140910_112825_3860259453/iris_l2_20140910_112825_3860259453_SJI_1400_t000.fits", 
              "/home/chuwyler/Desktop/FITS/20140910_112825_3860259453/iris_l2_20140910_112825_3860259453_SJI_2796_t000.fits",
              "/home/chuwyler/Desktop/FITS/20140910_112825_3860259453/iris_l2_20140910_112825_3860259453_raster_t000_r00000.fits" ]
    
    file_method = fits.open
    fhub = file_hub( file_method, max_files=5 )

    for path in PATHS:
        print( fhub )
        handle = fhub.open( path, mode="persistent" )
        headers = len ( handle[0].header )
        print( headers )

