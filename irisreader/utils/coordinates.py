#!/usr/bin/env python3

import warnings
import numpy as np
from astropy.wcs import WCS
import matplotlib.pyplot as plt

# some unit conversions
UNIT_M_NM = 1e10
UNIT_DEC_ARCSEC = 3600
XLABEL_ARCSEC = "solar x [arcsec]"
YLABEL_ARCSEC = "solar y [arcsec]"
XLABEL_ANGSTROM = r'$\lambda$ [$\AA$]'



# an adapter for coordinate transform when working in a WCS projection with matplotlib
def _ArcsecTransformAdapter( transformer ):
    
    # change points from arcseconds to degrees
    transformer.transform_non_affine_deg = transformer.transform_non_affine
    transformer.transform_non_affine = lambda x: transformer.transform_non_affine_deg( np.array(x)/3600 )
    transformer.transform_path_non_affine_deg = transformer.transform_path_non_affine
    
    # change path vertices from arcseconds to degrees
    def my_transform_path_non_affine( path ):
        path.vertices /= 3600
        return transformer.transform_path_non_affine_deg( path )
    transformer.transform_path_non_affine = my_transform_path_non_affine 
    
    return transformer

def get_ax_transform():
    """
    Get the necessary coordinate transformer when plotting in WCS projected world coordinates.
    
    Usage:
    sji.plot( 0, units="coordinates" )
    """
    return _ArcsecTransformAdapter( plt.gca().get_transform('world') )



