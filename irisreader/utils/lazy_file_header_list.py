#!/usr/bin/env python3

import numpy as np

class lazy_file_header_list:
    """
    This class abstracts a list of headers stored in many different files.
    It holds a list for every file of iris_data_cube and loads headers lazy
    upon request. It abstracts access such that it can be used almost like a
    regular python list (assigning to elements is currently not implemented).
    
    Parameters
    ----------
    valid_steps : numpy.ndarray
        valid_steps array from iris_data_cube
    file_load_fn : function
        function to load a specific file
    """

    # constructor    
    def __init__( self, valid_steps, file_load_fn ):
        # the valid steps numpy array from iris_data_cube, passed by reference!
        self._valid_steps = valid_steps
        
        # function to load a specific file
        self._load_file = file_load_fn
        
        # create a list with a sublist for every file: this is the representation
        # under the hood
        n_files = int( np.max( valid_steps[:,0] ) + 1 )
        self._data = [[]] * n_files

    # abstract access to the headers in order to appear as list on the outside
    # this function can return both single items but also slices of data
    def __getitem__( self, index ):
        
        # get file number and file step (numpy array)
        steps = self._valid_steps[ index, : ]
        
        # if steps contains only one line: make sure it's two-dimensional
        if steps.ndim == 1:
            steps = steps.reshape(1,-1)
        
        # load all the required files and create a list with the requested data
        res = []
        for file_no in np.unique( steps[:,0] ):
            if len( self._data[ file_no ] ) == 0: # load data if not there yet
                self._data[ file_no ] = self._load_file( file_no )
            
            # get file steps that are to be used
            file_steps = steps[steps[:,0]==file_no,:][:,1]
            
            # append the headers to the output
            res.extend( [ self._data[ file_no ][i] for i in file_steps ] )
        
        # make sure that single outputs are not encapsulated in a list
        if len(res) == 1:
            return res[0]
        else:
            return res
    
    # returns the number of headers that are (lazily) available    
    def __len__( self ):
        return self._valid_steps.shape[0]
   
    # too complicated to deal with slices: raise an error if user wants to set a whole slice
    def __setitem__( self, index, value ):
        if isinstance( index, (list, tuple, slice) ):
            raise NotImplementedError( "The assignment of arrays to lazy header lists is currently not possible. Please use .tolist() to get a list representation" )
        
        self[index] # make sure the file belonging to index is loaded
        file_no, file_step = self._valid_steps[ index, : ]
        self._data[ file_no ][ file_step ] = value

    # delete an item (e.g. when removing bad images after cropping)    
    # this is done automatically, since _valid_steps is passed by reference!    
    # def __delitem__( self, index )

    # convert representation into a regular python list (will load everything)
    def tolist( self ):
        return self[:]

    # upon print call return a list representation (will load everything)
    def __repr__( self ):
        return str( self.tolist() )

# Test code
if __name__ == "__main__":
    import irisreader as ir
    from irisreader import iris_data_cube
    ir.config.verbosity_level = 4
    raster_data = iris_data_cube( 
           [ "/home/chuwyler/Desktop/IRISreader/irisreader/data/IRIS_raster_test1.fits", 
            "/home/chuwyler/Desktop/IRISreader/irisreader/data/IRIS_raster_test2.fits" ],
            line="Mg"
    )
    
    lh = lazy_file_header_list( raster_data._valid_steps, raster_data._load_time_specific_header_file )
    
    for header in lh:
        print( header['DATE_OBS'] )
    



