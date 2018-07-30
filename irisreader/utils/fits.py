#!/usr/bin/env python3

# exception class for corrupt FITS files
class CorruptFITSException( Exception ):
    pass

# function that converts wavelength string into extension number
def line2extension( header, line ):
    """
    Converts wavelength string into an extension number.
    Returns -1 if the line could not be found or several lines where found.
    
    Parameters
    ----------
    header : astropy.io.fits.header.Header
        Primary header of the FITS file
    line : str
        Line to select: this can be any unique abbreviation of the line name (e.g. "Mg"). For non-unique abbreviations, an error is thrown.

    Returns
    -------
    location : int
        -1 if if no or multiple matching lines are found,
        otherwise extension number is returned.
    """

    # get all headers that contain line information
    keys = [k for k in header.keys() if k.startswith("TDESC")]
    
    # make sure the line descriptions are sorted
    line_descriptions = [header[k] for k in sorted(keys)]
    
    # get all line descriptions that contain the line string
    res = [s for s in line_descriptions if line in s]       
    
    # return -1 if no or multiple matching lines are found
    if len( res ) != 1: 
        return -1
    else:
        return line_descriptions.index( res[0] ) + 1

# function to translate headers stored in a data array
def array2dict( header, data ):
    """
    Reads (key, index) pairs from the header of the extension and uses them
    to assign each row of the data array to a dictionary.
    
    Parameters
    ----------
    header : astropy.io.fits.header.Header
        Header with the keys to the data array
    data : numpy.ndarray
        Data array

    Returns
    -------
    list of header dictionaries
    """
    
    # some headers are not keys but real headers: remove them
    keys_to_remove=['XTENSION', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'PCOUNT', 'GCOUNT']
    header_keys = dict( header )
    header_keys = {k: v for k, v in header_keys.items() if k not in keys_to_remove}

    # initialize dictionary list
    res = [dict() for x in range( data.shape[0] )]

    # fill dictionaries
    for i in range(0, data.shape[0]):
        res[i] = dict( zip( header_keys.keys(), data[i,list(header_keys.values())] ) )

    return res

        

