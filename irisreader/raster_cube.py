#!/usr/bin/env python

# import libraries
import matplotlib.pyplot as plt
import numpy as np
import re
from irisreader import iris_data_cube
from irisreader.config import DEBUG_LAZY_LOADING_LEVEL
from irisreader.utils import coordinates as co


# some unit conversions
UNIT_M_NM = 1e10
UNIT_DEC_ARCSEC = 3600

# define raster class
class raster_cube( iris_data_cube ):
    """This class implements an abstraction of an IRIS raster FITS file on top of the
    iris_data_cube class. Raster files are more complex than SJI files and
    require more modifications, especially since there are also line-specific
    headers. The headers are parsed in a way similar to solar soft's read_iris_l2 
    and data is made available in time-step chunks in order to avoid memory mapping.
    Note that raster_cube will only load one line out of multiple lines contained
    in the FITS file, specified via the line parameter.
    
    
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
    r_value : int
        Sequence number of the raster file.
    n_steps : int
        Number of time steps in the data cube.
    primary_headers: dict
        Dictionary with primary headers of the FITS file (lazy loaded).
    time_specific_headers: dict
        List of dictionaries with time-specific headers of the selected line (lazy loaded).
    line_specific_headers: dict
        Dictionary with line-specific headers of the selected line (lazy loaded).
    headers: dict
        List of combined primary and time-specific headers (lazy loaded).
    """
    
    # constructor
    def __init__( self, filename, line='', keep_null=False ):
    
        # initialize constructor of iris_data_cube
        iris_data_cube.__init__( self, filename=filename, line=line, keep_null=keep_null )
        
        # initialize line specific headers (lazy loaded)
        self.line_specific_headers = {}
        
        # set r value
        m = re.search( "_r([0-9]{5})\.", self._filename )
        if m:
            self.r_value = int( m.group(1) )
        else:
            self.r_value = None
        
        # raise error if the data_cube is a sji
        if self.type=='sji':
            self.close()
            raise ValueError("This is a SJI file. Please use sji_cube to open it.")
    
    
    # lazy load the headers
    def __getattribute__( self, name ):
        if name=='_valid_images' and object.__getattribute__( self, "_valid_images" ) == [-1]:
            iris_data_cube._prepare_valid_images( self )
            return iris_data_cube.__getattribute__( self, "_valid_images" )
        
        elif name=='n_steps' and object.__getattribute__( self, "n_steps" ) == -1:
            iris_data_cube._prepare_valid_images( self )
            return iris_data_cube.__getattribute__( self, "n_steps" ) 
        
        elif name=='shape' and object.__getattribute__( self, "shape" ) == None:
            self._prepare_valid_images()
            return object.__getattribute__( self, "shape" )
           
        elif name=='primary_headers' and object.__getattribute__( self, "primary_headers" ) == {}:
            iris_data_cube._prepare_primary_headers( self )
            return iris_data_cube.__getattribute__( self, "primary_headers" )     
            
        elif name=='time_specific_headers' and object.__getattribute__( self, "time_specific_headers" ) == [-1]:
            self._prepare_time_specific_headers()
            return self.__getattribute__( "time_specific_headers" ) 
        
        elif name=='line_specific_headers' and object.__getattribute__( self, "line_specific_headers" ) == {}:
            self._prepare_line_specific_headers()
            return self.__getattribute__( "line_specific_headers" ) 
        
        elif name=='headers' and object.__getattribute__( self, "headers" ) == [-1]:
            self._prepare_combined_headers()
            return object.__getattribute__( self, "headers" )
            
        else:
            return object.__getattribute__( self, name )

    # return the description upon a print call
    def __str__( self ):
        return "raster line window: {}\n(n_steps, n_y, n_lambda) = {}".format( self.line_info, self.shape )
    
    def __repr__( self ):
        return self.__str__()

    # function to prepare time_specific_headers
    def _prepare_time_specific_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL >= 3: print("DEBUG: [raster cube] Lazy loading time specific headers")
        iris_data_cube._prepare_time_specific_headers( self )
        time_specific_headers = self.__getattribute__( "time_specific_headers" ) 
        
        # remove some headers that are not needed and fix some headers manually
        for i in range(0, self.n_steps):
            time_specific_headers[i]['DSRCRCNIX'] = time_specific_headers[i].pop('DSRCNIX') # just rename this header
            
            for key_to_remove in ['PC1_1IX', 'PC1_2IX', 'PC2_1IX', 'PC2_2IX', 'PC2_3IX', 'PC3_1IX', 'PC3_2IX', 'PC3_3IX', 'OPHASEIX', 'OBS_VRIX']:
                if key_to_remove in time_specific_headers[i].keys():
                    del time_specific_headers[i][ key_to_remove ]
                    
        self.time_specific_headers = time_specific_headers
    
    # function to prepare line_specific_headers
    def _prepare_line_specific_headers( self ):
        if DEBUG_LAZY_LOADING_LEVEL >= 3: print("DEBUG: [raster_cube] Lazy loading line specific headers")
        line_specific_headers = dict( self._fits_file[ self._selected_ext ].header )
        
        # add wavelnth, wavename, wavemin and wavemax (without loading primary headers)
        line_specific_headers['WAVELNTH'] = self._fits_file[0].header['TWAVE'+str(self._selected_ext-self._first_data_ext+1)]
        line_specific_headers['WAVENAME'] = self._fits_file[0].header['TDESC'+str(self._selected_ext-self._first_data_ext+1)]
        line_specific_headers['WAVEMIN'] =  self._fits_file[0].header['TWMIN'+str(self._selected_ext-self._first_data_ext+1)]
        line_specific_headers['WAVEMAX'] =  self._fits_file[0].header['TWMAX'+str(self._selected_ext-self._first_data_ext+1)]
        
        self.line_specific_headers = line_specific_headers
    
    # function to prepare combined headers
    def _prepare_combined_headers( self ):
        """
        Prepares the combination (primary header, time-specific header, 
        line-specific header) lazily for each image.
        """
        if DEBUG_LAZY_LOADING_LEVEL >= 3: print( "Lazy loading combined headers" )
        self.headers = [ dict( list(self.primary_headers.items()) + list(self.line_specific_headers.items()) + list(t_header.items()) ) for t_header in self.time_specific_headers ]

        # Fix some headers manually
        for i in range( 0, self.n_steps ):
            self.headers[i]['XCEN'] = self.headers[i]['XCENIX'] # this is not modified in IDL!
            self.headers[i]['YCEN'] = self.headers[i]['YCENIX'] # this is not modified in IDL!
            self.headers[i]['CRVAL2'] = self.headers[i]['YCENIX'] # this is not modified in IDL!
                
            # set EXPTIME = EXPTIMEF in FUV and EXPTIME = EXPTIMEN in NUV (this is not modified in IDL!)
            waveband = self.headers[i]['TDET'+str(self._selected_ext)][0]
            self.headers[i]['EXPTIME'] = self.headers[i]['EXPTIME'+waveband]

        
    # function to convert pixels to coordinates (wrapper for wcs)
    def pix2coords( self, step, pixel_coordinates ):
        """
        Returns wavelength in Angstrom / solar y coordinates for the list of given pixel coordinates.
        
        **Caution**: This function takes pixel coordinates in the form [x,y] while
        images come as [y,x]
        
        Parameters
        ----------
        step : int
            The time step in the raster to get the coordinates for. 
        pixel_coordinates : np.array
            Numpy array with shape (pixel_pairs,2) that contains pixel coordinates
            in the format [x,y]
            
        Returns
        -------
        float
            Numpy array with shape (pixel_pairs,2) containing wavelength in angstrom / solar y coordinate
        """

        conversion = [co.UNIT_M_NM, co.UNIT_DEC_ARCSEC]
        return co.pix2coords( self._wcs, step, pixel_coordinates, conversion, xmin=self._xmin, ymin=self._ymin )

    
    # function to convert coordinates to pixels (wrapper for wcs)
    def coords2pix( self, step, wl_solar_coordinates, round_pixels=True ):
        """
        Returns pixel coordinates for the list of given wavelength in angstrom / solar y coordinates.
        
        Parameters
        ----------
        step : int
            The time step in the SJI to get the pixel coordinates for. 
        wl_solar_coordinates : np.array
            Numpy array with shape (coordinate_pairs,2) that contains wavelength in 
            angstrom / solar y coordinates in the form [lat/lon] in units of arcseconds
            
        Returns
        -------
        float
            Numpy array with shape (coordinate_pairs,2) containing pixel coordinates
        """
        
        conversion = [co.UNIT_M_NM, co.UNIT_DEC_ARCSEC]
        return co.coords2pix( self._wcs, step, wl_solar_coordinates, conversion, round_pixels=round_pixels, xmin=self._xmin, ymin=self._ymin )

        
    # function to get axis coordinates for a particular image
    def get_axis_coordinates( self, step ):
        """
        Returns coordinates for the image at the given time step.
        
        Parameters
        ----------
        step : int
            The time step in the SJI to get the coordinates for.

        Returns
        -------
        float
            List [coordinates along x axis, coordinates along y axis]
        """

        conversion = [co.UNIT_M_NM, co.UNIT_DEC_ARCSEC]
        return co.get_axis_coordinates( self._wcs, step, self.shape, conversion, self._xmin, self._xmax, self._ymin, self._ymax )
        
        
    # function to get interpolated image step
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
        
        from irisreader.preprocessing import spectrum_interpolator
        interpolator = spectrum_interpolator( lambda_min, lambda_max, n_breaks )
        lambda_units = self.get_axis_coordinates( step )[0]
        return interpolator.fit_transform( self.get_image_step( step ), lambda_units )
        
    # function to plot an image step
    def plot( self, step, y=None, units='pixels', gamma=None, cutoff_percentile=99.9 ):
        """Plots the raster spectrum at time step <step> and possible slit position <y>. 
        
        Parameters
        ----------
        step : int
            The time step in the raster.
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

        # if gamma is not specified, use gamma=1 for SJI_2832 and gamma=0.4 for everything else
        if gamma is None:
           gamma = 0.4

        # load image into memory and exponentiate it with power
        image = self.get_image_step( step, divide_by_exptime=True ).clip( min=0 ) ** gamma
        vmax = np.percentile( image, cutoff_percentile )

        # set image extent and labels according to choice of units
        ax = plt.subplot(111)
        
        if units == 'coordinates':
            units = self.get_axis_coordinates( step=step )
            extent = [ units[0][0], units[0][-1], units[1][0], units[1][-1]  ]
            ax.set_xlabel( r'$\lambda$ [$\AA$]' )
            ax.set_ylabel("solar y [arcsec]")            

        elif units == 'pixels':
            extent = [ 0, image.shape[1], 0, image.shape[0] ]
            ax.set_xlabel("camera x")
            ax.set_ylabel("camera y")
        else:
            raise ValueError( "Plot units '" + units + "' not defined!" )

        # set title
        ax.set_title( self.line_specific_headers['WAVENAME'] + "\n" + self.time_specific_headers[step]['DATE_OBS'] )        

        # show image
        if y is None:
            ax.imshow( image, cmap='gist_heat', origin='lower', vmax=vmax, extent=extent )

        else:
            ax.set_ylabel("photon count / s (y=" + str(y) + ")")
            ax.plot( extent[0]+np.linspace(0, extent[1]-extent[0], image.shape[1]), image[y,:] )
            
        ax.set_aspect('auto')

        plt.show()
        
        # delete image variable (otherwise memory mapping keeps file open)
        del image        
        
# remove this
if __name__ == "__main__":
    raster = raster_cube( "/home/chuwyler/Desktop/FITS/20140910_112825_3860259453/iris_l2_20140910_112825_3860259453_raster_t000_r00000.fits", line="Mg" )

