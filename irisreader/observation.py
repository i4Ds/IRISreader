#!/usr/bin/env python

# TODO: should also work when all SJI files are corrupt.

# import libraries
import os
import pandas as pd
import warnings
from irisreader import sji_cube, raster_cube, combined_raster, get_lines
from irisreader.has_line import find_line
from irisreader.coalignment import goes_data, hek_data
from irisreader.config import DEBUG_LAZY_LOADING_LEVEL

__all__ = ['observation']

class sji_loader:
    """
    Loads all supplied SJI FITS files and presents two different interfaces to the available lines (that are only loaded lazily):
    
        - **call interface**: sji_loader( text ) returns the :py:class:`sji_cube` whose line description in `text` matches an available line.
        - **list interface**: sji_loader[i] returns the :py:class:`sji_cube` lines in the order they were read from the filesystem.
          
    Parameters
    ----------
    sji_files : str
        list of SJI FITS file paths.
    keep_null : bool
        Controls whether images that are NULL (-200) everywhere are removed from the data cube. keep_null=True keeps NULL images and keep_null=False removes them.
    """
    
    def __init__( self, sji_files, keep_null=False ):
        
        # open all files that can be opened
        self._sji_data = []
        for file in sji_files:
            try:
                self._sji_data.append( sji_cube( file, keep_null=keep_null ) )
            except Exception as e:
                warnings.warn( "Skipping " + file + ": " + str(e) )
                        
        # get line information
        if len(self._sji_data) > 0:
            self._line_info = pd.concat( list( map( get_lines, self._sji_data ) ) ).reset_index( drop=True )
        else:
            raise Exception( "No SJI data for this observation." )
        
    def _close( self ):
        """Function to close all files"""
        for sji in self._sji_data:
            sji.close()
    
    def __getitem__( self, i ):
        """Caller to (lazily) behave like a list"""
        return self._sji_data[i]
    
    def __len__( self ):
        """Returns number of items"""
        return len( self._sji_data )
            
    def __call__( self, text ):
        """Caller to (lazily) behave like a function"""
        line = find_line( self._line_info, text )
        if line < 0:
            raise ValueError("The desired spectral window could not be found!")
        else:
            return self._sji_data[line]
        
    def has_line( self, description ):
        """
        Finds whether or not a given line is present in the loader.
    
        Parameters
        ----------
        description : str
            Line description - if specified ambiguously, an exception will be thrown.
        
        Returns
        -------
        bool
             True if supplied line description is available in the list of SJIs and False otherwise.
        """
        return find_line( self.get_lines(), description ) != -1
        
    def get_lines( self ):
        """
        Get the list of lines in the loader.
        
        Returns
        -------
        pandas.DataFrame
            Data frame with information about available lines.
        """
        return self._line_info
    

class raster_loader:
    """
    Loads all supplied raster FITS files and presents two different interfaces to the available lines (that are only loaded lazily):
    
        - **call interface**: sji_loader( text ) returns the :py:class:`sji_cube` whose line description in `text` matches an available line.
        - **list interface**: sji_loader[i] returns the :py:class:`sji_cube` lines in the order they were read from the filesystem.
    
        
    Parameters
    ----------
    raster_files : string
        list of SJI FITS file paths.
    keep_null : boolean
        Controls whether images that are NULL (-200) everywhere are removed from the data cube. keep_null=True keeps NULL images and keep_null=False removes them.
    """
    
    def __init__( self, raster_files, keep_null=False ):
        
        # store parameters
        self._raster_files = raster_files
        self._keep_null = keep_null
        
        # open first raster
        self._first_raster = raster_cube( raster_files[0], keep_null=keep_null )
        
        # set line info
        self._line_info = get_lines( self._first_raster )
        
        # close first raster as it is not needed anymore
        self._first_raster.close()
        
        # raster data will be lazy loaded for each line
        self._raster_data = [[]] * len( self._line_info )
        
    def _load( self, i ):
        """Function to lazy load the combined raster for the selected line"""
        if DEBUG_LAZY_LOADING_LEVEL >= 1: print("DEBUG: [observation] Lazy loading combined raster")
        self._raster_data[i] = combined_raster( self._raster_files, line=self._line_info['description'][i], keep_null=self._keep_null )
        
    def _close( self ):
        """Function to close all open files"""
        for raster in self._raster_data:
            if raster != []:
                raster.close()
           
    def __getitem__( self, i ):
        """Caller to (lazily) behave like a list"""
        if self._raster_data[i] == []:
            self._load(i)
        return self._raster_data[i]
    
    def __len__( self ):
        """Returns number of items"""
        return len( self._raster_data )
    
    def __call__( self, line ):
        """Caller to (lazily) behave like a function"""
        line = find_line( self._line_info, line )
        if line < 0:
            raise ValueError("The desired spectral window could not be found!")
        if self._raster_data[line] == []:
            self._load( line )
        return self._raster_data[line]
    
    def has_line( self, description ):
        """
        Finds whether or not a given line is present in the loader.
    
        Parameters
        ----------
        description : str
            Line description - if specified ambiguously, an exception will be thrown.
        
        Returns
        -------
        bool
             True if supplied line description is available in the list of rasters and False otherwise.
        """
        return find_line( self.get_lines(), description ) != -1
    
    def get_lines( self ):
        """
        Get the list of lines in the loader.
        
        Returns
        -------
        pandas.DataFrame
            Data frame with information about available lines.
        """
        return self._line_info

