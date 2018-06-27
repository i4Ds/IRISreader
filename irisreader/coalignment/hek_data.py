import requests
import pandas as pd
import numpy as np

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

    Attributes
    ----------    
    start_date : datetime.datetime
        Start date/time of the HEK events time window
    end_date : datetime.datetime
        End date/time of the HEK events time window
    data:
        Pandas data frame with HEK events.
    """
    
    def __init__( self, start_date, end_date, lazy_eval=False ):
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        
        if not lazy_eval:
            self.data = load_hek_data( self.start_date, self.end_date )
        
    def __getattribute__( self, name ):
        if name=="data" and object.__getattribute__( self, "data" ) is None:
            self.data = load_hek_data( self.start_date, self.end_date )
            return object.__getattribute__( self, "data" )
        else:
            return object.__getattribute__( self, name )
        
    def get_flares( self ):
        fields = ['fl_goescls', 'hpc_radius', 'hpc_x', 'hpc_y']
        return self.data[self.data.event_type == 'FL'][ fields ]


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
    hek_events = []
    
    page = 1
    while True:
        r = requests.get("http://www.lmsal.com/hek/her", params={
            "cosec": "2",  # JSON format
            "cmd": "search",
            "type": "column",
            "event_type": "fl,ar",  # Flares and active regions
            "event_starttime": to_Tformat( start_date ),
            "event_endtime": to_Tformat( end_date ),
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
        
    return pd.DataFrame( hek_events )


