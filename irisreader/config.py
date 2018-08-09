# This is a config file for internal use, please do not modify it if you are not
# instructed otherwise. Make sure you rebuild the package after you made changes
# to this file.

# Available mirrors
MIRRORS = {
        'lmsal': 'http://www.lmsal.com/solarsoft/irisa/data/level2_compressed/', 
        'uio': 'http://sdc.uio.no/vol/fits/iris/level2/', 
        'fhnw': 'http://server1071.cs.technik.fhnw.ch/data/'
        }

# default mirror
DEFAULT_MIRROR = "lmsal"

# goes base url
GOES_BASE_URL = "https://satdat.ngdc.noaa.gov/sem/goes/data/full/"
#GOES_BASE_URL = "http://server1071.cs.technik.fhnw.ch/goes/xrs/"

# HEK url
HEK_URL = "http://www.lmsal.com/hek/her"