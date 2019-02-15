import requests
import pandas as pd
import numpy as np

from datetime import timedelta
import irisreader as ir
from irisreader.utils.date import to_Tformat

class hek_data:
    """
    This class represents an interface to the Heliophysics Events Knowledge
    database (HEK). It loads all HEK active regions and flares that were
    recorded in a defined time span and makes them available as a pandas data
    frame. Optionally, the data are only loaded upon first read access.
    
    Parameters
    ----------
    start_date : datetime.datetime
        Start date/time of the time window for which HEK events should be 
        downloaded.
    end_date : datetime.datetime
        End date/time of the time window for which HEK events should be 
        downloaded.
    lazy_eval : boolean
        Whether or not data should only be loaded upon first read access.
    x : float
        solar coordinates x of center of field of view in arcsec (defaults to None)
    y : float
        solar coordinates y of center of field of view in arcsec (defaults to None)
    fovx : float
        width of the field of view (FOV) in x direction in arcsec (defaults to None)
    fovy : float
        width of the field of view (FOV) in y direction in arcsec (defaults to None)


    Attributes
    ----------    
    start_date : datetime.datetime
        Start date/time of the HEK events time window
    end_date : datetime.datetime
        End date/time of the HEK events time window
    data:
        Pandas data frame with HEK events.
    """
    
    def __init__( self, start_date, end_date, lazy_eval=False, x=None, y=None, fovx=None, fovy=None ):
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.x = x
        self.y = y
        self.fovx = fovx
        self.fovy = fovy
        
        if not lazy_eval:
            self.data = load_hek_data( self.start_date, self.end_date )
        
    def __getattribute__( self, name ):
        if name=="data" and object.__getattribute__( self, "data" ) is None:
            self.data = load_hek_data( self.start_date, self.end_date )
            return object.__getattribute__( self, "data" )
        else:
            return object.__getattribute__( self, name )

    # return a short summary of the object        
    def __repr__( self ):
        ret_str = "HEK query\n--------------------------------------------------------------\n"
        ret_str += "data source: {}\n".format( ir.config.hek_base_url ) 
        ret_str += "time window: {} - {}\n".format( self.start_date, self.end_date )

        if self.x is not None and self.y is not None:
            ret_str += "instrument center of FOV: x = {}'', y = {}''\n".format( self.x, self.y )
            
        if self.fovx is not None and self.fovy is not None:
            ret_str += "instrument FOV width: FOVX = {}'', FOVY = {}'\n".format( self.fovx, self.fovy )
        
        ret_str += "--------------------------------------------------------------\n"

        return ret_str
        
    def get_flares( self, in_FOV=False, margin=100 ):
        """
        Returns a data frame with all flare events in the time window.
        
        Parameters
        ----------
        in_FOV : bool
            whether to return only flares that occured in the field of view (FOV)
        margin : int
            search margin in arcsec in addition to field of view (flares can have diameters of ~100 arcsec)
        """
        
        fields = ['fl_goescls', 'event_starttime', 'event_endtime', 'event_peaktime', 'hpc_radius', 'hpc_x', 'hpc_y']
        flare_data = self.data[self.data.event_type == 'FL'][ fields ]
        
        # raise exception if fovx, fovy, x or y are not initialized
        if in_FOV: 
            if self.x is None or self.y is None:
                raise Exception("fovx and fovy are not initialized!")
            if self.fovx is None or self.fovy is None:
                raise Exception("x and y are not initialized!")
            
            flare_data = flare_data[ in_fov(flare_data, self.x, self.y, self.fovx, self.fovy, margin=margin) ]
    
        return flare_data

def in_fov( data, x, y, fovx, fovy, margin=100 ):
    """
    This function takes a data frame with HEK events and (hpc_x, hpc_y) coordinates
    and returns a list of booleans for every row of the data frame, indicating whether
    the event happend within the field of view or not. Since flares can extend over up
    to 100 arcseconds in diameter, also a margin (defaults to 100) can be specified.
    
    
    Parameters
    ----------
    data : pd.DataFrame
        event data frame given by load_hek_data()
    x : float
        solar coordinate x in arcsec
    y : float
        solar coordinate y in arcsec
    fovx : float
        field of view with in x-direction in arcsec
    fovy : float
        field of view with in y-direction in arcsec
    margin : float
        number of arcseconds to extend the field of view event search space (defaults to 100)
    """
    
    # compute distances in x and y direction
    dist_x = np.abs( x-data['hpc_x'] )
    dist_y = np.abs( y-data['hpc_y'] )
    
    # define thresholds
    threshold_x = fovx/2 + margin
    threshold_y = fovy/2 + margin
    
    # return boolean indicating whether event is within margin
    return np.logical_and( dist_x <= threshold_x, dist_y <= threshold_y )


def load_hek_data( start_date, end_date ):
    """
    This function downloads all HEK active regions and flares between `start_date`
    and `end_date`.
    
    Parameters
    ----------
    start_date : datetime.datetime
        Start date/time of the HEK events time window
    end_date : datetime.datetime
        End date/time of the HEK events time window
        
    Returns
    -------
    float
        Pandas data frame with HEK events.
    """
    
    # get HEK events within +/- two hours of the observation time frame
    hek_events = []
    page = 1
    while True:
        r = requests.get( ir.config.hek_base_url, params={
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
            "page": page,
            "return": "hpc_bbox,hpc_coord,event_type,intensmin,obs_meanwavel,intensmax,intensmedian,obs_channelid,ar_noaaclass,frm_name,obs_observatory,hpc_x,hpc_y,kb_archivdate,ar_noaanum,frm_specificid,hpc_radius,event_starttime,event_endtime,event_peaktime,fl_goescls,frm_daterun,fl_peakflux,fl_goescls",
            "param0": "FRM_NAME",
            "op0": "=",
            "value0": "NOAA SWPC Observer,SWPC,SSW Latest Events"
        })

        events = r.json()["result"]

        if len(events) == 0:
            break

        hek_events += events

        page += 1
    
    # convert results to a data frame and filter out events that stopped before the observation time or started after the observation time    
    df = pd.DataFrame( hek_events )
    df = df[np.logical_and( df.event_starttime < to_Tformat( end_date ), df.event_endtime > to_Tformat( start_date ) )]
    
    return df

if __name__ == "__main__":
    from irisreader.utils.date import from_Tformat
    s = from_Tformat("2014-01-01T21:30:11")
    e = from_Tformat("2014-01-03T1:30:17")
    h = hek_data( s, e, x=-900, y=-71, fovx=50, fovy=50 )
    k = hek_data( s, e, x=-900, y=-71, fovx=50, fovy=None )
    kk = hek_data( s, e, x=-900, y=None, fovx=50, fovy=None )
