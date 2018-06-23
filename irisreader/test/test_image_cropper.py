import unittest
import numpy as np
from irisreader import sji_cube, raster_cube
from irisreader.preprocessing import image_cropper

class test_image_cropper( unittest.TestCase ):
    
    def setUp( self ):
        self.sji_data = sji_cube( 'irisreader/data/IRIS_SJI_test.fits' )
        self.raster_data = raster_cube( 'irisreader/data/IRIS_raster_test1.fits', line="Mg" )
    
    def tearDown( self ):
        self.sji_data.close()
        self.raster_data.close()
        
    def test_sji_cropping( self ):
        image = self.sji_data.get_image_step( 0 )
        units = self.sji_data.get_units( 0 )
        cropper = image_cropper()
        cropped_image = cropper.fit_transform( image )
        cropped_units = cropper.transform_units( units )
        
        self.assertEqual( np.sum( cropped_image < 0), 170 )
        self.assertEqual( cropped_image.shape, (997, 1045) )
        self.assertEqual( cropped_image[100,100], 293.25 )
        self.assertEqual( ( len(cropped_units[0]), len(cropped_units[1]) ), cropped_image.shape )
        self.assertEqual( cropper.get_bounds(), [22, 1019, 30, 1075] )
        
    def test_raster_cropping( self ):
        image = self.raster_data.get_image_step( 0 )
        units = self.raster_data.get_units( 0 )
        cropper = image_cropper()
        cropped_image = cropper.fit_transform( image )
        cropped_units = cropper.transform_units( units )
        
        self.assertEqual( np.sum( cropped_image < 0), 0 )
        self.assertEqual( cropped_image.shape, (581, 1040) )
        self.assertEqual( cropped_image[100,100], 61.75 )
        self.assertEqual( ( len(cropped_units[0]), len(cropped_units[1]) ), cropped_image.shape )
        self.assertEqual( cropper.get_bounds(), [26, 607, 2, 1042] )
    
