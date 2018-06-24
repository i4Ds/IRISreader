import unittest
from irisreader.iris_data_cube import iris_data_cube
from irisreader.data.sample import DATA_PATH

class test_iris_data_cube( unittest.TestCase ):
    
    def setUp( self ):
        self.fits_data = iris_data_cube( DATA_PATH + '/IRIS_raster_test1.fits' )
        
    def tearDown( self ):
        self.fits_data.close()
        
    def test_init( self ):
        self.assertEqual( self.fits_data.type, 'raster' )
        self.assertEqual( self.fits_data.obsid, '3860258481' )
        self.assertEqual( self.fits_data.mode, 'n-step raster' )
        
    def test_prepare_valid_images( self ):
        self.assertEqual( self.fits_data.n_steps, len( self.fits_data._valid_images) )    
        self.assertEqual( self.fits_data.n_steps, self.fits_data.shape[0] )
    
    def test_prepare_primary_headers( self ):
        self.assertEqual( type(self.fits_data.primary_headers), dict )
        self.assertGreater( len(self.fits_data.primary_headers), 1  )
    
    def test_prepare_time_specific_headers( self ):
        self.assertEqual( type(self.fits_data.time_specific_headers[1]), dict )
        self.assertGreater( len(self.fits_data.time_specific_headers[1]), 1 )   
        self.assertEqual( len( self.fits_data.time_specific_headers ), self.fits_data.n_steps )
        
    def test_get_data( self ):
        self.assertEqual( self.fits_data[:,:,:].shape, self.fits_data.shape )
        self.assertEqual( self.fits_data[0,:,:].shape, self.fits_data.get_image_step(0, divide_by_exptime=False).shape )
        self.assertEqual( self.fits_data.shape, self.fits_data._fits_file[self.fits_data._selected_ext].shape )
    
    def test_get_nsatpix( self ):
        self.assertEqual( self.fits_data.get_nsatpix( 0 ), 0 )
   
    def test_get_timestamps( self ):
        self.assertEqual( len( self.fits_data.get_timestamps() ), self.fits_data.n_steps )     
        
    def test_copy( self ):
        self.assertFalse( self.fits_data.copy() is self.fits_data  )
        
    def test_get_foes_flux( self ):
        self.assertEqual( len(self.fits_data.get_goes_flux()), self.fits_data.n_steps )
        
    def test_crop( self ):
        cropped = self.crop( inplace=False )
        self.assertIsNotNone( cropped._xmin )
        self.assertIsNotNone( cropped._xmax )
        self.assertIsNotNone( cropped._ymin )
        self.assertIsNotNone( cropped._ymax )
        self.assertIsTrue( cropped._cropped )