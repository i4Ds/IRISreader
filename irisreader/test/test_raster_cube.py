import unittest
import numpy as np
from irisreader.raster_cube import raster_cube

class test_raster_cube( unittest.TestCase ):
    
    def setUp( self ):
        self.raster = raster_cube( 'irisreader/data/IRIS_raster_test1.fits', line='Mg' )

    def tearDown( self ):
        self.raster.close()

    def test_init( self ):
        self.assertEqual( self.raster.n_steps, 3 )
        self.assertEqual( self.raster.type, 'raster' )
        self.assertRaises( ValueError, raster_cube, 'irisreader/data/IRIS_SJI_test.fits' )
        self.assertEqual( len( self.raster.primary_headers ), 215 )
        self.assertEqual( self.raster.time_specific_headers[2]['DATE_OBS'], '2014-03-29T14:09:58.000' )
    
    def test_prepare_combined_headers( self ):
        self.assertEqual( self.raster.headers[2]['XCEN'], self.raster.headers[2]['XCENIX'] )
        self.assertEqual( self.raster.headers[2]['WAVELNTH'], self.raster.headers[1]['WAVELNTH'] )
        self.assertEqual( self.raster.headers[2]['DATE_OBS'], self.raster.headers[2]['DATE_OBS'] )

    def test_coordinates( self ):
        ycen = self.raster.primary_headers['YCEN']

        # Test transformation inverse on origin and first and second time step    
        self.assertTrue( np.all( self.raster.coords2pix( 0, self.raster.pix2coords( 0, np.array([0,0]) ) ) == np.array([0,0]) ) )
        self.assertTrue( np.all( self.raster.coords2pix( 1, self.raster.pix2coords( 1, np.array([0,0]) ) ) == np.array([0,0]) ) )
        
        # Test transformation inverse on upper right corner and first and second time step    
        self.assertTrue( np.all( self.raster.coords2pix( 0, self.raster.pix2coords( 0, np.array([self.raster.shape[2],self.raster.shape[1]]) ) ) == np.array([self.raster.shape[2],self.raster.shape[1]]) ) )
        self.assertTrue( np.all( self.raster.coords2pix( 1, self.raster.pix2coords( 1, np.array([self.raster.shape[2],self.raster.shape[1]]) ) ) == np.array([self.raster.shape[2],self.raster.shape[1]]) ) )
        
        # Test transformation the other way using suitable coordinates
        self.assertTrue( np.all( self.raster.pix2coords( 0, self.raster.coords2pix( 0, np.array([2800,ycen]), round_pixels=False ) ) - np.array([2800,ycen]) < 1e-10 )  )
        
        # Test whether transformation of YCEN lands more or less in the middle in terms of pixel coordinates
        self.assertTrue( np.abs( (self.raster.coords2pix( 0, np.array([2800,ycen]), round_pixels=False )[1] - self.raster.shape[1]/2) / (self.raster.shape[1]/2) ) < 0.1 )
        
        # Test get_axis_coordinates
        self.assertTrue( np.all( [np.min( self.raster.get_axis_coordinates(0)[0] ), np.min( self.raster.get_axis_coordinates(0)[1] )] - self.raster.pix2coords( 0, np.array([0,0]) ) == np.array([0,0])) )
        self.assertTrue( np.all( [np.max( self.raster.get_axis_coordinates(0)[0] ), np.max( self.raster.get_axis_coordinates(0)[1] )] - self.raster.pix2coords( 0, np.array([self.raster.shape[2],self.raster.shape[1]]) ) == np.array([0,0])) )        
        
        # Store coordinates of the origin of the uncropped self.raster to check cropping
        uncropped_cords = self.raster.pix2coords( 1, np.array([0,0]) )
        
        # Test whether the above commands also work on a cropped self.raster
        self.raster.crop()
        self.assertTrue( np.all( self.raster.coords2pix( 0, self.raster.pix2coords( 0, np.array([0,0]) ) ) == np.array([0,0]) ) )
        self.assertTrue(np.all( self.raster.coords2pix( 1, self.raster.pix2coords( 1, np.array([0,0]) ) ) == np.array([0,0]) ) )
        self.assertTrue(np.all( self.raster.coords2pix( 0, self.raster.pix2coords( 0, np.array([self.raster.shape[2],self.raster.shape[1]]) ) ) == np.array([self.raster.shape[2],self.raster.shape[1]]) ) )
        self.assertTrue(np.all( self.raster.coords2pix( 1, self.raster.pix2coords( 1, np.array([self.raster.shape[2],self.raster.shape[1]]) ) ) == np.array([self.raster.shape[2],self.raster.shape[1]]) ) )
        self.assertTrue(np.all( self.raster.pix2coords( 0, self.raster.coords2pix( 0, np.array([2800,ycen]), round_pixels=False ) ) - np.array([2800,ycen]) < 1e-10 ) )
        self.assertTrue(np.abs( (self.raster.coords2pix( 0, np.array([2800,ycen]), round_pixels=False )[1] - self.raster.shape[1]/2) / (self.raster.shape[1]/2) ) < 0.1 )
        self.assertTrue( np.all( [np.min( self.raster.get_axis_coordinates(0)[0] ), np.min( self.raster.get_axis_coordinates(0)[1] )] - self.raster.pix2coords( 0, np.array([0,0]) ) == np.array([0,0])) )
        self.assertTrue( np.all( [np.max( self.raster.get_axis_coordinates(0)[0] ), np.max( self.raster.get_axis_coordinates(0)[1] )] - self.raster.pix2coords( 0, np.array([self.raster.shape[2],self.raster.shape[1]]) ) == np.array([0,0])) )        
                
        # Test whether pixels of stored coordinates are now offset by boundaries
        self.assertTrue( np.all( self.raster.coords2pix( 1, uncropped_cords ) == -np.array( [self.raster._xmin, self.raster._ymin] ) ) )
        
