#!/usr/bin/env python3

"""
raster_cube class: abstraction that makes the data, the headers and a number
of auxiliary variables available for IRIS spectrograph data
"""

import irisreader as ir
from irisreader import iris_data_cube

DEBUG = True

class raster_cube( iris_data_cube ):
    """
    This class implements an abstraction of an IRIS raster FITS file.
    
    Parameters
    ----------
    filename : string
        Path to the IRIS SJI FITS file.
    line : string
        Line to select: this can be any unique abbreviation of the line name (e.g. "Mg"). For non-unique abbreviations, an error is thrown.
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
    def __init__( self, files, line='', keep_null=False ):
        
        # call constructor of parent iris_data_cube
        super().__init__( files, line=line, keep_null=keep_null )        
        
        # raise error if the data_cube is a raster
        if self.type=='sji':
            self.close()
            raise ValueError("This is a SJI file. Please use sji_cube to open it.")
            
    # return description upon a print call
    def __str__( self ):
        return "SJI {} line window:\n(n_steps, n_y, n_x) = {}".format( self.line_info, self.shape )

    def __repr__( self ):
        return self.__str__()
        
    # make some additional preparations for time-specific headers            
    def _prepare_time_specific_headers( self ):
        
        if DEBUG: print("DEBUG: [raster cube] Lazy loading time specific headers")

        # prepare iris_data_cube time specific headers
        super()._prepare_time_specific_headers()
    
        # make headers local to avoid recursion problems
        time_specific_headers = self.__getattribute__( "time_specific_headers" ) 
        
        # remove some headers that are not needed and fix some headers manually
        for i in range(0, self.n_steps):
            time_specific_headers[i]['DSRCRCNIX'] = time_specific_headers[i].pop('DSRCNIX') # just rename this header
            
            for key_to_remove in ['PC1_1IX', 'PC1_2IX', 'PC2_1IX', 'PC2_2IX', 'PC2_3IX', 'PC3_1IX', 'PC3_2IX', 'PC3_3IX', 'OPHASEIX', 'OBS_VRIX']:
                if key_to_remove in time_specific_headers[i].keys():
                    del time_specific_headers[i][ key_to_remove ]
                    
        self.time_specific_headers = time_specific_headers
        

if __name__ == "__main__":

    import os    
    raster_dir = "/home/chuwyler/Desktop/FITS/20140329_140938_3860258481/"
    raster_files = os.listdir( raster_dir )
    raster_files = [raster_dir + "/" + file for file in raster_files if 'raster' in file]
    raster = raster_cube( sorted(raster_files), line="Mg" )
