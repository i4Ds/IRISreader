#!/usr/bin/env python

import numpy as np
import copy
import os
import warnings
from irisreader import raster_cube
from irisreader.config import DEBUG_LAZY_LOADING_LEVEL
from irisreader.coalignment import goes_data

class combined_raster( object ):
    """This class implements an abstraction of a combination of IRIS raster FITS 
    files. The access interface is very similar to the one for raster data and
    as much as possible of the concatenation mechanism is hidden.
    
    
    Parameters
    ----------
    filename : str
        Path to the IRIS SJI FITS file.
    line : str
        Line to select: this can be any unique abbreviation of the line name (e.g. "Mg"). For non-unique abbreviations, an error is thrown.
    keep_null : bool
        Controls whether images that are NULL (-200) everywhere are removed from the data cube. keep_null=True keeps NULL images and keep_null=False removes them.
        
        
    Attributes
    ----------
    type : str
        Observation type: 'sji' or 'raster'.
    obsid : str
       Observation ID of the selected observation.
    desc : str
        Description of the selected observation.
    date : str
        Date of the selected observation.
    mode : str
        Observation mode of the selected observation ('sit-and-stare' or 'raster').
    line_info : str
        Description of the selected line.
    n_raster : int
        Number of raster files that are concatenated to one single raster.
    n_raster_steps : int
        List with number of steps per raster: the number of raster steps per single raster files may vary because of images in the sequence that are null or corrupt. This list is lazy loaded.
    n_steps : int
        Number of time steps in the combined raster cube. This quantity is nothing but the sum of n_raster_steps and is therefore also lazy loaded.
    primary_headers : dict
        Dictionary with primary headers of the FITS file (lazy loaded).
    time_specific_headers : dict
        List of dictionaries with time-specific headers of the selected line (lazy loaded).
    line_specific_headers : dict
        Dictionary with line-specific headers of the selected line (lazy loaded).
    headers : dict
        List of combined primary and time-specific headers (lazy loaded).
    """
    
    # constructor
    def __init__( self, filenames, line='', keep_null=False ):
        
        # if only one file is passed make sure it comes as a list
        if not isinstance( filenames, (list, tuple) ):
            filenames = [filenames]
        
        # open raster files (disable individual cube warnings)
        self._raster_data = []
        for raster_file in sorted( filenames ):
            self._raster_data.append( raster_cube( raster_file, line=line, keep_null=keep_null ) )
        self._closed = False
        
        # set FITS type
        self.type = 'raster'
        
        # get obsid, date and description
        self.obsid = self._raster_data[0].obsid
        self.start_date = self._raster_data[0].start_date
        self.end_date = self._raster_data[0].end_date # BUG: this should come from the last raster?
        self.desc = self._raster_data[0].desc
        
        # get observation mode
        if 'sit-and-stare' in self.desc:
            self.mode = 'sit-and-stare'
        else:
            self.mode = 'n-step raster'
            
        # get line information
        self.line_info = self._raster_data[0].line_info

        # number of rasters
        self.n_raster = len( filenames )
        
        # store individual number of raster steps (lazy loaded)
        self.n_raster_steps = [-1] * self.n_raster
        
        # store individual raster lookup table
        self._lookup_table = None
        
        # total number of steps and shape (lazy loaded)
        self.n_steps = -1
        self.shape = None
        
        # primary, time-specific, line-specific and combined headers are lazy loaded
        self.primary_headers = {}
        self.time_specific_headers = []
        self.line_specific_headers = {}
        self.headers = []
        
        # cropping boundaries and indicator whether data cube has been cropped
        self._xmin = None
        self._xmax = None
        self._ymin = None
        self._ymax = None
        self._cropped = False

        # wcs object
        self._wcs = self._raster_data[0]._wcs
        
        
    # lazy load the headers
    def __getattribute__( self, name ): 
        if name=='headers' and object.__getattribute__( self, "headers" ) == []:
            self._prepare_combined_headers()
            return object.__getattribute__( self, "headers" )
        
        elif name=='n_raster_steps' and object.__getattribute__( self, "n_raster_steps" ) == [-1] * self.n_raster:
            self._prepare_n_raster_steps()
            return object.__getattribute__( self, "n_raster_steps" )
        
        elif name=='_lookup_table' and object.__getattribute__( self, "_lookup_table" ) is None:
            self._prepare_lookup_table()
            return object.__getattribute__( self, "_lookup_table" )
        
        elif name=='n_steps' and object.__getattribute__( self, "n_steps" ) == -1:
            self._prepare_n_raster_steps()
            return object.__getattribute__( self, "n_steps" )
        
        elif name=='shape' and object.__getattribute__( self, "shape" ) is None:
            self._prepare_n_raster_steps()
            return object.__getattribute__( self, "shape" )
        
        elif name=='primary_headers' and object.__getattribute__( self, "primary_headers" ) == {}:
            self._prepare_primary_headers()
            return object.__getattribute__( self, "primary_headers" )
        
        elif name=='time_specific_headers' and object.__getattribute__( self, "time_specific_headers" ) == []:
            self._prepare_time_specific_headers()
            return object.__getattribute__( self, "time_specific_headers" )
        
        elif name=='line_specific_headers' and object.__getattribute__( self, "line_specific_headers" ) == {}:
            self._prepare_line_specific_headers()
            return object.__getattribute__( self, "line_specific_headers" )
        
        else:
            return object.__getattribute__( self, name )

    # return the description upon a print call
    def __str__( self ):
        return "raster line window: {}\n(n_steps, n_y, n_lambda) = {}".format( self.line_info, self.shape )
    
    def __repr__( self ):
        return self.__str__()

    # function to lazily prepare individual numbers of steps and total
    def _prepare_n_raster_steps( self ):
        if DEBUG_LAZY_LOADING_LEVEL >= 2: print("DEBUG: [combined raster] Lazy loading individual raster steps")
        n_steps = 0
        n_raster_steps = [0]*self.n_raster
        for i in range( self.n_raster ):
            with warnings.catch_warnings(): # ignore warnings by individual rasters
                warnings.simplefilter("ignore")
                n_raster_steps[i] = self._raster_data[i].n_steps
                n_steps += n_raster_steps[i]
        self.n_raster_steps = n_raster_steps
        self.n_steps = n_steps
        self.shape = tuple( [ self.n_steps ] + list( self._raster_data[0]._fits_file[ self._raster_data[0]._selected_ext ].shape[1:] ) )

    # function to lazily prepare primary headers
    def _prepare_primary_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL  >= 2: print("DEBUG: [combined_raster] Lazy loading primary headers")
        
        # set primary header to the primary header of the first raster
        # CAUTION: some parts of the primary header could change throughout the different raster files.
        self.primary_headers = self._raster_data[0].primary_headers

    # function to lazily concatenate time-specific headers
    def _prepare_time_specific_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL  >= 2: print("DEBUG: [combined_raster] Lazy loading individual time-specific headers")
        time_specific_headers = []
        for raster in self._raster_data:
            time_specific_headers += raster.time_specific_headers
        self.time_specific_headers = time_specific_headers

    # function to lazily prepare line specific headers
    def _prepare_line_specific_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL >= 2: print("DEBUG: [combined_raster] Lazy loading line-specific headers")
        
        # set line-specific header to the line-specific header of the first raster
        # CAUTION: some parts of the line-specific header could change throughout 
        # the different raster files (CRVAL2, CRVAL3, PC*). To avoid any confusion, 
        # these are removed here
        self.line_specific_headers = self._raster_data[0].line_specific_headers
        for key in ['CRVAL2', 'CRVAL3', 'PC1_1', 'PC1_2', 'PC2_1', 'PC2_2', 'PC2_3', 'PC3_1', 'PC3_2', 'PC3_3']:
            del self.line_specific_headers[key]

    # function to prepare combined headers
    def _prepare_combined_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL  >= 2: print("DEBUG: [combined_raster] Lazy loading combined headers")
        headers = []
        for i in range( 0, self.n_raster ):
            headers += self._raster_data[i].headers
        self.headers = headers
    
    # function to prepare lookup table
    def _prepare_lookup_table( self ):
        if DEBUG_LAZY_LOADING_LEVEL  >= 2: print("DEBUG: [combined_raster] Lazy loading lookup table")
        
        self._lookup_table = []
        
        file_no = 0
        file_index = 0
        for i in range( self.n_steps ):
            # raise file_no if file_index is larger than number of raster in file file_no
            if file_index >= self.n_raster_steps[ file_no ]:
                file_index = 0
                file_no += 1
                
                # jump over files with no valid rasters
                while self.n_raster_steps[ file_no ] == 0:
                    file_no += 1
                
            self._lookup_table.append( [i, file_no, file_index] )
            file_index += 1
            
        self._lookup_table = np.vstack( self._lookup_table )
        
    # functions to enter and exit a context
    def __enter__( self ):
        return self
    
    def __exit__( self ):
        self.close()
    
    # caller to behave like a data array
    def __getitem__( self, index ):

        if len( index ) != 3:
            raise ValueError("This is a three-dimensional object, please index accordingly.")
        
        # if index[0] is a single number (not iterable, not a slice), make a list of it
        if not hasattr( index[0], '__iter__') and not isinstance( index[0], slice ):
            time_slices = self._lookup_table[ [index[0]], : ]
        else:
            time_slices = self._lookup_table[ index[0], : ]
        
        slices = []
        
        for file_no in np.unique( time_slices[:,1] ):
            idx = time_slices[time_slices[:,1]==file_no, 2]
            slices.append( self._raster_data[ file_no ][idx, index[1], index[2]] )
        
        return np.vstack( slices )
           
    # function to find raster file and raster position
    def _whereat( self, step ):
                
        if step < 0 or step >= self.n_steps:
            raise ValueError("This is not a valid raster step!")

        return self._lookup_table[ step, 1: ]

    # function to set bounds on images
    def _set_bounds( self, bounds ):
        for i in range(len(self._raster_data)):
            self._raster_data[i]._xmin, self._raster_data[i]._xmax, self._raster_data[i]._ymin, self._raster_data[i]._ymax = bounds
            self._raster_data[i]._cropped = True
        self.shape = tuple( [self.shape[0], self._raster_data[i]._ymax-self._raster_data[i]._ymin, self._raster_data[i]._xmax-self._raster_data[i]._xmin] )
        self._cropped = True
        self._xmin, self._xmax, self._ymin, self._ymax = bounds
        
    # function to remove an image step from the data cube
    def _remove_image_steps( self, steps ):
        if not isinstance( steps, (list, tuple) ):
            steps = [steps]
        
        # update the corresponding individual rasters:
        # make sure here that steps in the same file are deleted simultaneously
        
        # first create an array with the raster file number in the first column
        # and the step number in the second column
        locations = np.empty([0,2], dtype=np.int )
        for step in steps:
            locations = np.vstack( [locations, np.array(self._whereat( step ))] )
        
        # now delete all steps in each file simultaneously
        raster_files = np.unique( locations[:,0] )
        for raster in raster_files:
            steps_to_remove = locations[:,1][locations[:,0] == raster].tolist()
            self._raster_data[ raster ]._remove_image_steps( steps_to_remove )
            
        # update raster steps variables
        self._prepare_n_raster_steps()
        
        # update lookup table
        self._prepare_lookup_table()
        
        # update headers (if loaded already)
        if object.__getattribute__( self, "time_specific_headers" ) != []:
            self._prepare_time_specific_headers()
        if object.__getattribute__( self, "headers" ) != []:
            self._prepare_combined_headers()

    # function to get coordinates for a particular image
    def get_coordinates( self, step ):
        """
        Returns coordinates for the image at the given time step. This 
        function reuses the get_coordinates function of the individual raster files.
  
        Parameters
        ----------
        step : int
            The time step in the raster to get the coordinates for.

        Returns
        -------
        float
            List [coordinates along wavelength axis, coordinates along y axis]
        """
        file_no, raster_step = self._whereat( step )
        return self._raster_data[file_no].get_coordinates( step=raster_step )
            
    # function to get one image only (in case image does not fit into memory)
    # via the raster-specific get_image_step function
    def get_image_step( self, step, divide_by_exptime=True ):
        """
        Returns the image at position step. This function reuses the 
        get_image_step function of the individual raster files.
        
        **Warning**: This function by default divides by exposure time, as this
        is more suitable for automatic processing.
        
        Parameters
        ----------
        step : int
            Time step in the data cube.
            
        Returns
        -------
        numpy.ndarray
            2D image at time step <step>. Format [y,wavelength].
        """
        file_no, raster_step = self._whereat( step )
        return self._raster_data[file_no].get_image_step( step=raster_step, divide_by_exptime=divide_by_exptime )

    # function to get one image only (in case image does not fit into memory)
    # via the raster-specific get_image_step function
    def get_interpolated_image_step( self, step, lambda_min, lambda_max, n_breaks ):
        """
        Returns the image at position step. This function uses the section 
        routine of astropy to only return a slice of the image and avoid 
        memory problems.
        
        **Warning**: This function by default divides by exposure time, as this
        is more suitable for automatic processing.
        
        Parameters
        ----------
        step : int
            Time step in the data cube.
        lambda_min : float
            Minimum wavelength of the interpolation region
        lambda_max : float
            Maximum wavelength of the interpolation region
        n_breaks : int
            Number of uniform breaks in the interpolation region

        Returns
        -------
        numpy.ndarray
            interpolated 2D image at time step <step>. Format: [y,x] (SJI), [y,wavelength] (raster).
        """
        file_no, raster_step = self._whereat( step )
        return self._raster_data[file_no].get_interpolated_image_step( step=raster_step, lambda_min=lambda_min, lambda_max=lambda_max, n_breaks=n_breaks )

    # function to plot image via the raster-specific plot function
    def plot( self, step, y=None, units='pixels', gamma=None, cutoff_percentile=99.9 ):
        """
        Plots the spectrograph window at time step <step>.
        
        Parameters
        ----------
        step : int
            The time step in the SJI.
        y : int
            A pixel position on the slit. If set, only values for this position will be plotted.
        units : str
            Tick units: 'pixels' for indices in the array or 'coordinates' for units in arcseconds on the sun.
        gamma : float
            Gamma exponent for gamma correction that adjusts the plot scale. If gamma is None (default),
            gamma=1 is used for the photospheric SJI 2832 and gamma=0.4 otherwise.
        cutoff_percentile : float
            Often the maximum pixels shine out everything else, even after gamma correction. In order to reduce 
            this effect, the percentile at which to cut the intensity off can be specified with cutoff_percentile
            in a range between 0 and 100.
        """
        
        file_no, raster_step = self._whereat( step )
        self._raster_data[file_no].plot( step=raster_step, y=y, units=units, gamma=gamma, cutoff_percentile=cutoff_percentile )

    # function to close combined raster        
    def close( self ):
        """
        Closes all FITS files.
        """
        for raster in self._raster_data:
            raster.close()
        self._closed = True

    # function to reopen combined raster
    def reopen( self ):
        """
        Reopens FITS files.
        """
        
        if self._closed:
            for raster in self._raster_data:
                raster.reopen()
            self._closed = False
        else:
            print("File is already open - doing nothing")
      


    # function to get millisecond timestamps of images
    def get_timestamps( self ):
        """
        Converts DATE_OBS to milliseconds since 1970 with the aim to make 
        timestamp comparisons easier.
        
        Returns
        -------
        float
            List of millisecond timestamps.
        """
        timestamps=[]
        for raster in self._raster_data:
            timestamps += raster.get_timestamps()
        return timestamps
    
    # function to get number of saturated pixels for an image
    # via the raster-specific nsatpix function
    def get_nsatpix( self, step ):
        """
        Returns the number of saturated pixels in an image. According to
        iris_prep.pro, a pixel is saturated if it has a data number >= 1.6e4.       
        
        Parameters
        ----------
        step : int
            Time step in the data cube.
        
        Returns
        -------
        int
            Number of saturated pixels at time step <step>.
        """
        file_no, raster_step = self._whereat( step )
        return self._raster_data[file_no].get_nsatpix( step=raster_step )
    
    # function to return a copy of this object
    def copy( self ):
        """
        Returns a copy of this combined_raster object.
                
        Returns
        -------
        combined_raster
            Copy of this combined_raster object.
        """
        copied_self = copy.copy( self )
        
        # need also to copy the content of _raster_data, otherwise just the
        # references will be copied
        copied_self._raster_data = [] * len( self._raster_data )
        for raster_obj in self._raster_data:
            copied_self._raster_data.append( raster_obj.copy() )
        
        return copied_self
    
    # function to crop the combined raster
    def crop( self, inplace=True ):
        """        
        Crops the images in the data cube and returns a new data cube object
        if inplace==False and otherwise directly crops the data cube.
        
        This is equivalent to:
        from irisreader.preprocessing import image_cube_cropper
        cropper = image_cube_cropper()
        cropped_cube = cropper.fit_transform( data_cube )
        (and data_cube = cropped_cube if inplace==True)
     
        Arguments
        ---------
        inplace : boolean
            whether to return cropped data cube object (inplace=False) or to
            directly modify the present data cube
           
        Returns
        -------
        iris_data_cube
            Copy of this data cube object.
        """
        if not self._cropped: 
 
            from irisreader.preprocessing import image_cube_cropper
            cropper = image_cube_cropper()
            cropped = cropper.fit_transform( self )
        
            if inplace:
                self.close()
                self.__dict__.update(cropped.__dict__)
            else:
                return cropped
            
        else:
            print("This data cube has already been cropped - doing nothing.")
            
            if not inplace:
                return self

    # function to get goes flux information
    def get_goes_flux( self ):
        
        timestamps = np.array( [] )
        g = goes_data( self.start_date, self.end_date, os.path.dirname( self._raster_data[0]._filename ) + "/goes_data", lazy_eval=True )
            
        for raster in self._raster_data:
            if raster.n_steps > 0:
                timestamps = np.append( timestamps, raster.get_timestamps() )
        return g.interpolate( timestamps )

