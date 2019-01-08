class config:
    """
    IRISreader configuration
    
    To see what options are possible, run `print(ir.config)`.
    Options can be set with `ir.config.OPTION = value`.
    
    To learn more about a certain option, read the online documentation of 
    irisreader or the docstrings in the source code.
    """

    # return current configuration upon print call
    def __repr__( self ):
        options = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        ret_str = "IRISreader configuration:\n---------------------------\n"
        for option in options:
            ret_str += "{}: {}\n".format(option, getattr(self, option) )
            
        return ret_str
    
    """
    sets verbosity level:
    0: batch mode (no printed output)
    1: interactive mode (printed output that informs the interactive user) (DEFAULT)
    2: developer mode (printed output that gives more diagnostics that are only useful for the developer)
    3: unfiltered mode (print all possible outputs, should only be used for specific debugging)
    """
    verbosity_level = 1

    """
    sets memory mapping mode:
    It currently seems that many computations are sometimes a factor of 1000 
    faster when the file's data are loaded into memory. The largest data cube has 
    a size of ~2 GB (total raster file size 14 GB), which should not be a problem 
    if only one data cube is loaded at the same time.
    Using memmap for interactive mode might be better because of the lower response times (loading data into memory)
    True: use memory mapping
    False: load data into memory (DEFAULT)
    """
    use_memmap = False

    """
    sets maximum number of open files in file hub (DEFAULT: 256)
    """
    max_open_files = 256

    """
    Available data mirrors for downloading. Check ir.config.MIRRORS to see the 
    list of available mirrors.
    """
    MIRRORS = {
        'lmsal': 'http://www.lmsal.com/solarsoft/irisa/data/level2_compressed/', 
        'uio': 'http://sdc.uio.no/vol/fits/iris/level2/', 
        'fhnw': 'http://server1071.cs.technik.fhnw.ch/data/' # only available through vpn
        }

    """
    Default data mirror to use for downloading data
    """
    DEFAULT_MIRROR = "lmsal"

    """
    Base URL for GOES data
    """
    GOES_BASE_URL = "https://satdat.ngdc.noaa.gov/sem/goes/data/full/"
    #GOES_BASE_URL = "http://server1071.cs.technik.fhnw.ch/goes/xrs/"

    """
    Base URL for HEK data
    """
    HEK_URL = "http://www.lmsal.com/hek/her"