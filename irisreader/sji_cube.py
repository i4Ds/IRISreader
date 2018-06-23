#!/usr/bin/env python

# import libraries
import numpy as np
import matplotlib.pyplot as plt
from irisreader import iris_data_cube
from irisreader.config import DEBUG_LAZY_LOADING_LEVEL

# define SJI class
class sji_cube( iris_data_cube ):
    """This class implements an abstraction of an IRIS SJI FITS file on top of the
    iris_data_cube class. SJI FITS files are not very complex and therefore 
    only a few modifications on top of iris_data_cube are necessary. The headers
    are parsed in a way similar to solar soft's read_iris_l2 and data is made
    available in time-step chunks in order to avoid memory mapping.
    
    Parameters
    ----------
    filename : string
        Path to the IRIS SJI FITS file.
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
    def __init__( self, filename, keep_null=False ):
    
        # initialize constructor of iris_data_cube
        iris_data_cube.__init__( self, filename=filename, line='', keep_null=keep_null )
        
        # raise error if the data_cube is a raster
        if self.type=='raster':
            self.close()
            raise ValueError("This is a raster file. Please use raster_cube to open it.")
        
    # lazy load the combined headers
    # TODO: can this somehow be done with the function of super() ?
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
            iris_data_cube._prepare_time_specific_headers( self )
            return iris_data_cube.__getattribute__( self, "primary_headers" )     
        
        elif name=='time_specific_headers' and object.__getattribute__( self, "time_specific_headers" ) == [-1]:
            iris_data_cube._prepare_time_specific_headers( self )
            return iris_data_cube.__getattribute__( self, "time_specific_headers" ) 
            
        elif name=='headers' and object.__getattribute__( self, "headers" ) == [-1]:
            self._prepare_combined_headers()
            return object.__getattribute__( self, "headers" )
        
        else:
            return object.__getattribute__( self, name )


    # function to prepare combined headers
    def _prepare_combined_headers( self ):
        """
        Prepares the combination (primary header, time-specific header) lazily
        for each image.
        """
        if DEBUG_LAZY_LOADING_LEVEL >= 3: print( "Lazy loading combined headers" )
        self.headers = [dict(list(self.primary_headers.items())+list(t_header.items())) for t_header in self.time_specific_headers]
        
        # manual adjustments
        for i in range(0, self.n_steps):
            self.headers[i]['XCEN'] = self.headers[i]['XCENIX']
            self.headers[i]['YCEN'] = self.headers[i]['YCENIX']
            self.headers[i]['PC1_1'] = self.headers[i]['PC1_1IX']
            self.headers[i]['PC1_2'] = self.headers[i]['PC1_2IX']
            self.headers[i]['PC2_1'] = self.headers[i]['PC2_1IX']
            self.headers[i]['PC2_2'] = self.headers[i]['PC2_2IX']
            self.headers[i]['CRVAL1'] = self.headers[i]['XCENIX']
            self.headers[i]['CRVAL2'] = self.headers[i]['YCENIX']
            self.headers[i]['EXPTIME'] = self.headers[i]['EXPTIMES']            

    # function to get coordinates for a particular image
    # TODO: introduce more generic pixel2coords and coords2pixel functions
    def get_coordinates( self, step ):
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

        # see e.g. https://fits.gsfc.nasa.gov/wcs/coordinates.pdf
        # or http://www.aanda.org/articles/aa/pdf/2002/45/aah3859.pdf
        # TODO: check how satellite rotations enters with PC matrix, is this correct?
        h = self.primary_headers
        x = h['PC1_1'] * h['CRVAL1'] + h['CDELT1'] * ( np.arange( h['NAXIS1'] ) - h['CRPIX1'] )
        y = h['PC2_2'] * h['CRVAL2'] + h['CDELT2'] * ( np.arange( h['NAXIS2'] ) - h['CRPIX2'] )

        # Return bounded units if image is cropped
        if self._cropped:
            return [ x[self._xmin:self._xmax], y[self._ymin:self._ymax] ]
        else:
            return [ x, y ]

    # function to plot an image step
    def plot( self, step, units='pixels', gamma=None, cutoff_percentile=99.9 ):
        """Plots the slit-jaw image at time step <step>. 
        
        Parameters
        ----------
        step : int
            The time step in the SJI.
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
            if '2832' in self.line_info: # photospheric line
                gamma = 1
            else:
                gamma = 0.4

        # load image into memory and exponentiate it with power
        image = self.get_image_step( step, divide_by_exptime=True ).clip( min=0 ) ** gamma
        vmax = np.percentile( image, cutoff_percentile )

        # set image extent and labels according to choice of units
        if units == 'coordinates':
            units = self.get_coordinates( step=step )
            extent = [ units[0][0], units[0][-1], units[1][0], units[1][-1]  ]
            plt.xlabel("solar x [arcsec]")
            plt.ylabel("solar y [arcsec]")

        elif units == 'pixels':
            extent = [ 0, image.shape[1], 0, image.shape[0] ]
            plt.xlabel("camera x")
            plt.ylabel("camera y")
        else:
            raise ValueError( "Plot units '" + units + "' not defined!" )
            
        # create title
        plt.title(self.line_info + '\n' + self.time_specific_headers[step]['DATE_OBS'] )

        # show image
        plt.imshow( image, cmap='gist_heat', origin='lower', vmax=vmax, extent=extent )
        plt.show()
        
        # delete image variable (otherwise memory mapping keeps file open)
        del image
    