import unittest
import numpy as np
from irisreader import observation
from irisreader.preprocessing import image_cube_cropper
from irisreader.preprocessing import spectrum_smoother

class test_spectrum_smoother( unittest.TestCase ):
    
    def setUp( self ):
        self.obs = observation( "irisreader/data/20140518_151415_3820607204" )
        self.X = np.transpose( image_cube_cropper().fit_transform( self.obs.raster[2] ).get_image_step( 0 ) )
        
    def tearDown( self ):
        self.obs.close()
        
    def test_fit_transform( self ):
        self.smoother = spectrum_smoother( width=1 )
        X_smoothed = self.smoother.fit_transform( self.X )
        
        # test deviation for a particular spectrum
        self.assertEqual( np.sqrt( np.sum( (self.X[100,:]-X_smoothed[100,:])**2 ) ), 68.939020093083 )
        
        
    
