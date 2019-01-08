#!/usr/bin/env python3

"""
functions for coalignment of SJI and raster data
"""

import numpy as np

def find_closest_sji( sji, raster, raster_step ):
    """
    Finds closest sji step to raster step <raster_step> in time.
    
    Parameters
    ----------
    sji : irisreader.sji_cube
        sji_cube_instance
    raster : irisreader.raster_cube
        raster_cube instance
    raster_step : int
        raster step
        
    Returns
    -------
    sji_step : int
        SJI step
    """
    
    # check if data cubes come from the same observation and raise exception if not
    if raster.primary_headers['STARTOBS'] != sji.primary_headers['STARTOBS']:
        raise Exception("data cubes are not from the same observation!")
    
    return np.argmin( np.abs( np.array( sji.get_timestamps() )-raster.get_timestamps()[raster_step] ) )
    
    
def find_closest_raster( raster, sji, sji_step ):
    """
    Finds closest raster step to SJI step <sji_step> in time.
    
    Parameters
    ----------
    raster : irisreader.raster_cube
        raster_cube instance
    sji : irisreader.sji_cube
        sji_cube_instance
    sji_step : int
        sji step
        
    Returns
    -------
    raster_step : int
        SJI step
    """
    
    # check if data cubes come from the same observation and raise exception if not
    if raster.primary_headers['STARTOBS'] != sji.primary_headers['STARTOBS']:
        raise Exception("data cubes are not from the same observation!")
    
    return np.argmin( np.abs( np.array( raster.get_timestamps() )-sji.get_timestamps()[sji_step] ) )
    
