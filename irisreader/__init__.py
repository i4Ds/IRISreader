from irisreader.file_hub import file_hub, ASTROPY_FILE_METHOD
from irisreader.iris_data_cube import iris_data_cube
from irisreader.raster_cube import raster_cube
from irisreader.sji_cube import sji_cube
from irisreader.get_lines import get_lines
from irisreader.has_line import has_line
from irisreader.observation import observation

# instantiate file hub object and make it global
file_hub = file_hub( ASTROPY_FILE_METHOD )

# format for warnings
import warnings
def warning_format(message, category, filename, lineno, file=None, line=None):
    return 'Warning: {} \n'.format( message )
warnings.formatwarning = warning_format

