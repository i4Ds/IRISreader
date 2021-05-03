#!/usr/bin/env python3

"""
functions for coalignment of SJI and raster data
"""

import numpy as np
import pandas as pd
from functools import lru_cache

# internal function to sort steps of an observation in a dataframe
@lru_cache(maxsize=64)
def sort_steps( raster, sji ):
    rts = raster.get_timestamps()
    sts = sji.get_timestamps()
    df = pd.DataFrame({
        'timestamp': np.hstack([rts, sts]),
        'origin': np.hstack([['raster']*len(rts), ['sji']*len(sts)]),
        'step': np.hstack([np.arange(len(rts)), np.arange(len(sts))])
    })
    df = df.set_index('timestamp').sort_index()
    return df

@lru_cache(maxsize=64)
def find_closest_raster( raster, sji ):
    """
    Finds closest raster steps to sji steps for a given raster and sji object.
    
    Parameters
    ----------
    raster : irisreader.raster_cube
        raster_cube instance
    sji : irisreader.sji_cube
        sji_cube_instance

    Returns
    -------
    raster_steps : numpy.array
        array with closest raster steps
    """

    
    # sort steps
    df = sort_steps( raster, sji )
    
    # get available sji steps
    raster_steps = []
    
    for sji_step in range(sji.n_steps):
    
        # timestamp of sji
        sji_tstamp = df[(df.origin=='sji') & (df.step==sji_step)].index.values[0]

        # get closest rasters on both sides
        below = df[(df.origin=='raster') & (df.index<=sji_tstamp)].tail(1)
        above = df[(df.origin=='raster') & (df.index>sji_tstamp)].head(1)
        candidates = pd.concat( [below, above], axis=0 )
        
        # append closest raster step of both
        raster_steps.append( candidates.step.values[np.argmin(np.abs(candidates.index - sji_tstamp))] )
     
    return np.array(raster_steps)


@lru_cache(maxsize=64)
def find_closest_sji( raster, sji ):
    """
    Finds closest sji steps to raster steps for a given sji and raster object.
    
    Parameters
    ----------
    raster : irisreader.raster_cube
        raster_cube instance
    sji : irisreader.sji_cube
        sji_cube_instance

        
    Returns
    -------
    sji_steps : numpy.array
        array with closest sji steps
    """

    return find_closest_raster( sji, raster )
