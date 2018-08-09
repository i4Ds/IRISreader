from irisreader.file_hub import file_hub, ASTROPY_FILE_METHOD
from irisreader.iris_data_cube import iris_data_cube
from irisreader.raster_cube import raster_cube
from irisreader.sji_cube import sji_cube
from irisreader.get_lines import get_lines
from irisreader.has_line import has_line
from irisreader.observation import observation
from irisreader.obs_iterator import obs_iterator

# instantiate file hub object and make it global
file_hub = file_hub( ASTROPY_FILE_METHOD )

# format for warnings
import warnings
def warning_format(message, category, filename, lineno, file=None, line=None):
    return 'Warning: {} \n'.format( message )
    warnings.formatwarning = warning_format

# ------------ configuration -------------------------------------------------

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