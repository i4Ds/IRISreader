#!/usr/bin/env python3

"""
raster_cube class: abstraction that makes the data, the headers and a number
of auxiliary variables available for IRIS spectrograph data
"""

import numpy as np
import matplotlib.pyplot as plt

import irisreader as ir
from irisreader import iris_data_cube
from irisreader.preprocessing import spectrum_interpolator

class raster_cube( iris_data_cube ):
    """
    This class implements an abstraction of an IRIS raster FITS file.
    
    Parameters
    ----------
    files : string
        Path or list of paths to the (sorted) IRIS FITS file(s).
    line : string
        Line to select: this can be any unique abbreviation of the line name (e.g. "Mg"). For non-unique abbreviations, an error is thrown.
    keep_null : boolean
        Controls whether images that are NULL (-200) everywhere are removed from the data cube. keep_null=True keeps NULL images and keep_null=False removes them.
        
        
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
        Endt date of the selected observation.
    mode : str
        Observation mode of the selected observation ('sit-and-stare' or 'raster').
    line_info : str
        Description of the selected line.
    n_steps : int
        Number of time steps in the data cube.
    primary_headers : dict
        Dictionary with primary headers of the FITS file (lazy loaded).
    time_specific_headers : dict
        List of dictionaries with time-specific headers of the selected line (lazy loaded).
    headers : dict
       List of combined primary and time-specific headers (lazy loaded).
    """
    
    # constructor
    def __init__( self, files, line='', keep_null=False, force_valid_steps=False ):
        
        # call constructor of parent iris_data_cube
        super().__init__( files, line=line, keep_null=keep_null, force_valid_steps=force_valid_steps )        
        
        # raise error if the data_cube is a raster
        if self.type=='sji':
            self.close()
            raise ValueError("This is a SJI file. Please use sji_cube to open it.")
            
    # return description upon a print call
    def __repr__( self ):
        return "raster {} line window:\n(n_steps, n_y, n_x) = {}".format( self.line_info, self.shape )
        
    # load some variables upon request
    def __getattribute__( self, name ):
        if name=='n_spectra':
            return self.shape[0] * self.shape[1]
        else:
            return super().__getattribute__( name ) # call method of class where we inherited from
    
    # prepare combined headers
    def _prepare_combined_headers( self ):
        """
        Prepares the combination (primary header, time-specific header, 
        line-specific header) lazily for each image.
        """
        if ir.verbosity_level >= 2: print( "[raster cube] Lazy loading combined headers" )
        headers = [ dict( list(self.primary_headers.items()) + list(self.line_specific_headers.items()) + list(t_header.items()) ) for t_header in self.time_specific_headers ]

        # Fix some headers manually
        for i in range( 0, self.n_steps ):
            headers[i]['XCEN'] = headers[i]['XCENIX'] # this is not modified in IDL!
            headers[i]['YCEN'] = headers[i]['YCENIX'] # this is not modified in IDL!
            headers[i]['CRVAL2'] = headers[i]['YCENIX'] # this is not modified in IDL!

            # set EXPTIME = EXPTIMEF in FUV and EXPTIME = EXPTIMEN in NUV (this is not modified in IDL!)
            waveband = headers[i]['TDET'+str(self._selected_ext)][0]
            headers[i]['EXPTIME'] = headers[i]['EXPTIME'+waveband]
            
        # Set class instance variable
        self.headers = headers

    # overwrite get_image_step function to be able to divide by exposure time
    # divide_by_exptime defaults to False because the exposure time has to be 
    # searched for in the time-specific headers which slows file access down.
    # Moreover, often the data are normalized anyway.
    def get_image_step( self, step, divide_by_exptime=False ):
        """
        Returns the image at position step. This function uses the section 
        routine of astropy to only return a slice of the image and avoid 
        memory problems.
        
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
            2D image at time step <step>. Format: [y,wavelength].
        """
        
        if divide_by_exptime:
            # get uv region
            uv_region = self.line_specific_headers['WAVEWIN'][0]
            
            # get exposure time stored in 'EXPTIMES'
            exptime = self.time_specific_headers[ step ]['EXPTIME'+uv_region]
            
            # divide image by exposure time
            image = super().get_image_step( step ) 
            image[image>0] /= exptime
            return image
        
        else: 
            return super().get_image_step( step )
    
    # function to get interpolated image step
    def get_interpolated_image_step( self, step, lambda_min, lambda_max, n_breaks, divide_by_exptime=False ):
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
        divide_by_exptime : bool
            Whether to divide image by its exposure time or not. Dividing by exposure
            time will present a normalized image instead of the usual data numbers.

        Returns
        -------
        numpy.ndarray
            interpolated 2D image at time step <step>. Format: [y,x] (SJI), [y,wavelength] (raster).
        """

        interpolator = spectrum_interpolator( lambda_min, lambda_max, n_breaks )
        lambda_units = self.get_axis_coordinates( step )[0]
        return interpolator.fit_transform( self.get_image_step( step, divide_by_exptime ), lambda_units )
    
    # function to get a spectrum step
    def get_spectrum( self, step, lambda_min=None, lambda_max=None, n_breaks=None, divide_by_exptime=False ):
        
        image_size = self.shape[1]
        image_step = int(step/image_size)
        y_value = step % image_size
        
        if lambda_min is not None and lambda_max is not None and n_breaks is not None:
            spectrum = self.get_interpolated_image_step( image_step, lambda_min, lambda_max, n_breaks, divide_by_exptime )[y_value,:]
        else:
            #spectrum = self.get_image_step( image_step, divide_by_exptime )[y_value,:]
            spectrum = self[ image_step, y_value, : ]
        
        return image_step, y_value, spectrum
    
    # function to plot an image step
    def plot( self, step, y=None, units='pixels', gamma=None, cutoff_percentile=99.9 ):
        """
        Plots the slit-jaw image at time step <step>. 
        
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

        # if gamma is not specified, use gamma=1 for SJI_2832 and gamma=0.4 for everything else
        if gamma is None:
            gamma = 0.4

        # load image into memory and find a good value for vmax with gamma correction
        image = self.get_image_step( step ).clip( min=0 ) 
        vmax = np.percentile( image**gamma, cutoff_percentile )
    
        # set image extent and labels according to choice of units
        ax = plt.subplot(111)
        
        if units == 'coordinates':
            units = self.get_axis_coordinates( step=step )
            extent = [ units[0][0], units[0][-1], units[1][0], units[1][-1]  ]
            ax.set_xlabel( self._ico.xlabel )
            ax.set_ylabel( self._ico.ylabel )

        elif units == 'pixels':
            extent = [ 0, image.shape[1], 0, image.shape[0] ]
            ax.set_xlabel("camera x")
            ax.set_ylabel("camera y")
            
        else:
            raise ValueError( "Plot units '" + units + "' not defined!" )
            
        # create title
        ax.set_title(self.line_info + '\n' + self.time_specific_headers[step]['DATE_OBS'] )

        # show image
        if y is None:
            ax.imshow( image**gamma, cmap='gist_heat', origin='lower', vmax=vmax, extent=extent )
        else:
            ax.set_ylabel("photons / s (y=" + str(y) + ")")
            ax.plot( extent[0]+np.linspace(0, extent[1]-extent[0], image.shape[1]), image[y,:] )
        
        # set aspect ratio depending
        ax.set_aspect('auto') 
        
        # show plot
        plt.show()
        
        # delete image variable (otherwise memory mapping keeps file open)
        del image

