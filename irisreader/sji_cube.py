#!/usr/bin/env python3

"""
sji_cube class: abstraction that makes the data, the headers and a number
of auxiliary variables available for IRIS slit-jaw image data
"""

from irisreader import iris_data_cube

DEBUG = True

class sji_cube( iris_data_cube ):
    """
    This class implements an abstraction of an IRIS SJI FITS file.
    
    Parameters
    ----------
    filename : string
        Path to the IRIS SJI FITS file.
    keep_null : boolean
        Controls whether images that are NULL (-200) everywhere are removed from the data cube. keep_null=True keeps NULL images and keep_null=False removes them.
        
        
    Attributes
    ----------
    type : str
        Observation type: 'sji' or 'raster'.
    obsid : str
        Observation ID of the selected observation.
    desc : str
        Description of the selected observation.
    start_date : str
        Start date of the selected observation.
    end_date : str
        Endt date of the selected observation.
    mode : str
        Observation mode of the selected observation ('sit-and-stare' or 'raster').
    line_info : str
        Description of the selected line.
    n_steps : int
        Number of time steps in the data cube.
    primary_headers : dict
        Dictionary with primary headers of the FITS file (lazy loaded).
    time_specific_headers : dict
        List of dictionaries with time-specific headers of the selected line (lazy loaded).
    headers : dict
       List of combined primary and time-specific headers (lazy loaded).
    """


    # constructor
    def __init__( self, file, keep_null=False ):
        
        # call constructor of parent iris_data_cube
        super().__init__( file, line='', keep_null=keep_null )        
        
        # raise error if the data_cube is a raster
        if self.type=='raster':
            self.close()
            raise ValueError("This is a raster file. Please use raster_cube to open it.")
            
        # line specific headers are not required - delete instance variable
        del self.line_specific_headers
    
    # return description upon a print call
    def __str__( self ):
        return "SJI {} line window:\n(n_steps, n_y, n_x) = {}".format( self.line_info, self.shape )

    def __repr__( self ):
        return self.__str__()

    # function to prepare combined headers
    def _prepare_combined_headers( self ):
        """
        Prepares the combination (primary header, time-specific header) lazily
        for each image.
        """
        if DEBUG: print( "Lazy loading combined headers" )
        self.headers = [dict(list(self.primary_headers.items())+list(t_header.items())) for t_header in self.time_specific_headers]
        
        # manual adjustments
        for i in range(0, self.n_steps):
            self.headers[i]['XCEN'] = self.headers[i]['XCENIX']
            self.headers[i]['YCEN'] = self.headers[i]['YCENIX']
            self.headers[i]['PC1_1'] = self.headers[i]['PC1_1IX']
            self.headers[i]['PC1_2'] = self.headers[i]['PC1_2IX']
            self.headers[i]['PC2_1'] = self.headers[i]['PC2_1IX']
            self.headers[i]['PC2_2'] = self.headers[i]['PC2_2IX']
            self.headers[i]['CRVAL1'] = self.headers[i]['XCENIX']
            self.headers[i]['CRVAL2'] = self.headers[i]['YCENIX']
            self.headers[i]['EXPTIME'] = self.headers[i]['EXPTIMES']
 
        
        
        
if __name__ == "__main__":
    
    sji = sji_cube( '/home/chuwyler/Desktop/FITS/20140329_140938_3860258481/iris_l2_20140329_140938_3860258481_SJI_1400_t000.fits' )