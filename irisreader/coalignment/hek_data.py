import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import timedelta
import irisreader as ir
from irisreader.utils.date import to_Tformat, from_Tformat

class hek_data:
    """
    This class represents an interface to the Heliophysics Events Knowledge
    database (HEK). It loads all HEK active regions and flares that were
    recorded during an IRIS observation and makes them available as a pandas data
    frame.
    
    Parameters
    ----------
 
    caller : iris_data_cube
        observation object that called the hek_data object.
        This is required to give hek_data the ability to access the observation's XCENIX/YCENIX positions at different times in a lazy way.
    instrument : str
        which instrument to query - defaults to GOES which might be most practical
    lazy_eval : boolean
        Whether or not data should only be loaded upon first read access.
    
    Attributes
    ----------    
    start_date : datetime.datetime
        Start date/time of the HEK events time window
    end_date : datetime.datetime
        End date/time of the HEK events time window
    instrument : str
        Queried instrument
    data:
        Pandas data frame with HEK events.
    """
    
    def __init__( self, caller, instrument="GOES", lazy_eval=False ):
        self._caller = caller
        self.start_date = from_Tformat( caller.raster[0].start_date )
        self.end_date = from_Tformat( caller.raster[0].end_date )
        self.instrument = instrument
        self.data = None
        
        if not lazy_eval:
            self._load()
            
    def _load( self ):
        """
        Download HEK data and add IRIS position information.
        """
        
        # download data from lmsal API
        self.data = download_hek_data( self.start_date, self.end_date, self.instrument )
        
        # add iris position information
        if len( self.data ) > 0:
            iris_x = []
            iris_y = []
            for t in self.data.event_starttime:
                x, y = self.get_iris_coordinates( from_Tformat( t ) )
                iris_x.append( x )
                iris_y.append( y )
            self.data['iris_xcenix'] = iris_x
            self.data['iris_ycenix'] = iris_y
                
            # add euclidean distances to IRIS FOV center
            self.data['dist_arcsec'] = np.sqrt( (self.data.hpc_x-self.data.iris_xcenix)**2 + (self.data.hpc_y-self.data.iris_ycenix)**2 )
            self.data.sort_values( by="dist_arcsec", inplace=True )

    # make sure that self.data is lazy loaded
    def __getattribute__( self, name ):
        if name=="data" and object.__getattribute__( self, "data" ) is None:
            self._load()
            return object.__getattribute__( self, "data" )
        else:
            return object.__getattribute__( self, name )

    # return a short summary of the object        
    def __repr__( self ):
        repr_str = "GOES event query interface (through HEK)\n--------------------------------------------------------------\n"
        repr_str += "data source: {}\n".format( ir.config.hek_base_url ) 
        repr_str += "time window: {} - {}\n".format( self.start_date, self.end_date )

        if self._caller is not None:
            repr_str += "\ncaller: {}\n".format( self._caller.full_obsid )
        
        repr_str += "--------------------------------------------------------------\n"
        
        repr_str += "data:            event data\n"
        repr_str += "get_flares():    get flare data\n"
        repr_str += "plot_flares():   plot flare data with respect to IRIS FOV\n"
        repr_str += "--------------------------------------------------------------\n"
    
        return repr_str
    
    def get_flares( self, classes="", in_FOV=False, FOV_margin=100 ):
        """
        Returns a data frame with all flare events in the time window.
        
        Parameters
        ----------
        classes : str
            what flare event classes to return:
                "": all classes, "C": only C-class, "M": only M-class, "X": only X-class, "MX": both M- and X-class, etc.
        in_FOV : bool
            whether to return only flares that occured in the field of view (FOV)
        FOV_margin : int
            search margin in arcsec in addition to field of view (flares can have diameters of ~100 arcsec)
        """
        
        
        fields = ['fl_goescls', 'event_starttime', 'event_endtime', 'event_peaktime', 'hpc_radius', 'hpc_x', 'hpc_y', 'iris_xcenix', 'iris_ycenix', 'dist_arcsec']
        raw_flare_data = self.data[self.data.event_type == 'FL'][ fields ]
        
        # filter out certain flare classes
        flare_data = pd.DataFrame( columns=raw_flare_data.columns )
        if classes == "":
            flare_data = raw_flare_data.copy()
        for cls in classes:
            flare_data = flare_data.append( raw_flare_data[raw_flare_data.fl_goescls.str.contains( cls )], ignore_index=True )
        
        # filter out only flares in FOV within margin if desired
        if in_FOV:
            flare_data = flare_data[ self.in_fov( margin=FOV_margin) ]

        return flare_data
    
    def plot_flares( self, classes="", in_FOV=False, FOV_margin=100 ):
        """
        Plots all flare events with respect to the field of view.
        
        Parameters
        ----------
        classes : str
            what flare event classes to return:
                "": all classes, "C": only C-class, "M": only M-class, "X": only X-class, "MX": both M- and X-class, etc.
        in_FOV : bool
            whether to return only flares that occured in the field of view (FOV)
        margin : int
            search margin in arcsec in addition to field of view (flares can have diameters of ~100 arcsec)
        """
        
        flare_events = self.get_flares( classes, in_FOV, FOV_margin )

        # plot IRIS FOV
        fovx = self._caller.raster[0].primary_headers['FOVX']
        fovy = self._caller.raster[0].primary_headers['FOVY']
        left_x = -fovx/2
        right_x = fovx/2
        upper_y = fovy/2
        lower_y = -fovy/2
        
        plt.plot( [left_x, right_x], [upper_y, upper_y], c="black" )
        plt.plot( [left_x, right_x], [lower_y, lower_y], c="black" )
        plt.plot( [left_x, left_x], [lower_y, upper_y], c="black" )
        plt.plot( [right_x, right_x], [lower_y, upper_y], c="black" )
                
        # plot margin if not zero
        plt.plot( [left_x-FOV_margin, right_x+FOV_margin], [upper_y+FOV_margin, upper_y+FOV_margin], c="black", ls="--" )
        plt.plot( [left_x-FOV_margin, right_x+FOV_margin], [lower_y-FOV_margin, lower_y-FOV_margin], c="black", ls="--" )
        plt.plot( [left_x-FOV_margin, left_x-FOV_margin], [lower_y-FOV_margin, upper_y+FOV_margin], c="black", ls="--" )
        plt.plot( [right_x+FOV_margin, right_x+FOV_margin], [lower_y-FOV_margin, upper_y+FOV_margin], c="black", ls="--" )
        
        # plot FOV center
        plt.scatter( 0, 0, marker="x", s=100, c="black" )

        # plot flare events
        for index, event in flare_events.iterrows():
            plt.scatter( 
                    event['hpc_x'] - event['iris_xcenix'], 
                    event['hpc_y'] - event['iris_ycenix'], 
                    marker="*", s=100, label="{} {}".format( event['fl_goescls'], event['event_starttime'] ) 
            )
            
        # set labels
        plt.xlabel("solar x [arcsec]")
        plt.ylabel("solar y [arcsec]")
        plt.title("(points outside the FOV are subject to projection errors)")
        if len( flare_events ) > 0:
            plt.legend()
        plt.show()        
        

    def in_fov( self, margin=100 ):
        """
        This function returns a list of boolean values for each row in the event
        data frame, stating for each event whether it occured in the IRIS FOV plus 
        some margin (flares can spread to diameters of up to 100 arcseconds).
        
        Parameters
        ----------
        margin : float
            number of arcseconds to extend the field of view event search space (defaults to 100)
            
        Returns
        -------
        in_fov :
            List of boolean values
        """
        
        # get iris coordinates for each event
        # compute distances in x and y direction
        dist_x = np.abs( self.data.hpc_x - self.data.iris_xcenix )
        dist_y = np.abs( self.data.hpc_y - self.data.iris_ycenix )
        
        # define thresholds
        threshold_x = self._caller.raster[0].primary_headers['FOVX']/2 + margin
        threshold_y = self._caller.raster[0].primary_headers['FOVY']/2 + margin
        
        # return boolean indicating whether event is within margin
        return np.logical_and( dist_x <= threshold_x, dist_y <= threshold_y )
    

    def get_iris_coordinates( self, flare_date ):
        """
        Approximates FOV center coordinates of IRIS at the time of a flare.
        
        Parameters
        ----------
        flare_date : datetime.datetime
            start date and time of the flare
            
        Returns
        -------
        iris_xcenix : float
            XCENIX coordinate of IRIS at the time of the flare
        iris_ycenix : float
            YCENIX coordinate of IRIS at the time of the flare
        """
        n = int( np.round( self._caller.raster[0].n_steps * (flare_date-self.start_date) / (self.end_date-self.start_date) ) )
        return [self._caller.raster[0].time_specific_headers[n]['XCENIX'], self._caller.raster[0].time_specific_headers[n]['YCENIX']]



