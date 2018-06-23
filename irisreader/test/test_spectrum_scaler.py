import unittest
import numpy as np
from irisreader import observation
from irisreader.preprocessing import image_cube_cropper
from irisreader.preprocessing import spectrum_scaler

class test_spectrum_scaler( unittest.TestCase ):
    
    def setUp( self ):
        self.obs = observation( "irisreader/data/20140518_151415_3820607204" )
        self.X = np.transpose( image_cube_cropper().fit_transform( self.obs.raster[2] ).get_image_step( 0 ).astype( np.float64 ) )
        self.exptime = self.obs.raster[2].headers[0]['EXPTIME']
        
    def tearDown( self ):
        self.obs.close()
        
    def test_exposure_only( self ):
        self.scaler = spectrum_scaler( method="exposure_only", exposure_time=self.exptime ).fit( self.X )
        self.assertEqual( self.scaler._scale_params, 1 )
        self.assertIsNone( self.scaler._scaler )
        
        X_scaled = self.scaler.transform( self.X )
        self.assertEqual( np.mean( self.X.clip(min=0) / X_scaled  ), self.exptime )

    def test_divide_by_max( self ):
        self.scaler = spectrum_scaler( method="divide_by_max" ).fit( self.X )
        self.assertEqual( self.scaler._scale_params.shape, (1040,1) )
        self.assertIsNone( self.scaler._scaler )
        
        X_scaled = self.scaler.transform( self.X )
        self.assertEqual( np.mean( self.X.clip(min=0) / np.max( self.X.clip(min=0), axis=1).reshape(-1,1) / X_scaled ), 1.0 )
        
    def test_divide_by_sum( self ):
        self.scaler = spectrum_scaler( method="divide_by_sum" ).fit( self.X )
        self.assertEqual( self.scaler._scale_params.shape, (1040,1) )
        self.assertIsNone( self.scaler._scaler )
        
        X_scaled = self.scaler.transform( self.X )
        self.assertEqual( np.mean( self.X.clip(min=0) / np.sum( self.X.clip(min=0), axis=1).reshape(-1,1) / X_scaled * self.X.shape[1] ), 1.0 )
        
    def test_divide_by_norm( self ):
        self.scaler = spectrum_scaler( method="divide_by_norm" ).fit( self.X )
        self.assertEqual( self.scaler._scale_params.shape, (1040,1) )
        self.assertIsNone( self.scaler._scaler )
        
        X_scaled = self.scaler.transform( self.X )
        self.assertEqual( np.mean( self.X.clip(min=0) / np.linalg.norm( self.X.clip(min=0), ord=2, axis=1).reshape(-1,1) / X_scaled * self.X.shape[1] ), 1.0 )
        
    def test_centerscale( self ):
        self.scaler = spectrum_scaler( method="centerscale" ).fit( self.X )
        self.assertIsNone( self.scaler._scale_params )
        self.assertEqual( str( type(self.scaler._scaler) ), "<class 'sklearn.preprocessing.data.StandardScaler'>" )
        
        X_scaled = self.scaler.transform( self.X )
        self.assertTrue( -1e-5 < np.mean( X_scaled ) < 1e-5 )
        self.assertTrue( 0.99999 < np.std( X_scaled ) < 1.00001 )
        
        self.assertEqual( np.mean( self.scaler.inverse_transform( self.scaler.transform( self.X ) ) / self.X.clip(min=0) ), 1.0 )