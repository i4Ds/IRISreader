#!/usr/bin/env python

# import libraries
import pandas as pd
from irisreader import iris_data_cube, sji_cube, raster_cube

def get_lines( file_object ):
    """
    Returns the available lines in a raster or SJI file. Both filenames and
    open iris_data_cube objects are accepted.
    
    Parameters
    ----------
    file_object : string or iris_data_cube
        The function accepts either an open iris_data_cube or the path to the
        FITS file to assess the lines in the observation.
        
    Returns
    -------
    pandas.DataFrame :
        Data frame with info about available lines.
    """
    
    # check whether file_object is a filename or an already opened iris_data_cube object
    if isinstance( file_object, str ):
        fits_data = iris_data_cube( file_object )
        
    elif isinstance( file_object, iris_data_cube ) or isinstance( file_object, sji_cube ) or isinstance( file_object, raster_cube ):
        fits_data = file_object
        
    else:
        raise ValueError("Please pass a either a filename or a valid iris_data_cube object.")
    
    
    # check whether the object is a raster or SJI and extract line info
    if fits_data.type == 'sji':

        line_info = pd.DataFrame( {
                'field': ['FUV1', 'FUV2', 'NUV', 'NUV'], 
                'wavelength': [1330.0, 1400.0, 2796.0, 2832.0], 
                'description': ['C II 1330', 'Si IV 1400', 'Mg II h/k 2796', 'Mg II wing 2832']
                } )
    
        line_info = line_info[line_info.description == fits_data.line_info].reset_index( drop=True )  
        line_info = line_info[['field', 'wavelength', 'description']] # make sure line info stays in the right format
    
    elif fits_data.type == 'raster':
    
        wave_field_keys = [k for k in fits_data.primary_headers.keys() if k.startswith("TDET")]
        wave_field_values = [fits_data.primary_headers[x] for x in sorted(wave_field_keys)]
        wave_length_keys = [k for k in fits_data.primary_headers.keys() if k.startswith("TWAVE")]
        wave_length_values = [round(fits_data.primary_headers[x],1) for x in sorted(wave_length_keys)]
        wave_text_keys = [k for k in fits_data.primary_headers.keys() if k.startswith("TDESC")]
        wave_text_values = [fits_data.primary_headers[x] for x in sorted(wave_text_keys)]

        line_info = pd.DataFrame(
                {'field': wave_field_values, 'wavelength': wave_length_values, 
                 'description': wave_text_values}, 
                 columns=['field', 'wavelength', 'description']
        )
    
    # close object again if a string was passed
    if isinstance( file_object, str ):
        fits_data.close()
        
    
    return line_info

# MOVE TO TEST
if __name__ == "__main__":

    get_lines( '/home/chuwyler/Desktop/FITS/20140329_140938_3860258481/iris_l2_20140329_140938_3860258481_SJI_1400_t000.fits' )
    get_lines( "/home/chuwyler/Desktop/IRISreader/irisreader/data/IRIS_raster_test1.fits" )
