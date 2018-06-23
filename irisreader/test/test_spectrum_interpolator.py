import unittest
import numpy as np
from irisreader import observation
from irisreader.preprocessing import image_cube_cropper
from irisreader.preprocessing import spectrum_interpolator

class test_spectrum_interpolator( unittest.TestCase ):
    
    def setUp( self ):
        self.obs = observation( "irisreader/data/20140518_151415_3820607204" )
        self.raster_data = image_cube_cropper().fit_transform( self.obs.raster[2] )
        self.X = np.transpose( self.raster_data.get_image_step(0) )
        
    def tearDown( self ):
        self.obs.close()
        
    def test_fit_transform( self ):
        lambda_min = 2794
        lambda_max = 2800
        lambda_units = self.raster_data.get_units( 0 )[0]
        interpolator = spectrum_interpolator( lambda_min, lambda_max, 100 ).fit( self.X, lambda_units )
        X_interp = interpolator.transform( self.X )
        transformed_units = interpolator.get_units()
        
        self.assertEqual( X_interp.shape, (self.X.shape[0], 100) )
        self.assertEqual( transformed_units[0], lambda_min )
        self.assertEqual( transformed_units[-1], lambda_max )
        self.assertEqual( len( transformed_units ), 100 )
        
        
    
