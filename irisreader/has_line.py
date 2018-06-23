#!/usr/bin/env python

# import libraries
import warnings
from irisreader import get_lines

__all__ = ['has_line']

# define available lines in the IRIS line list
sji_linelist = ['C II 1330', 'Si IV 1400', 'Mg II wing 2832', 'Mg II h/k 2796']
raster_linelist = ['Si IV 1394', 'Si IV 1403', 'C II 1336', 'Fe XII 1349', 
                   'Cl I 1352', 'Mg II k 2796', 'O I 1356', '1343', '2786',
                   '2814', '2826', '2830' '2832' ]

# function to return the extension of a line description
def find_line( line_info, description ):
    """
    Returns the position of the line matching the supplied description using
    the given line_info data frame. If no line is found, -1 is returned, if
    multiple lines match the description, an error is thrown.
    
    Parameters
    ----------
    
    line_info : string
        line info data frame from get_lines() function.
    description : string
        Any abbreviation of the line description to look for.
        
        
    Returns
    -------
    
    integer :
        If -1 is returned, no matching line has been found. Otherwise a positive
        integer indicating the position in the line_info data frame is returned.
    """
    
    
    descriptions = line_info['description'].tolist()
    res = [s for s in descriptions if description in s] 
    
    if len( res ) == 0: # no matching line found
        return -1
    elif len( res ) > 1: # multiple matching lines found
        raise ValueError("Multiple lines match this description!")
    else:
        # check whether this line is ambiguous in the whole IRIS linelist
        if res[0] in sji_linelist:
            linelist_res = [s for s in sji_linelist if description in s] 
        else:
            linelist_res = [s for s in raster_linelist if description in s] 
        
        if len(linelist_res) > 1:
            warnings.warn("This line description has multiple matches in the IRIS line list, you might run into problems when using it blindly.")
            
        return descriptions.index( res[0] )

def has_line( file_object, description ):
    """
    Returns True if the supplied raster or SJI contains the line in question 
    and False if not. If the line is ambiguously specified, an error will be
    raised. Both filenames and open iris_data_cube objects are accepted.
    
    Parameters
    ----------
    
    file_object : string or iris_data_cube
        The function accepts either an open iris_data_cube or the path to the
        FITS file to assess the lines in the observation.
    
    description : string
         Any abbreviation of the line description to look for.
         
    
    Returns
    -------
    
    boolean :
        True / False
        
    """

    # get line position using find_line and return False if result is -1 and
    # True otherwise    
    return find_line( get_lines( file_object ), description ) != -1
    