#!/usr/bin/env python3

# This file contains date utility functions

from datetime import datetime as dt
from datetime import timedelta

T_FORMAT_MS = '%Y-%m-%dT%H:%M:%S.%f'
T_FORMAT_S = '%Y-%m-%dT%H:%M:%S'
OBS_FORMAT = '%Y%m%d_%H%M%S'


def from_Tformat( date_str ):
    """
    Docstring
    """
    try:
        date = dt.strptime( date_str , T_FORMAT_MS )
    except ValueError:
        date = dt.strptime( date_str , T_FORMAT_S )
    return date

def to_Tformat( date, milliseconds=True ):
    """
    Docstring
    """
    if milliseconds:
        date_str = dt.strftime( date, T_FORMAT_MS )[:-3]
    else: # round to seconds
        microseconds = date.microsecond / 1e6
        date_str = dt.strftime( date + timedelta( seconds=round(microseconds) ) , T_FORMAT_S )
    return date_str

def from_obsformat( full_obsid_str ):
    """
    Docstring
    """
    date_str = '_'.join( full_obsid_str.split('_')[:-1] )
    date = dt.strptime( date_str, OBS_FORMAT )
    return date

def to_epoch( date ):
    """
    Docstring
    """
    return (date - dt.utcfromtimestamp(0)).total_seconds()

