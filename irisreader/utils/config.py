class config:

    def __repr__( self ):
        options = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        ret_str = "IRISreader configuration:\n---------------------------\n"
        for option in options:
            ret_str += "{}: {}\n".format(option, getattr(self, option) )
            
        return ret_str
    
    # set verbosity level
    # 0: batch mode (no printed output)
    # 1: interactive mode (printed output that informs the interactive user)
    # 2: developer mode (printed output that gives more diagnostics that are only useful for the developer)
    # 3: unfiltered mode (print all possible outputs, should only be used for specific debugging)
    verbosity_level = 1

    # set memory mapping mode
    # It currently seems that many computations are sometimes a factor of 1000 
    # faster when the file's data are loaded into memory. The largest data cube has 
    # a size of ~2 GB (total raster file size 14 GB), which should not be a problem 
    # if only one data cube is loaded at the same time.
    # Using memmap for interactive mode might be better because of the lower response times (loading data into memory)
    # True: use memory mapping
    # False: load data into memory
    use_memmap = False

    # number of open files in file hub
    max_open_files = 512

    # Available mirrors - move this to somewhere else?
    MIRRORS = {
        'lmsal': 'http://www.lmsal.com/solarsoft/irisa/data/level2_compressed/', 
        'uio': 'http://sdc.uio.no/vol/fits/iris/level2/', 
        'fhnw': 'http://server1071.cs.technik.fhnw.ch/data/' # only available through vpn
        }

    # default mirror
    DEFAULT_MIRROR = "lmsal"

    # goes base url
    GOES_BASE_URL = "https://satdat.ngdc.noaa.gov/sem/goes/data/full/"
    #GOES_BASE_URL = "http://server1071.cs.technik.fhnw.ch/goes/xrs/"

    # HEK url
    HEK_URL = "http://www.lmsal.com/hek/her"