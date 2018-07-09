#!/usr/bin/env python3

# This file contains coordinate conversion functions

import numpy as np

# some unit conversions
UNIT_M_NM = 1e10
UNIT_DEC_ARCSEC = 3600

# function to convert from camera (pixel) coordinates to solar/physical coordinates
# wraps astropy.wcs
def pix2coords( wcs_object, timestep, pixel_coordinates, conversion, xmin=None, ymin=None ):
    
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
        if not (xmin is None or ymin is None):
            pixel_coordinates += np.array([xmin, ymin])            
        
        # stack timestep to pixels
        pixel_coordinates = np.hstack( [ pixel_coordinates, pixel_coordinates.shape[0]*[[timestep]] ] )
         
        # transform pixels to solar coordinates
        solar_coordinates = wcs_object.all_pix2world( pixel_coordinates, 1 )[:,:2]  
        
        # convert units
        solar_coordinates *= conversion
        
        # return tuple if input was only one tuple
        if ndim == 1:
            return solar_coordinates[0]
        else:
            return solar_coordinates
        
# function to convert from solar/physical coordinates to camera (pixel) coordinates
# wraps astropy.wcs
def coords2pix( wcs_object, timestep, solar_coordinates, conversion, round_pixels=True, xmin=None, ymin=None ):
    
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
        solar_coordinates = solar_coordinates / conversion
                
        # convert timestep to time coordinate (want always to reference time with timestep)
        time_coordinate = wcs_object.all_pix2world( [[0,0,timestep]], 1  )[0, 2]

        # stack timestep to pixels
        solar_coordinates = np.hstack( [ solar_coordinates, solar_coordinates.shape[0]*[[time_coordinate]] ] )
         
        # transform solar coordinates to pixels
        pixel_coordinates = wcs_object.all_world2pix( solar_coordinates, 1 )[:,:2]  
        
        # subtract offset if image is cropped
        if not (xmin is None or ymin is None):
            pixel_coordinates -= np.array([xmin, ymin])
            
        # round to nearest pixels            
        if round_pixels:
            pixel_coordinates = np.round( pixel_coordinates ).astype( np.int )
        
        # return tuple if input was only one tuple
        if ndim == 1:
            return pixel_coordinates[0]
        else:
            return pixel_coordinates
                
# function to get axis coordinates for a particular image
def get_axis_coordinates( wcs_object, step, shape, conversion, xmin=None, xmax=None, ymin=None, ymax=None ):
    
    # create input for wcs.all_pix2world: list of triples (x,y,t)
    # evaluated only at coordinate axes (to be fast)
    arr_x = [[x,0,step] for x in range(shape[2])]
    arr_y = [[0,y,step] for y in range(shape[1])]
        
    # pass pixel lists to wcs.all_pix2world and extract axis values
    # convert from degrees to arcseconds by multiplying with 3600
    coords_x = wcs_object.all_pix2world( arr_x, 1 )[:,0] * conversion[0]
    coords_y = wcs_object.all_pix2world( arr_y, 1 )[:,1] * conversion[1]
        
    # Return bounded units if image is cropped
    if not (xmin is None or ymin is None):
        return [ coords_x[xmin:xmax], coords_y[ymin:ymax] ]
    else:
        return [ coords_x, coords_y ]    

# Tests: should be sent to unit testing
if __name__ == "__main__":
    from irisreader import observation
    obs = observation("/home/chuwyler/Desktop/FITS/20140910_112825_3860259453/")
    obs.sji[0].plot( 0, units="coordinates" )
    obs.raster["Mg"].plot( 0 )
    obs.raster["Mg"].plot( 0, units="coordinates" )   
    
    # SJI tests:
    conversion = [UNIT_DEC_ARCSEC,UNIT_DEC_ARCSEC]
    shape = obs.sji[0].shape
    xcen = obs.sji[0].primary_headers['XCEN']
    ycen = obs.sji[0].primary_headers['YCEN']

    # back and forth / forth and back
    coords2pix( obs.sji[0]._wcs, 0, pix2coords( obs.sji[0]._wcs, 0, np.array([0,0]), conversion ), conversion ) == np.array([0,0])        
    coords2pix( obs.sji[0]._wcs, 0, pix2coords( obs.sji[0]._wcs, 0, np.array([shape[2],shape[1]]), conversion ), conversion ) == np.array([shape[2],shape[1]])        
    np.linalg.norm( pix2coords( obs.sji[0]._wcs, 0, coords2pix( obs.sji[0]._wcs, 0, np.array([xcen,ycen]), conversion, round_pixels=False ), conversion ) - np.array([xcen,ycen]) ) < 1e10       
    
    # crop
    obs.sji[0].crop()
    coords2pix( obs.sji[0]._wcs, 0, pix2coords( obs.sji[0]._wcs, 0, np.array([0,0]), conversion, xmin=obs.sji[0]._xmin, ymin=obs.sji[0]._ymin ), conversion, xmin=obs.sji[0]._xmin, ymin=obs.sji[0]._ymin )  == np.array([0,0])
    
    # raster tests:
    conversion = [UNIT_M_NM, UNIT_DEC_ARCSEC]
    shape = obs.raster("Mg").shape
    xcen = obs.raster("Mg").primary_headers['XCEN']
    ycen = obs.raster("Mg").primary_headers['YCEN']

    # back and forth / forth and back
    coords2pix( obs.raster["Mg"]._wcs, 0, pix2coords( obs.raster["Mg"]._wcs, 0, np.array([0,0]), conversion ), conversion ) == np.array([0,0])
    coords2pix( obs.raster["Mg"]._wcs, 0, pix2coords( obs.raster["Mg"]._wcs, 0, np.array([shape[2],shape[1]]), conversion ), conversion ) == np.array([shape[2],shape[1]])
    np.linalg.norm( pix2coords( obs.raster("Mg")._wcs, 0, coords2pix( obs.raster("Mg")._wcs, 0, np.array([xcen,ycen]), conversion, round_pixels=False ), conversion ) - np.array([xcen,ycen]) ) < 1e10       

    # crop
    obs.raster("Mg").crop()
    coords2pix( obs.raster("Mg")._wcs, 0, pix2coords( obs.raster("Mg")._wcs, 0, np.array([0,0]), conversion, xmin=obs.raster("Mg")._xmin, ymin=obs.raster("Mg")._ymin ), conversion, xmin=obs.raster("Mg")._xmin, ymin=obs.raster("Mg")._ymin )  == np.array([0,0])
    
    
    
    # get axis
    obs.sji[0].plot(0, units="coordinates")
    axes_coords = get_axis_coordinates( obs.sji[0]._wcs, 0, obs.sji[0].shape, [UNIT_DEC_ARCSEC, UNIT_DEC_ARCSEC] )    
    [ np.min(axes_coords[0]), np.max(axes_coords[0]) ]
    [ np.min(axes_coords[1]), np.max(axes_coords[1]) ]

    obs.raster["Mg"].plot(0, units="coordinates")
    axes_coords = get_axis_coordinates( obs.raster["Mg"]._wcs, 0, obs.raster["Mg"].shape, [UNIT_M_NM, UNIT_DEC_ARCSEC] )    
    [ np.min(axes_coords[0]), np.max(axes_coords[0]) ]
    [ np.min(axes_coords[1]), np.max(axes_coords[1]) ]