def download_hek_data( start_date, end_date, instrument=None ):
    """
    This function downloads all HEK active regions and flares between `start_date`
    and `end_date`.
    
    Parameters
    ----------
    start_date : datetime.datetime
        Start date/time of the HEK events time window
    end_date : datetime.datetime
        End date/time of the HEK events time window
    instrument : str
        Use only data from given instrument, will download data from all instruments if set to None, defaults to "GOES"
        
    Returns
    -------
    float
        Pandas data frame with HEK events.
    """
    
    # set params for json request
    hek_params = {
            "cosec": "2",  # JSON format
            "cmd": "search",
            "type": "column",
            "event_type": "fl,ar",  # Flares and active regions
            "event_starttime": to_Tformat( start_date-timedelta(hours=2) ),
            "event_endtime": to_Tformat( end_date+timedelta(hours=2) ),
            "event_coordsys": "helioprojective",
            "x1": "-1200",
            "x2": "1200",
            "y1": "-1200",
            "y2": "1200",
            "result_limit": "500",
            "page": 1,
            "return": "hpc_bbox,hpc_coord,event_type,intensmin,obs_meanwavel,intensmax,intensmedian,obs_channelid,ar_noaaclass,frm_name,obs_observatory,hpc_x,hpc_y,kb_archivdate,ar_noaanum,frm_specificid,hpc_radius,event_starttime,event_endtime,event_peaktime,fl_goescls,frm_daterun,fl_peakflux,fl_goescls",
            "param0": "FRM_NAME",
            "op0": "=",
            "value0": "NOAA SWPC Observer,SWPC,SSW Latest Events"
        }
    
    if instrument is not None:
        hek_params.update( {
            "param1": "OBS_Observatory",
            "op1": "=",
            "value1": "GOES"                
        })
        
    # get HEK events within +/- two hours of the observation time frame
    hek_events = []
    while True:
        r = requests.get( ir.config.hek_base_url, hek_params )

        if not r:
            raise Exception("Connection error. Please check HEK: https://www.lmsal.com/isolsearch")

        events = r.json()["result"]

        if len(events) == 0:
            break

        hek_events += events
        hek_params['page'] += 1
    
    # convert results to a data frame and filter out events that stopped before the observation time or started after the observation time    
    df = pd.DataFrame( hek_events )
    if len( df ) > 0:
        df = df[np.logical_and( df.event_starttime < to_Tformat( end_date ), df.event_endtime > to_Tformat( start_date ) )]
    
    return df

if __name__ == "__main__":
    from irisreader import observation
    s = from_Tformat("2014-01-01T21:30:11")
    e = from_Tformat("2014-01-03T1:30:17")

    obs = observation( "/home/chuwyler/Desktop/FITS/20140329_140938_3860258481/" )
    h = hek_data( instrument="GOES", caller=obs )
