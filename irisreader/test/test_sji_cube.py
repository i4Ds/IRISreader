import unittest
import numpy as np
from irisreader.sji_cube import sji_cube
#from .header_regression_test import header_regression_test, read_saved_headers, headers_to_exclude_sji

class test_sji_cube( unittest.TestCase ):
    
    def setUp( self ):
        self.sji = sji_cube( 'irisreader/data/IRIS_SJI_test.fits' )
    
    def tearDown( self ):
        self.sji.close()

    def test_init( self ):
        self.assertEqual( self.sji.n_steps, 3 )
        self.assertEqual( self.sji.type, 'sji' )
        self.assertRaises( ValueError, sji_cube, 'irisreader/data/IRIS_raster_test1.fits' )
        self.assertEqual( len( self.sji.primary_headers ), 147 )   
        self.assertEqual( self.sji.time_specific_headers[2]['DATE_OBS'], '2014-03-29T14:10:25.840' )
    
    def test_prepare_combined_headers( self ):
        self.assertEqual( self.sji.headers[2]['XCEN'], self.sji.headers[2]['XCENIX'] )

    def test_coordinates( self ):
        xcen = self.sji.primary_headers['XCEN']
        ycen = self.sji.primary_headers['YCEN']

        # Test transformation inverse on origin and first and second time step    
        np.all( self.sji.coords2pix( 0, self.sji.pix2coords( 0, np.array([0,0]) ) ) == np.array([0,0]) )
        np.all( self.sji.coords2pix( 1, self.sji.pix2coords( 1, np.array([0,0]) ) ) == np.array([0,0]) )
    
        # Test transformation inverse on upper right corner and first and second time step    
        np.all( self.sji.coords2pix( 0, self.sji.pix2coords( 0, np.array([self.sji.shape[2],self.sji.shape[1]]) ) ) == np.array([self.sji.shape[2],self.sji.shape[1]]) )
        np.all( self.sji.coords2pix( 1, self.sji.pix2coords( 1, np.array([self.sji.shape[2],self.sji.shape[1]]) ) ) == np.array([self.sji.shape[2],self.sji.shape[1]]) )
        
        # Test transformation the other way using suitable coordinates
        np.all( self.sji.pix2coords( 0, self.sji.coords2pix( 0, np.array([xcen,ycen]), round_pixels=False ) ) - np.array([xcen,ycen]) < 1e-10 ) 
        
        # Test whether transformation of XCEN/YCEN lands more or less in the middle in terms of pixel coordinates
        pixels = self.sji.coords2pix( 0, np.array([xcen,ycen]), round_pixels=False )
        np.abs( (pixels - np.array(self.sji.shape[1:])/2) / (np.array(self.sji.shape[1:])/2) ) < 0.1

        # Test get_axis_coordinates
        self.assertTrue( np.all( [np.min( self.sji.get_axis_coordinates(0)[0] ), np.min( self.sji.get_axis_coordinates(0)[1] )] - self.sji.pix2coords( 0, np.array([0,0]) ) == np.array([0,0])) )
        self.assertTrue( np.all( [np.max( self.sji.get_axis_coordinates(0)[0] ), np.max( self.sji.get_axis_coordinates(0)[1] )] - self.sji.pix2coords( 0, np.array([self.sji.shape[2],self.sji.shape[1]]) ) == np.array([0,0])) )        

        # Store coordinates of the origin of the uncropped self.sji to check cropping
        uncropped_cords = self.sji.pix2coords( 1, np.array([0,0]) )

        # Test whether the above commands also work on a cropped self.sji
        self.sji.crop()
        np.all( self.sji.coords2pix( 0, self.sji.pix2coords( 0, np.array([0,0]) ) ) == np.array([0,0]) )
        np.all( self.sji.coords2pix( 1, self.sji.pix2coords( 1, np.array([0,0]) ) ) == np.array([0,0]) )
        np.all( self.sji.coords2pix( 0, self.sji.pix2coords( 0, np.array([self.sji.shape[2],self.sji.shape[1]]) ) ) == np.array([self.sji.shape[2],self.sji.shape[1]]) )
        np.all( self.sji.coords2pix( 1, self.sji.pix2coords( 1, np.array([self.sji.shape[2],self.sji.shape[1]]) ) ) == np.array([self.sji.shape[2],self.sji.shape[1]]) )
        np.all( self.sji.pix2coords( 0, self.sji.coords2pix( 0, np.array([2800,ycen]), round_pixels=False ) ) - np.array([2800,ycen]) < 1e-10 ) 
        pixels = self.sji.coords2pix( 0, np.array([xcen,ycen]), round_pixels=False )
        np.abs( (pixels - np.array(self.sji.shape[1:])/2) / (np.array(self.sji.shape[1:])/2) ) < 0.1
        self.assertTrue( np.all( [np.min( self.sji.get_axis_coordinates(0)[0] ), np.min( self.sji.get_axis_coordinates(0)[1] )] - self.sji.pix2coords( 0, np.array([0,0]) ) == np.array([0,0])) )
        self.assertTrue( np.all( [np.max( self.sji.get_axis_coordinates(0)[0] ), np.max( self.sji.get_axis_coordinates(0)[1] )] - self.sji.pix2coords( 0, np.array([self.sji.shape[2],self.sji.shape[1]]) ) == np.array([0,0])) )        


        # Test whether pixels of stored coordinates are now offset by boundaries
        np.all( self.sji.coords2pix( 1, uncropped_cords ) == -np.array( [self.sji._xmin, self.sji._ymin] ) )
