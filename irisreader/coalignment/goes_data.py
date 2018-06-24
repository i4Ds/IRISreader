#!/usr/bin/env python

import pandas as pd
import datetime as dt
import requests
import os
from scipy.interpolate import interp1d
import numpy as np

from irisreader.config import GOES_BASE_URL

# TODO: create a downloader utility function?


class goes_data:
    """
    This class represents an interface to GOES X-ray flux data. An instantiated
    object will download all GOES15 XRS data between the given dates and will
    store it in the specified data directory. Data that are already present
    will not be downloaded again. The stored data is made accessible as a
    pandas data frame which can then be plotted with `plot` or interpolated to
    other points in time with `interpolate`. Optionally, the data are only
    loaded upon first read access.
    
    Parameters
    ----------
    start_date : datetime.datetime
        Start date/time of the time window for which GOES data should be 
        downloaded.
    end_date : datetime.datetime
        End date/time of the time window for which GOES data should be 
        downloaded.
    data_dir : string
        Data directory in which the downloaded data will be stored.
    lazy_eval : boolean
        Whether or not data should only be loaded upon first read access.

    Attributes
    ----------    
    start_date : datetime.datetime
        Start date/time of the GOES X-ray flux data time window
    end_date : datetime.datetime
        End date/time of the GOES X-ray flux data time window
    data:
        Pandas data frame with GOES data.
    """
    
    def __init__( self, start_date, end_date, data_dir, lazy_eval=False ):
        self._data_dir = data_dir
        self.start_date = start_date
        self.end_date = end_date
        self._files = []
        self.data = None
        
        if not lazy_eval:
            self._load()

    # catch attribute requests to perform lazy loading if necessary
    def __getattribute__( self, name ):
        if name=="data" and object.__getattribute__( self, "data" ) is None:
            self._load()
            return object.__getattribute__( self, "data" )
        else:
            return object.__getattribute__( self, name )
            
    # function to load data and download files if necessary
    def _load( self ):
        
        # create data directory if not present
        if not os.path.exists( self._data_dir ):
            try:
                os.mkdir( self._data_dir )
            except: # write to the local folder if no permission to create directory
                self._data_dir = "goes_data"
                os.mkdir( self._data_dir )
                
            
        # download files
        self._get_files( self.start_date, self.end_date )
        
        # parse files and concatenate data frames
        self.data = pd.DataFrame( [] )
        for file in self._files:
            self.data = self.data.append( self._parse_file( self._data_dir + "/" + file ) )
            
    # function to download all required goes data for a certain time span
    def _get_files( self, start_date, end_date ):
        for day in range((end_date-start_date).days + 2):
            current_date = start_date + dt.timedelta(days=day)
            date_str = current_date.strftime("%Y%m%d")
            target_file_name = "g15_xrs_2s_" + date_str + "_" + date_str + ".csv"
            target_url = GOES_BASE_URL + "/" + str(current_date.year) + "/" + str(current_date.month).zfill(2) + "/goes15/csv/" + target_file_name
            self._download_file( target_url, target_file_name )
            self._files.append( target_file_name )

    # function to download a file if it is not yet present                     
    def _download_file( self, url, target_file_name ):
        
        # download data
        if not os.path.exists( self._data_dir + "/" + target_file_name ):
            print( "Downloading " + target_file_name )
            r = requests.get( url )
        
            if r.ok:
                with open( self._data_dir + "/" + target_file_name, "wb" ) as f:
                    f.write( r.content )
            else:
                raise Exception( "File could not be downloaded" )

    # function to parse goes csv data into a pandas data frame
    def _parse_file( self, file_path ):
        with open( file_path, "r" ) as f:
            # Skip lines until data: label is read
            for line in f:
                if line.startswith("data:"):
                    break

            return pd.read_csv( f, sep=",", parse_dates=["time_tag"], index_col="time_tag" )


    def plot( self, restrict_to_obstime=False ):
        """
        This function plots the GOES X-ray flux around the given time period.
        
        Parameters
        ----------
        restrict_to_obstime : boolean
            If True, only the flux within the observation time period will be 
            plotted.
        """
        
        # prepare a data frame with zero values set to NaN (such that matplotlib does not plot them)
        plot_data = self.data.copy()
        plot_data.loc[:]['A_FLUX'][plot_data['A_FLUX']==0] = np.nan
        plot_data.loc[:]['B_FLUX'][plot_data['B_FLUX']==0] = np.nan
        
        # plot the fluxes
        ax = plot_data.plot( y=['A_FLUX', 'B_FLUX'], logy=True, title="GOES X-ray Flux" )
        
        # restrict plot to observation time period if desired, otherwise draw
        # shaded region and dashed restriction lines where the observation
        # takes place
        if restrict_to_obstime:
            ax.set_xlim([self.start_date, self.end_date])
        else:
            ax.axvspan( self.start_date, self.end_date, alpha=0.05, color='red' )
            ax.axvline( x=self.start_date, color='red', linestyle='--', linewidth=1.0 )
            ax.axvline( x=self.end_date, color='red', linestyle='--', linewidth=1.0 )
        
        # draw magnitudes with dashed lines 
        ax.axhline( y=1e-3, color='black', linestyle='--', linewidth=1.0 )
        ax.axhline( y=1e-4, color='black', linestyle='--', linewidth=1.0 )
        ax.axhline( y=1e-5, color='black', linestyle='--', linewidth=1.0 )
        ax.axhline( y=1e-6, color='black', linestyle='--', linewidth=1.0 )
        ax.axhline( y=1e-7, color='black', linestyle='--', linewidth=1.0 )
        ax.axhline( y=1e-8, color='black', linestyle='--', linewidth=1.0 )
        
        # set a magnitude scale on the right
        ax2 = ax.twinx()
        ax2.set_ylim( ax.get_ylim() )
        ax2.set_yscale( 'log' )
        ax2.set_yticks([3e-8, 3e-7, 3e-6, 3e-5, 3e-4])
        ax2.set_yticklabels(['A', 'B', 'C', 'M', 'X'])
        ax2.minorticks_off()
        ax2.tick_params( right=False )
        
        # set boundaries, labels and legend
        ax.set_ylim([1e-9, 1e-2])
        ax.set_ylabel(r'Watts / m$^2$')
        ax.set_xlabel("Universal Time")
        ax.legend( ['GOES 15 0.5-1 $\AA$', 'GOES 15 1-8 $\AA$'] )
 
        
    def interpolate( self, iris_timestamps, field=['B_FLUX'] ):
        """
        This function takes timestamps from `iris_data_cube.get_timestamps()`
        (UNIX time - seconds since Thursday, 1 January 1970 00:00:00) and
        computes interpolated GOES flux data.
        
        Parameters
        ----------
        iris_timestamps : float
            Array with timestamps from `iris_data_cube.get_timestamps()` or 
            `combined_raster.get_timestamps()`.
        field : string
            'B_FLUX' (default) for the 1-8 Angstrom X-ray flux or 'A_FLUX' for
            the 0.5-1 Angstrom X-ray flux.
            
        Returns
        -------
        float
            List with interpolated GOES fluxes in W/m^2
        """
        
        goes_timestamps = np.array( (self.data.index-dt.datetime.utcfromtimestamp(0)).total_seconds() )
        f = interp1d( x=goes_timestamps, y=self.data[field].values.flatten(), kind="cubic" )
        return f( iris_timestamps )
    
    def get_peak_flux( self, flux='B_FLUX' ):
        """
        Returns the peak flux measured in the observation time period.
        
        Parameters
        ----------
        field : str
            'B_FLUX' (default) for the 1-8 Angstrom X-ray flux or 'A_FLUX' for
            the 0.5-1 Angstrom X-ray flux.
            
        Returns
        -------
        float
            Peak flux in W/m^2
        """
        fluxes = self.data[np.logical_and( self.data.index >= self.start_date, self.data.index <= self.end_date)][flux]
        if len( fluxes ) > 0:
            return np.nanmax( fluxes)
        else:
            return None
