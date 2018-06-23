import unittest
from irisreader.iris_data_cube import iris_data_cube

class test_iris_data_cube( unittest.TestCase ):
    
    def setUp( self ):
        self.fits_data = iris_data_cube( 'irisreader/data/IRIS_SJI_test.fits' )
        
    def tearDown( self ):
        self.fits_data.close()
        
    def test_init( self ):
        self.assertEqual( self.fits_data.obsid, '3860258481' )
        self.assertEqual( self.fits_data.date, '2014-03-29' )
    
    def test_prepare_valid_images( self ):
        self.assertEqual( self.fits_data.n_steps, 3 )    
        self.assertEqual( self.fits_data._valid_images, [0,1,2] )
    
    def test_prepare_primary_headers( self ):
        self.assertEqual( self.fits_data.primary_headers['CDELT1'], 0.16635 )
    
    def test_prepare_time_specific_headers( self ):
        self.assertEqual( self.fits_data.time_specific_headers[1]['DATE_OBS'], '2014-03-29T14:10:07.310' )
        self.assertEqual( len( self.fits_data.time_specific_headers ), len( self.fits_data._valid_images ) )
        
    def test_get_image_step( self ):
        self.assertEqual( self.fits_data.get_image_step( 1 )[400,400], 305.75 )        
    
    def test_get_nsatpix( self ):
        self.assertEqual( self.fits_data.get_nsatpix( 0 ), 0 )
   
    def test_get_timestamps( self ):
        self.assertEqual( self.fits_data.get_timestamps(), [1396102188.49, 1396102207.31, 1396102225.84] )     
        
    def test_copy( self ):
        self.assertEqual( self.fits_data.copy() is self.fits_data, False  )