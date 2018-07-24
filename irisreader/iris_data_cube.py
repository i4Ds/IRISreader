#!/usr/bin/env python

from astropy.io import fits
from astropy.wcs import WCS
from datetime import datetime as dt, timedelta
import numpy as np
import os
import warnings
import copy
from irisreader.config import DEBUG_LAZY_LOADING_LEVEL
from irisreader.coalignment import goes_data
from irisreader.utils.date import to_epoch, from_Tformat, to_Tformat

class iris_data_cube( object ):
    """This class implements an abstraction of an IRIS FITS file, specifically it gives
    access to data cubes and individual image headers stored in the different
    extensions. It provides a prototype for sji_cube and raster_cube and 
    should only be used internally.
    
    Parameters
    ----------
    filename : string
        Path to the IRIS FITS file.
    line : string
        Line to select: this can be any unique abbreviation of the line name (e.g. "Mg"). For non-unique abbreviations, an error is thrown.
    keep_null : boolean
        Controls whether images that are NULL (-200) everywhere are removed from the data cube (keep_null=False) or not (keep_null=True).
        
        
    Attributes
    ----------
    type : str
        Observation type: 'sji' or 'raster'.
    obsid : str
        Observation ID of the selected observation.
    desc : str
        Description of the selected observation.
    start_date : str
        Start date of the selected observation.
    end_date : str
        End date of the selected observation.
    mode : str
        Observation mode of the selected observation ('sit-and-stare' or 'raster').
    line_info : str
        Description of the selected line.
    n_steps : int
        Number of time steps in the data cube (this is affected by the keep_null argument).
    primary_headers: dict
        Dictionary with primary headers of the FITS file (lazy loaded).
    time_specific_headers: dict
        List of dictionaries with time-specific headers of the selected line (lazy loaded).  
    shape : tuple
        Shape of the data cube (this is affected by the keep_null argument)
    """
    
    # constructor
    def __init__( self, filename, line='', keep_null=False ):
        
        # set parameters as variables
        self._filename = filename
        self._line = line
        self._keep_null = keep_null
        
        # open file
        self._fits_file = fits.open( filename )
        self._closed = False

        # get FITS type
        if 'INSTRUME' in self._fits_file[0].header.keys() and 'SJI' in self._fits_file[0].header['INSTRUME']:
            self.type = 'sji' 
        elif 'INSTRUME' in self._fits_file[0].header.keys() and 'SPEC' in self._fits_file[0].header['INSTRUME']:
            self.type = 'raster'
        else:
            self.close()
            raise ValueError( "This file is neither IRIS SJI nor raster!" )
        
        # get extensions with data cubes and set first and last data extension
        # unfortunately measuring the length of the hdulist requires loading all
        # the file (before extensions are lazy loaded). The number of extensions
        # is a crucial info, finding another way to know the number of elements
        # of the hdulist would save around 1s when opening 100 raster files.
        self._n_ext = len( self._fits_file )
        data_cube_extensions = []
        for i in range( self._n_ext ):
            if hasattr( self._fits_file[i], 'shape' ) and len( self._fits_file[i].shape ) == 3:
                data_cube_extensions.append( i )
                
        if len( data_cube_extensions ) == 0:
            raise ValueError( "No data cubes found." )
        
        self._first_data_ext = min( data_cube_extensions )
        self._last_data_ext = max( data_cube_extensions )
        
        # set extension for selected line
        if line == '':
            self._selected_ext = self._first_data_ext # choose first line by default
        elif self._line2extension( line ) != -1: 
            self._selected_ext = self._line2extension( line )
        else:
            self.close()
            raise ValueError(('Change the line parameter: The desired spectral'
                              ' window is either not found or specified'
                              ' ambiguously.'))
        
        # check whether the extensions come with the right dimensions
        if len( self._fits_file[ self._selected_ext ].shape ) != 3:
            raise ValueError( "The data extension does not contain a three-dimensional data cube!" )
        
        if len( self._fits_file[ self._n_ext-2 ].shape ) != 2:
            raise ValueError( "The time-specific header extension does not contain a two-dimensional data cube!" )
        
        # the valid images, number of steps and shape will be lazy created
        self._valid_images = [-1]
        self.n_steps = -1
        self.shape = None

        # the primary headers will be lazy loaded (conversion to dict takes time)
        self.primary_headers = {}

        # the time-specific headers will be lazy loaded
        self.time_specific_headers = [-1]
        
        # initialize the combined headers
        self.headers = [-1]
                
        # set obsid
        self.obsid = self._fits_file[0].header['OBSID']
        
        # set date
        self.start_date = dt.strptime( self._fits_file[0].header['STARTOBS'], '%Y-%m-%dT%H:%M:%S.%f' )
        self.end_date = dt.strptime( self._fits_file[0].header['ENDOBS'], '%Y-%m-%dT%H:%M:%S.%f' )

        # get description
        self.desc = self._fits_file[0].header['OBS_DESC']
        
        # get observation mode
        if 'sit-and-stare' in self.desc:
            self.mode = 'sit-and-stare'
        else:
            self.mode = 'n-step raster'
            
        # line information (SJI info is replaced by actual line information)
        self.line_info = self._fits_file[0].header['TDESC'+str(self._selected_ext-self._first_data_ext+1)]
        self.line_info = self.line_info.replace( 'SJI_1330', 'C II 1330' )
        self.line_info = self.line_info.replace( 'SJI_1400', 'Si IV 1400' )
        self.line_info = self.line_info.replace( 'SJI_2796', 'Mg II h/k 2796' )
        self.line_info = self.line_info.replace( 'SJI_2832', 'Mg II wing 2832' )
        
        # cropping information (used by image_cube_cropper in the preprocessing module)
        self._xmin = None
        self._xmax = None
        self._ymin = None
        self._ymax = None
        self._cropped = False
        
        # initialize WCS object and suppress warnings
        # set CDELT3 to a tiny value if zero (otherwise wcs produces singular PC matrix)
        # see e.g. discussion at https://github.com/sunpy/irispy/issues/78
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if self._fits_file[self._selected_ext].header['CDELT3'] == 0:
                self._fits_file[self._selected_ext].header['CDELT3'] = 1e-10
                self._wcs = WCS( self._fits_file[self._selected_ext].header )
                self._fits_file[self._selected_ext].header['CDELT3'] = 0
            else:
                self._wcs = WCS( self._fits_file[self._selected_ext].header )
        

    # lazy load _valid_images, time_specific_headers and n_steps
    def __getattribute__( self, name ):
        if name=='_valid_images' and object.__getattribute__( self, "_valid_images" ) == [-1]:
            self._prepare_valid_images()
            return object.__getattribute__( self, "_valid_images" )
        
        elif name=='n_steps' and object.__getattribute__( self, "n_steps" ) == -1:
            self._prepare_valid_images()
            return object.__getattribute__( self, "n_steps" ) 

        elif name=='shape' and object.__getattribute__( self, "shape" ) == None:
            self._prepare_valid_images()
            return object.__getattribute__( self, "shape" )
        
        elif name=='primary_headers' and object.__getattribute__( self, "primary_headers" ) == {}:
            self._prepare_primary_headers()
            return object.__getattribute__( self, "primary_headers" ) 
            
        elif name=='time_specific_headers' and object.__getattribute__( self, "time_specific_headers" ) == [-1]:
            self._prepare_time_specific_headers()
            return object.__getattribute__( self, "time_specific_headers" ) 
            
        else:
            return object.__getattribute__( self, name )

    # lazy load _valid_images - remove NULL images if keep_null is False
    def _prepare_valid_images( self ):
        if DEBUG_LAZY_LOADING_LEVEL >= 4: print("DEBUG: [iris_data_cube] Lazy loading valid images")
        valid_images = []
        for i in range( self._fits_file[ self._selected_ext ].shape[0] ):
            if self._keep_null or not np.all( self._fits_file[ self._selected_ext ].section[i,:,:] == -200 ):
                valid_images.append(i)
        
        # TODO: annoying warning message -- can the raster check whether its part of a combined raster and not output it?
        if valid_images == []:
            warnings.warn("This data cube contains no valid images!")
        
        self._valid_images = valid_images
        self.n_steps = len( valid_images )
        self.shape = tuple( [ self.n_steps ] + list( self._fits_file[ self._selected_ext ].shape[1:] ) )

    # lazy load primary headers
    def _prepare_primary_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL >= 4: print("DEBUG: [iris_data_cube] Lazy loading primary headers")
        self.primary_headers = dict( self._fits_file[0].header )
        self.primary_headers['SAA'] = self.primary_headers['SAA'].strip() 
        self.primary_headers['NAXIS'] = 2
        
        # remove empty headers
        if '' in self.primary_headers.keys():
            del self.primary_headers['']
        
        # DATE_OBS may not always be there: set it to STARTOBS
        if not 'STARTOBS' in self.primary_headers.keys() or self.primary_headers['STARTOBS'].strip() == '':
            raise ValueError( "No STARTOBS in primary header!" )
        else:
            self.primary_headers['DATE_OBS'] = self.primary_headers['STARTOBS']

    # lazy load time_specific_headers (involves lazy loading _valid_images)
    def _prepare_time_specific_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL >= 4: print("DEBUG: [iris_data_cube] Lazy loading time specific headers")
        time_specific_headers = self._array_to_dict( self._n_ext-2 )
        self.time_specific_headers = [time_specific_headers[i] for i in self._valid_images]
        
    # empty method to prepare combined headers (introduced in raster/sji)
    def _prepare_combined_headers( self ):
        pass
    
    # empty method to prepare line-specific headers (introduced in raster)
    def _prepare_line_specific_headers( self ):
        pass
        
    # functions to enter and exit a context
    def __enter__( self ):
        return self
    
    def __exit__( self ):
        self.close()
    
    # close the file
    def close( self ):
        """
        Closes the FITS file.
        """
        self._fits_file.close()
        self._closed = True
        
        # manually delete data object, otherwise memory mapping will keep file open
        # (http://docs.astropy.org/en/stable/io/fits/appendix/faq.html#id18)
        del self._fits_file[self._selected_ext].data
    
    # reopen the file
    def reopen( self ):
        """
        Reopens the FITS file.
        """
        if self._closed:
            self.__init__( self._filename, self._line, self._keep_null )
            self._closed = False
        else:
            print("File is already open - doing nothing")
    
    # caller to behave like a data array
    # TODO: Place a warning - slicing can take time, regarding whether the slices are close in memory!
    # Regarding timing: around 10-20% can be lost due to the fact that we transform the slice over the time step to a list
    # In the future a speed up could be achieved by trying to preserve slices there.

    def __getitem__( self, index ):
        """
        Abstracts access to the data cube. While in the get_image_step function
        data is loaded through the the section method to make sure that only
        the image requested by the user is loaded into memory, this method
        directly accesses the data object of the hdulist, allowing faster slicing
        of data. Whenever slices are not required, the get_image_step function
        should be used, since access through the data object can lead to 
        memory problems.
        
        If the data cube happens to be cropped, this method will automatically
        abstract access to the cropped data. If keep_null=False, null images
        will automatically be removed from the representation.
        """
        
        # check dimensions (this rules out ellipsis argument for the moment)        
        if len( index ) != 3:
            raise ValueError("This is a three-dimensional object, please index accordingly.")
        
        # uncropped data cube: x, y slices do not need to be shifted
        if not self._cropped:
            return self._fits_file[ self._selected_ext ].data[ np.array( self._valid_images )[ index[0] ], index[1], index[2] ]
            
        # cropped data cube: shift x, y slices so that they start at xmin, xmax
        else:
            # make sure that slices stay slices (more efficient than lists, about 30% faster), otherwise resort to list
            if isinstance( index[1], slice ):
                a = self._ymin if index[1].start is None else index[1].start+self._ymin
                b = self._ymax if index[1].stop is None else index[1].stop+self._ymin                
                internal_index1 = slice( a, b, index[1].step )
                
            else:
                internal_index1 = np.arange( self._ymin, self._ymax )[ index[1] ]
                
            if isinstance( index[2], slice ):
                a = self._xmin if index[2].start is None else index[2].start+self._xmin
                b = self._xmax if index[2].stop is None else index[2].stop+self._xmin                
                internal_index2 = slice( a, b, index[2].step )
                
            else:
                internal_index2 = np.arange( self._xmin, self._xmax )[ index[2] ]
    

            return self._fits_file[ self._selected_ext ].data[ np.array( self._valid_images )[ index[0] ], internal_index1, internal_index2 ]
        

    # function to translate headers stored in a data array
    def _array_to_dict( self, extension ):
        """
        Reads (key, index) pairs from the header of the extension and uses them
        to assign each row of the data array to a dictionary.
        """
        
        # some headers are not keys but real headers: remove them
        keys_to_remove=['XTENSION', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'PCOUNT', 'GCOUNT']
        header_keys = dict( self._fits_file[extension].header )
        header_keys = {k: v for k, v in header_keys.items() if k not in keys_to_remove}
        
        # make sure data array has the same number of columns like the
        # number of headers.
        if self._fits_file[extension].shape[1] == len( header_keys ):
        
            # initialize dictionary list
            res = [dict() for x in range(self._fits_file[extension].shape[0])]
        
            # fill dictionaries and set DATE_OBS to the real DATE_OBS = STARTOBS + TIME
            for i in range(0, self._fits_file[extension].shape[0]):
                res[i] = dict( zip( header_keys.keys(), self._fits_file[extension].data[i,list(header_keys.values())] ) )
                res[i]['DATE_OBS'] = to_Tformat( from_Tformat( self._fits_file[0].header['STARTOBS'] ) + timedelta(seconds=res[i]['TIME']))

            return res
        
        else:
            raise ValueError("Corrupt data file: second extension has not the "
                             "same amount of columns as its number of headery keys.")
    
    # function that converts wavelength string into extension number
    # the image extensions are stored in extensions [1,ext-3] = [1,n_lines]
    def _line2extension( self, line ):
        """
        Converts wavelength string into an extension number.
        Returns -1 if the line could not be found or several lines where found.
        """
        
        keys = [k for k in self._fits_file[0].header.keys() if k.startswith("TDESC")]
        line_descriptions = [self._fits_file[0].header[k] for k in sorted(keys)]
        res = [s for s in line_descriptions if line in s]        
        if len( res ) != 1: 
            return -1
        else:
            return line_descriptions.index( res[0] ) + 1

    # function to set bounds on images
    def _set_bounds( self, bounds ):
        self._xmin, self._xmax, self._ymin, self._ymax = bounds
        self.shape = tuple( [self.shape[0], self._ymax-self._ymin, self._xmax-self._xmin] )
        self._cropped = True

    # function to remove an image step from the data cube
    def _remove_image_steps( self, steps ):
        if not isinstance( steps, (list, tuple) ):
            steps = [steps]
            
        # some images might already be removed, here we make sure that they are properly indexed
        self._valid_images = sorted( list( set(self._valid_images) - set([self._valid_images[i] for i in steps]) ) )
        
        # update number of steps
        self.n_steps = len( self._valid_images )
        self.shape = tuple( [self.n_steps] + list( self.shape[1:]) )
        
        # update headers (if loaded already)
        if object.__getattribute__( self, "time_specific_headers" ) != []:
            self._prepare_time_specific_headers()
        if object.__getattribute__( self, "headers" ) != []:
            self._prepare_combined_headers()
        
    # function to get one image only
    def get_image_step( self, step, divide_by_exptime=True ):
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
        divide_by_exptime : bool
            Whether to divide image by its exposure time or not. Dividing by exposure
            time will present a normalized image instead of the usual data numbers.
            
        Returns
        -------
        numpy.ndarray
            2D image at time step <step>. Format: [y,x] (SJI), [y,wavelength] (raster).
        """
        
        # Check whether line and step exist
        if step < 0 or step >= len( self._valid_images ):
            raise ValueError( "This image step does not exist!" )
        
        # Return bounded image if _xmin, _xmax, _y_min and _y_max are all set
        # Note: In this part we directly use the section method, as it is faster
        # than access through the data object of the hdulist
        if self._cropped:
            img = self._fits_file[self._selected_ext].section[self._valid_images[step],self._ymin:self._ymax, self._xmin:self._xmax] 
        else:
            img = self._fits_file[self._selected_ext].section[self._valid_images[step],:,:]
            
        # Divide by exposure time if desired
        # Make sure that negative values are not scaled, otherwise it can interfere with cropping
        # TODO: This is not very beautiful, replace this in the future
        if divide_by_exptime:
            if self.headers == [-1]:
                warnings.warn("Exposure time is not available at the iris_data_cube level, did not divide by exposure time.")
            else:                
                img[img>0] /= self.headers[step]['EXPTIME']

        return img
    
    # TODO: rewrite get_image_step in raster / sji and introduce divide_by_exptime

    # function to get number of saturated pixels for an image
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
        
        return np.sum( self.get_image_step( step, divide_by_exptime=False ) >= 1.6e4 )
        
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
        timestamps = []
        for i in range( 0, self.n_steps ):
            timestamps.append( to_epoch( from_Tformat( self.time_specific_headers[i]['DATE_OBS'] ) ) )
        return timestamps
    
    # function to return a copy of this object
    def copy( self ):
        """
        Returns a copy of this data cube object.
                
        Returns
        -------
        iris_data_cube
            Copy of this data cube object.
        """
    
        # create copy using copy from copy package    
        copied_self = copy.copy( self )
        
        # create a new file handle
        copied_self._fits_file = fits.open( copied_self._filename, memmap=False )

        return( copied_self )
    
    # function to crop the data cube    
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
        
    # function to add goes xray intensity
    def get_goes_flux( self ):        
        if self.n_steps > 0:
            g = goes_data( self.start_date, self.end_date, os.path.dirname( self._filename ) + "/goes_data", lazy_eval=True )
            return g.interpolate( self.get_timestamps() )
        else:
            return np.array([])
        


        
if __name__ == "__main__":
    #fits_data1 = iris_data_cube( 'data/IRIS_SJI_test.fits' )
    fits_data1 = iris_data_cube( '/home/chuwyler/Desktop/FITS/20140910_112825_3860259453/iris_l2_20140910_112825_3860259453_SJI_1400_t000.fits' )
    fits_data2 = iris_data_cube( 'data/IRIS_raster_test1.fits', line="Mg" )
