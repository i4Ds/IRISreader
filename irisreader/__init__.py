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

# set verbosity level
# 0: batch mode (no printed output)
# 1: interactive mode (printed output that informs the interactive user)
# 2: developer mode (printed output that gives more diagnostics that are only useful for the developer)
# 3: unfiltered mode (print all possible outputs, should only be used for specific debugging)
verbosity_level = 1