class iris_coordinates:
    """
    A class that allows to convert pixels into coordinates and vice versa.
    Works both for spectra and rasters and makes heavy use of astropy.wcs.
    
    Warning: the functions in this file underwent basic tests, but more rigorous
    tests have to performed before this class can be fully trusted.
    
    Parameters
    ----------
    header : 
        astropy HDUList header directly from FITS extension
    mode:
        whether to work in SJI ('sji') or raster ('raster') mode
    """
    
    def __init__( self, header, mode ):
                
        # initialize astropy WCS object and suppress warnings
        # set CDELTi to a tiny value if zero (otherwise wcs produces singular PC matrix)
        # see e.g. discussion at https://github.com/sunpy/irispy/issues/78
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if header['CDELT1'] == 0:
                header['CDELT1'] = 1e-10
            if header['CDELT2'] == 0:
                header['CDELT2'] = 1e-10
            if header['CDELT3'] == 0:
                header['CDELT3'] = 1e-10            
                
            self.wcs = WCS( header )
            
            if header['CDELT1'] == 1e-10:
                header['CDELT1'] = 0
            if header['CDELT2'] == 1e-10:
                header['CDELT2'] = 0
            if header['CDELT3'] == 1e-10:
                header['CDELT3'] = 0 
            
        # set mode (sji or raster) and appropriate conversions and labels
        if mode == 'sji':
            self.conversion_factor = [UNIT_DEC_ARCSEC, UNIT_DEC_ARCSEC]
            self.xlabel = XLABEL_ARCSEC
            self.ylabel = YLABEL_ARCSEC
        elif mode == 'raster':
            self.conversion_factor = [UNIT_M_NM, UNIT_DEC_ARCSEC]
            self.xlabel = XLABEL_ANGSTROM
            self.ylabel = YLABEL_ARCSEC
        else:
            raise ValueError( "mode should be either 'sji' or 'raster'" )
        
        self.mode = mode
        
        # initialize bounds
        self.xmin, self.xmax, self.ymin, self.ymax = None, None, None, None
        self.cropped = False
        
    # function to set bounds
    def set_bounds( self, bounds ):
        """
        Set bounds on the image found e.g. by cropping procedure.
        This is important for pixel to coordinates conversion.
        
        Parameters
        ----------
        bounds : list
            List with Bounds [xmin, xmax, ymin, ymax]
        """
        
        self.cropped = True
        self.xmin, self.xmax, self.ymin, self.ymax = bounds
        
    # function to reset bounds
    def reset_bounds( self ):
        """
        Resets all the bounds that have previously been set.
        """
        self.cropped = False
        self.xmin, self.xmax, self.ymin, self.ymax = None, None, None, None
    

    def pix2coords( self, timestep, pixel_coordinates ):
        """
        Function to convert from camera (pixel) coordinates to solar/physical coordinates.
        Makes heavy use of astropy.wcs.
        
        Parameters
        ----------
        timestep : int
            time step in the image cube
        pixel_coordinates : np.array
            numpy array with x and y coordinates
            
        Returns
        -------
        np.array :
            Tuple of solar x and y coordinates in Arcsec (SJI) or wavelength and solar y coordinates (raster) in Arcsec / Angstrom.
        """
        
        # make sure pixel_coordinates is a numpy array
        pixel_coordinates = np.array( pixel_coordinates )
    
        # check dimensions
        ndim = pixel_coordinates.ndim
        shape = pixel_coordinates.shape
        if not ( (ndim == 1 and shape[0] == 2) or (ndim == 2 and shape[1] == 2) ):
            raise ValueError( "pixel_coordinates should be a numpy array with shape (:,2)." ) 
        
        # create a copy of the input coordinates
        pixel_coordinates = pixel_coordinates.copy()
        
        # generalize for single pixel pairs
        if ndim == 1:
            pixel_coordinates = np.array([pixel_coordinates])
            
        # add offset if image is cropped
        if self.cropped:
            pixel_coordinates += np.array([self.xmin, self.ymin])            
        
        # stack timestep to pixels
        pixel_coordinates = np.hstack( [ pixel_coordinates, pixel_coordinates.shape[0]*[[timestep]] ] )
         
        # transform pixels to solar coordinates
        solar_coordinates = self.wcs.all_pix2world( pixel_coordinates, 1 )[:,:2]  
        
        # convert units
        solar_coordinates *= self.conversion_factor
        
        # return tuple if input was only one tuple
        if ndim == 1:
            return solar_coordinates[0]
        else:
            return solar_coordinates
            
    def coords2pix( self, timestep, solar_coordinates, round_pixels=True ):
        """
        Function to convert from solar/physical coordinates to camera (pixel) coordinates.
        Makes heavy use of astropy.wcs.
            
        Parameters
        ----------
        timestep : int
            time step in the image cube
        solar_coordinates : np.array
            numpy array with solar coordinates (x,y) (SJI) or solar/wavelength coordinates (lambda,y) (raster) 
            
        Returns
        -------
        np.array :
            Tuple (x,y) of camera coordinates in pixels
        """
        
        # make sure solar_coordinates is a numpy array
        solar_coordinates = np.array( solar_coordinates )
    
        # check dimensions
        ndim = solar_coordinates.ndim
        shape = solar_coordinates.shape
        if not ( (ndim == 1 and shape[0] == 2) or (ndim == 2 and shape[1] == 2) ):
            raise ValueError( "pixel_coordinates should be a numpy array with shape (:,2)." ) 
        
        # create a copy of the input coordinates
        solar_coordinates = solar_coordinates.copy()
        
        # generalize for single pixel pairs
        if ndim == 1:
            solar_coordinates = np.array([solar_coordinates])

        # convert units
        solar_coordinates = solar_coordinates / self.conversion_factor
                
        # convert timestep to time coordinate (want always to reference time with timestep)
        time_coordinate = self.wcs.all_pix2world( [[0,0,timestep]], 1  )[0, 2]

        # stack timestep to pixels
        solar_coordinates = np.hstack( [ solar_coordinates, solar_coordinates.shape[0]*[[time_coordinate]] ] )
         
        # transform solar coordinates to pixels
        pixel_coordinates = self.wcs.all_world2pix( solar_coordinates, 1 )[:,:2]  
        
        # subtract offset if image is cropped
        if self.cropped:
            pixel_coordinates -= np.array([self.xmin, self.ymin])
            
        # round to nearest pixels            
        if round_pixels:
            pixel_coordinates = np.round( pixel_coordinates ).astype( np.int )
        
        # return tuple if input was only one tuple
        if ndim == 1:
            return pixel_coordinates[0]
        else:
            return pixel_coordinates
                    
    def get_axis_coordinates( self, step, shape ):
        """
        Get axis coordinates for a particular image.
        
        Parameters
        ----------
        step : int
            Time step in the data cube.
        shape : tuple
            Shape of 3D data cube
        
        Returns
        -------
        list :
            List containing the coordinates along the x and y axis.
        """
        
        # create input for wcs.all_pix2world: list of triples (x,y,t)
        # evaluated only at coordinate axes (to be fast)
        arr_x = [[x,0,step] for x in range(shape[2])]
        arr_y = [[0,y,step] for y in range(shape[1])]
            
        # pass pixel lists to wcs.all_pix2world and extract axis values
        # convert from degrees to arcseconds by multiplying with 3600
        coords_x = self.wcs.all_pix2world( arr_x, 1 )[:,0] * self.conversion_factor[0]
        coords_y = self.wcs.all_pix2world( arr_y, 1 )[:,1] * self.conversion_factor[1]
            
        # Return bounded units if image is cropped
        if self.cropped:
            return [ coords_x[self.xmin:self.xmax], coords_y[self.ymin:self.ymax] ]
        else:
            return [ coords_x, coords_y ]
        

