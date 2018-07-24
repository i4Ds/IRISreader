#!/usr/bin/env python3

from irisreader.utils.date import from_Tformat
import numpy as np

# line window identifiers
SJI_LINE_WINDOWS = ['C II 1330', 'Mg II h/k 2796', 'Mg II wing 2832', 'Si IV 1400']
RASTER_LINE_WINDOWS = ['1343', '2786', '2787', '2814', '2826', '2830', '2831', '2832', '2833', 'C I 1354', 'C II 1336', 
                'Cl I 1352', 'Fe XII 1349', 'Mg II h 2803', 'Mg II k 2796', 'O I 1356', 'Si IV 1394', 'Si IV 1403']


# function to get unique identifiers for the images
def unique_identifiers( fits_object ):
    """
    Creates unique identifiers for the images in the data cube that can be 
    used to refer to an image in a proper, robust way.
    
    Format: tllyyyyMMddhhmmssfff
    
    t: type of the FITS file (1: sji, 2: raster)
    ll: line window id
    yyyy: year
    MM: month
    dd: day
    hh: hour
    mm: minute
    ss: seconds
    fff: milliseconds
    
    SJI line window ids:
    0        C II 1330
    1   Mg II h/k 2796
    2  Mg II wing 2832
    3       Si IV 1400
    
    raster line window ids:
    0           1343
    1           2786
    2           2787
    3           2814
    4           2826
    5           2830
    6           2831
    7           2832
    8           2833
    9       C I 1354
    10     C II 1336
    11     Cl I 1352
    12   Fe XII 1349
    13  Mg II h 2803
    14  Mg II k 2796
    15      O I 1356
    16    Si IV 1394
    17    Si IV 1403
    
    """
    ids = []
    dates = [from_Tformat( h['DATE_OBS'] ) for h in fits_object.time_specific_headers]

    for d in dates:      
        if fits_object.type == 'sji':
            line_id = SJI_LINE_WINDOWS.index( fits_object.line_info ) if fits_object.line_info in SJI_LINE_WINDOWS else 0
            fits_type = 1
        else: 
            fits_type = 2
            line_id = RASTER_LINE_WINDOWS.index( fits_object.line_info ) if fits_object.line_info in RASTER_LINE_WINDOWS else 0

        millisec = "{:06d}".format( d.microsecond )[:-3]
        
        ids.append( "{}{:02d}{}{:02d}{:02d}{:02d}{:02d}{:02d}{}".format( fits_type, line_id, d.year, d.month, d.day, d.hour, d.minute, d.second, millisec ) )
        
        assert( np.all( np.array( list( map( len, np.array( ids ) ) ) ) == 20 ) )
    return ids