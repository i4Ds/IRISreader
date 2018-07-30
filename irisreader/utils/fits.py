#!/usr/bin/env python3

# exception class for corrupt FITS files
class CorruptFITSException( Exception ):
    pass

# function that converts wavelength string into extension number
# the image extensions are stored in extensions [1,ext-3] = [1,n_lines]
def line2extension( header, line ):
    """
    Converts wavelength string into an extension number.
    Returns -1 if the line could not be found or several lines where found.
    """

    keys = [k for k in header.keys() if k.startswith("TDESC")]
    line_descriptions = [header[k] for k in sorted(keys)]
    res = [s for s in line_descriptions if line in s]        
    if len( res ) != 1: 
        return -1
    else:
        return line_descriptions.index( res[0] ) + 1

# function to translate headers stored in a data array
def array2dict( header, data ):
    """
    Reads (key, index) pairs from the header of the extension and uses them
    to assign each row of the data array to a dictionary.
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

        

