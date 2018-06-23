import unittest
import numpy as np
from irisreader import observation
from irisreader.preprocessing import image_cube_cropper

class test_image_cube_cropper( unittest.TestCase ):
    
    def setUp( self ):
        self.obs = observation("irisreader/data/20140518_151415_3820607204", keep_null=True)
        self.cube_cropper1 = image_cube_cropper()
        self.cube_cropper2 = image_cube_cropper()
        self.cube_cropper1.fit( self.obs.raster[1] )
        self.cube_cropper2.fit( self.obs.raster[2] )       
        
    def tearDown( self ):
        self.obs.close()
        
    def test_fit( self ):
        self.assertEqual( self.cube_cropper1.get_corrupt_images(), [3] )
        self.assertEqual( self.cube_cropper1.get_null_images(), [] )
        self.assertEqual( self.cube_cropper1.get_bounds(), [16, 109, 47, 1089] )
        
        self.assertEqual( self.cube_cropper2.get_corrupt_images(), [] )
        self.assertEqual( self.cube_cropper2.get_null_images(), [4] )
        self.assertEqual( self.cube_cropper2.get_bounds(), [26, 607, 2, 1042] )
        
    def test_transform( self ):
        transformed_raster1 = self.cube_cropper1.transform( self.obs.raster[1] )
        first_raster1 = transformed_raster1._raster_data[0]
        self.assertEqual( [first_raster1._xmin, first_raster1._xmax, first_raster1._ymin, first_raster1._ymax], self.cube_cropper1.get_bounds() )
        self.assertEqual( transformed_raster1.get_image_step(0).shape, (93, 1042) )
        self.assertEqual( transformed_raster1.get_image_step(0).shape, transformed_raster1.get_image_step(1).shape )
        self.assertEqual( (len( transformed_raster1.get_units(0)[0] ), len( transformed_raster1.get_units(0)[1] )), transformed_raster1.get_image_step(0).shape )
        self.assertEqual( (len( transformed_raster1.get_units(1)[0] ), len( transformed_raster1.get_units(1)[1] )), transformed_raster1.get_image_step(0).shape )
        self.assertEqual( len( self.obs.raster[1].time_specific_headers ), 6 )
        self.assertEqual( len( transformed_raster1.time_specific_headers ), 5 )
        self.assertEqual( len( self.obs.raster[1].headers ), 6 )
        self.assertEqual( len( transformed_raster1.headers ), 5 )
        self.assertEqual( transformed_raster1.n_raster_steps, [3,2] )
        self.assertEqual( transformed_raster1.n_steps, 5 )
        self.assertEqual( len( transformed_raster1.get_timestamps() ), 5 )

        transformed_raster2 = self.cube_cropper2.transform( self.obs.raster[2] )
        first_raster2 = transformed_raster2._raster_data[0]
        self.assertEqual( [first_raster2._xmin, first_raster2._xmax, first_raster2._ymin, first_raster2._ymax], self.cube_cropper2.get_bounds() )
        self.assertEqual( transformed_raster2.get_image_step(0).shape, (581, 1040) )
        self.assertEqual( transformed_raster2.get_image_step(0).shape, transformed_raster2.get_image_step(1).shape )
        self.assertEqual( (len( transformed_raster2.get_units(0)[0] ), len( transformed_raster2.get_units(0)[1] )), transformed_raster2.get_image_step(0).shape )
        self.assertEqual( (len( transformed_raster2.get_units(1)[0] ), len( transformed_raster2.get_units(1)[1] )), transformed_raster2.get_image_step(0).shape )
        self.assertEqual( len( self.obs.raster[2].time_specific_headers ), 6 )
        self.assertEqual( len( transformed_raster2.time_specific_headers ), 5 )
        self.assertEqual( len( self.obs.raster[2].headers ), 6 )
        self.assertEqual( len( transformed_raster2.headers ), 5 )
        self.assertEqual( transformed_raster2.n_raster_steps, [3,2] )
        self.assertEqual( transformed_raster2.n_steps, 5 )
        self.assertEqual( len( transformed_raster2.get_timestamps() ), 5 )        
