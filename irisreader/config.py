class config_template:
    """
    Configuration template for the irisreader module of which an instance is
    created at irisreader.config.
    
    To see what options are currently set, run print(irisreader.config).
    Options can be set with `ir.config.OPTION = value`.
    For help about the different configuration options run help(irisreader.config).
    
    To learn more about a certain option, read the online documentation of 
    irisreader or the docstrings in the source code.
    
    Attributes
    ----------
    verbosity_level : int
        Sets verbosity level of IRISreader:
        0: batch mode (no printed output)
        1: interactive mode (printed output that informs the interactive user)
        2: developer mode (printed output that gives more diagnostics that are only useful for the developer)
        3: unfiltered mode (print all possible outputs, should only be used for specific debugging)
        
        Default: 1

    use_memmap : bool
        Sets memory mapping mode:
        It currently seems that many computations are sometimes a factor of 1000 
        faster when the file's data are loaded into memory. The largest data cube has 
        a size of ~2 GB (total raster file size 14 GB), which should not be a problem 
        if only one data cube is loaded at the same time.
        Using memmap for interactive mode might be better because of the lower response times (loading data into memory)
        
        True: use memory mapping
        
        False: load data into memory (default)
        
    max_open_files : int
        Sets maximum number of open files:
        Some rasters have > 6000 files and irisreader may reach the open files limit of the host system when opening all at once.
        For this reason, the file_hub class abstracts file access and allows to limit the number of open files.
        
        Default: 256
        
    mirrors : list
        Available data mirrors for downloading observations.
    
    default_mirror : str
        Default mirror to use from ir.config.mirrors
        
    goes_base_url : str
        Base URL for GOES data (as used in GOES coalignment)

    hek_base_url : str
        Base URL for HEK data

    """

    # return current configuration upon print call
    def __repr__( self ):
        options = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        ret_str = "IRISreader configuration:\n---------------------------\n"
        for option in options:
            ret_str += "{}: {}\n".format(option, getattr(self, option) )
            
        return ret_str

    # set default configuration    
    verbosity_level = 1
    use_memmap = False
    max_open_files = 256
    mirrors = {
        'lmsal': 'http://www.lmsal.com/solarsoft/irisa/data/level2_compressed/', 
        'uio': 'http://sdc.uio.no/vol/fits/iris/level2/', 
        'fhnw': 'http://server0090.cs.technik.fhnw.ch/iris_compressed/' # only available through vpn
        }
    default_mirror = "lmsal"
    goes_base_url = "https://satdat.ngdc.noaa.gov/sem/goes/data/full/"
    #goes_base_url = "http://server1071.cs.technik.fhnw.ch/iris/goes/xrs/"
    hek_base_url = "http://www.lmsal.com/hek/her"