class observation:    
    """
    Presents an abstract representation of a whole observation. This class
    opens all the SJI and raster files associated to an observation (in a given
    directory, as is the structure of IRIS data), possibly combines multiple
    raster to a combined_raster structure and sets a few observation parameters.
    
    Parameters
    ----------
    path : string
        Path to the IRIS observation directory where the FITS files are stored.
    keep_null : boolean
        Controls whether images that are NULL (-200) everywhere are removed from the data cube. keep_null=True keeps NULL images and keep_null=False removes them.
        
    Attributes
    ----------    
    sji : sji_loader
        :py:class:`sji_loader` instance that holds the sji attributes.
    raster : raster_loader
        :py:class:`raster_loader` instance that holds the raster attributes.
    n_raster : integer
        Number of individual raster files in the selected observation.
    n_sji : integer
        Number of individual sji files in the selected observation.
    obsid : string
        Observation ID of the selected observation.
    desc : string
        Description of the selected observation.
    date : string
        Date of the selected observation.
    mode : string
        Observation mode of the selected observation ('sit-and-stare' or 'raster').
    
    """
    
    def __init__( self, path, keep_null=False ):
        
        # find files in directory
        self._path = path
        self._sji_files = self._get_files( path, type='sji' )
        self._raster_files = self._get_files( path, type='raster' )
        self.n_raster = len( self._raster_files ) # remove this?
        self.n_sji = len( self._sji_files )
    
        # create the sji and raster loaders
        if len( self._sji_files ) > 0:
            self.sji = sji_loader( self._sji_files, keep_null )
        else:
            self.sji = None
            
        if len( self._raster_files ) > 0:
            self.raster = raster_loader( self._raster_files, keep_null )
        else:
            self.raster = None
        
        # Raise an error if no data files are present
        if self.sji is None and self.raster is None:
            raise ValueError("This directory contains no data.")
        
        # Issue a warning if SJI or rasters are missing
        if self.sji is None:
            warnings.warn("No SJI files in this observation.")
        if self.raster is None:
            warnings.warn("No raster files in this observation.")

        # set a few interesting KPIs
        self.obsid = self.sji[0].obsid
        self.mode = self.sji[0].mode
        self.desc = self.sji[0].desc
        self.start_date = self.sji[0].start_date
        self.end_date = self.sji[0].end_date
        
        # create the goes loader
        self.goes = goes_data( self.start_date, self.end_date, path + "/goes_data", lazy_eval=True )
        
        # create the hek loader
        self.hek = hek_data( self.start_date, self.end_date, lazy_eval=True )
        
    # define print output
    def __str__( self ):
        desc = self.desc
        if not self.sji is None: 
            desc += "\n\nSJI lines:\n" + str(self.sji.get_lines())
        if not self.raster is None:
            desc += "\n\nraster lines:\n" + str(self.raster.get_lines())
        return desc
    
    # functions to enter and exit a context
    def __enter__( self ):
        return self
    
    def __exit__( self ):
        self.close()
    
    # function to get all files in a specified path
    def _get_files( self, path, type='all' ):
        result = []
        dir_content = os.listdir( path )
        if dir_content == []:
            return []
        else:
            for file in dir_content:
                if (type=='all' or (type=='raster' and 'raster' in file) or (type=='sji' and 'SJI' in file)) and (file[-5:] == '.fits' ):
                    result.append(os.path.join(path, file))
        
            return sorted( result )

    # function to close files
    def close( self ):
        """
        Closes all associated FITS files.
        """
        if not self.sji is None:
            self.sji._close()
        if not self.raster is None:
            self.raster._close()