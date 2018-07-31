#!/usr/bin/env python3

"""
raster_cube class: abstraction that makes the data, the headers and a number
of auxiliary variables available for IRIS spectrograph data
"""

import numpy as np
import matplotlib.pyplot as plt

from irisreader import iris_data_cube

DEBUG = True

class raster_cube( iris_data_cube ):
    """
    This class implements an abstraction of an IRIS raster FITS file.
    
    Parameters
    ----------
    filename : string
        Path to the IRIS SJI FITS file.
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
    def __init__( self, files, line='', keep_null=False ):
        
        # call constructor of parent iris_data_cube
        super().__init__( files, line=line, keep_null=keep_null )        
        
        # raise error if the data_cube is a raster
        if self.type=='sji':
            self.close()
            raise ValueError("This is a SJI file. Please use sji_cube to open it.")
            
    # return description upon a print call
    def __str__( self ):
        return "SJI {} line window:\n(n_steps, n_y, n_x) = {}".format( self.line_info, self.shape )

    def __repr__( self ):
        return self.__str__()
        
    # make some additional preparations for time-specific headers            
    def _prepare_time_specific_headers( self ):
        
        if DEBUG: print("DEBUG: [raster cube] Lazy loading time specific headers")

        # prepare iris_data_cube time specific headers
        super()._prepare_time_specific_headers()
    
        # make headers local to avoid recursion problems
        time_specific_headers = self.__getattribute__( "time_specific_headers" ) 
        
        # remove some headers that are not needed and fix some headers manually
        for i in range(0, self.n_steps):
            time_specific_headers[i]['DSRCRCNIX'] = time_specific_headers[i].pop('DSRCNIX') # just rename this header
            
            for key_to_remove in ['PC1_1IX', 'PC1_2IX', 'PC2_1IX', 'PC2_2IX', 'PC2_3IX', 'PC3_1IX', 'PC3_2IX', 'PC3_3IX', 'OPHASEIX', 'OBS_VRIX']:
                if key_to_remove in time_specific_headers[i].keys():
                    del time_specific_headers[i][ key_to_remove ]
                    
        self.time_specific_headers = time_specific_headers
     
    # prepare combined headers
    def _prepare_combined_headers( self ):
        """
        Prepares the combination (primary header, time-specific header, 
        line-specific header) lazily for each image.
        """
        if DEBUG: print( "DEBUG: [raster cube] Lazy loading combined headers" )
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
    def get_image_step( self, step, divide_by_exptime=True ):
       
        # get uv region
        uv_region = self.line_specific_headers['WAVEWIN'][0]
        
        # get exposure time stored in 'EXPTIMES'
        exptime = self.time_specific_headers[ step ]['EXPTIME'+uv_region]
        
        # divide image by exposure time
        return super().get_image_step( step ) / exptime
            
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
        image = self.get_image_step( step, divide_by_exptime=True ).clip( min=0 ) 
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
            
        # create title (TODO)
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


if __name__ == "__main__":

    import os    
    raster_dir = "/home/chuwyler/Desktop/FITS/20140329_140938_3860258481/"
    raster_files = sorted( [raster_dir + "/" + file for file in os.listdir( raster_dir ) if 'raster' in file] )
    raster = raster_cube( sorted(raster_files), line="Mg" )

    # open a raster with > 6000 files:
    raster_dir = "/home/chuwyler/Desktop/FITS/20150404_155958_3820104165"
    raster_files = sorted( [raster_dir + "/" + file for file in os.listdir( raster_dir ) if 'raster' in file] )
    many_rasters = iris_data_cube( raster_files, line="Mg" )

    # open a raster with 14 GB size    
    very_large_raster = iris_data_cube( "/home/chuwyler/Desktop/FITS/20140420_223915_3864255603/iris_l2_20140420_223915_3864255603_raster_t000_r00000.fits", line="Mg" )