# Test code
if __name__ == "__main__":

    from irisreader.data.sample import sample_raster
    raster0 = sample_raster( line="Mg", keep_null=False )
    raster0.n_steps
    th = raster0.time_specific_headers # 13.4 ms
    raster0.plot(0)
    raster0.crop( check_coverage=False )
    raster0.plot(0)
    raster0.n_steps
    
    import os    
    raster_dir = "/home/chuwyler/Desktop/FITS/20140329_140938_3860258481/"
    raster_files = sorted( [raster_dir + "/" + file for file in os.listdir( raster_dir ) if 'raster' in file] )
    raster1 = raster_cube( sorted(raster_files), line="C" )
    raster1.n_steps
    th = raster1.time_specific_headers.tolist()
    raster1.plot(1300)
    raster1.crop( check_coverage=False )
    raster1.plot(0)

    # open a raster with 14 GB size    
    raster2 = raster_cube( "/home/chuwyler/Desktop/FITS/20140420_223915_3864255603/iris_l2_20140420_223915_3864255603_raster_t000_r00000.fits", line="Mg" )
    raster2.n_steps
    raster2.plot(0)
    raster2.crop()
    raster2.plot(0)

    # open a raster with 7000 files
    raster3_dir = "/home/chuwyler/Desktop/FITS/20150404_155958_3820104165"
    raster3_files = sorted( [raster3_dir + "/" + file for file in os.listdir( raster3_dir ) if 'raster' in file] )
    raster3 = raster_cube( raster3_files, line="Mg" )
    raster3.n_steps 
    raster3.plot(1000)
    raster3.crop( check_coverage=False )
    raster3.plot(1000)
    
    from tqdm import tqdm
    dn = []
    for step in tqdm( range( raster3.n_spectra ) ):
        image_step, y_value, spectrum = raster3.get_spectrum( step )
        dn.append( np.sum(spectrum) )
    