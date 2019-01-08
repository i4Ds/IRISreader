#!/usr/bin/env python3

# This file contains date utility functions

from datetime import datetime as dt
from datetime import timedelta

T_FORMAT_MS = '%Y-%m-%dT%H:%M:%S.%f'
T_FORMAT_S = '%Y-%m-%dT%H:%M:%S'
OBS_FORMAT = '%Y%m%d_%H%M%S'


def from_Tformat( date_str ):
    """
    Converts from the FITS date format '%Y-%m-%dT%H:%M:%S.%f' to a datetime object.
    
    Parameters
    ----------
    date_str : str
        FITS date string with 'T' between date and time.
    
    Returns
    -------
    datetime :
        Python datetime object
    """
    try:
        date = dt.strptime( date_str , T_FORMAT_MS )
    except ValueError:
        date = dt.strptime( date_str , T_FORMAT_S )
    return date

def to_Tformat( date, milliseconds=True ):
    """
    Converts from a datetime object to the FITS date format '%Y-%m-%dT%H:%M:%S'.
    
    Parameters
    ----------
    date : datetime
        Python datetime object
    milliseconds : bool
        Whether to include milliseconds in the output (separated with a dot)
    
    Returns
    -------
    date_str : str
        FITS date string with 'T' between date and time.
    """
    if milliseconds:
        date_str = dt.strftime( date, T_FORMAT_MS )[:-3]
    else: # round to seconds
        microseconds = date.microsecond / 1e6
        date_str = dt.strftime( date + timedelta( seconds=round(microseconds) ) , T_FORMAT_S )
    return date_str

def from_obsformat( full_obsid_str ):
    """
    Converts a full OBSID string to a date.
    
    Parameters
    ----------
    full_obsid_str : str
        Full OBSID
    
    Returns
    -------
    datetime :
        Python datetime object
    """
    date_str = '_'.join( full_obsid_str.split('_')[:-1] )
    date = dt.strptime( date_str, OBS_FORMAT )
    return date

def to_epoch( date ):
    """
    Converts a date to an integer with the number of seconds since 1.1.1970.
    This can be useful for time difference calculations.
    
    Parameters
    ----------
    date : datetime
        Python datetime object
        
    Returns
    -------
    int :
        Seconds since 1.1.1970 00:00:00
    """
    return (date - dt.utcfromtimestamp(0)).total_seconds()

