import unittest
from irisreader.combined_raster import combined_raster

class test_combined_raster( unittest.TestCase ):
    
    def setUp( self ):
        self.raster_data = combined_raster( ['irisreader/data/IRIS_raster_test1.fits', 'irisreader/data/IRIS_raster_test2.fits'], line='Fe' )

    def tearDown( self ):
        self.raster_data.close()

    def test_init( self ):
        self.assertEqual( self.raster_data.n_steps, 6 )
        self.assertEqual( self.raster_data.n_raster_steps, [3,3] )
        self.assertEqual( self.raster_data.n_raster, 2 )
        self.assertEqual( self.raster_data.type, 'raster' )
        self.assertEqual( len( self.raster_data.primary_headers ), 215 )
        self.assertEqual( self.raster_data.time_specific_headers[4]['DATE_OBS'], '2014-03-29T14:10:16.530' )
        self.assertEqual( self.raster_data.line_specific_headers['WAVELNTH'], 1349.43005371 )
        self.assertEqual( self.raster_data.primary_headers['STARTOBS'], '2014-03-29T14:09:38.830' )

    def test_prepare_combined_headers( self ):
        self.assertEqual( self.raster_data.headers[4]['XCEN'], self.raster_data.headers[4]['XCENIX'] )
        self.assertEqual( self.raster_data.headers[4]['WAVELNTH'], self.raster_data.headers[1]['WAVELNTH'] )
        
    def test_get_units( self ):
        self.assertEqual( self.raster_data.get_units(4)[0][100], 1350.277130314 )
        self.assertEqual( self.raster_data.get_units(4)[1][100], 207.4126750779641 )
        
    def test_get_image_step( self ):
        self.assertEqual( self.raster_data.get_image_step(3)[50,400], 5.75 )
    
    def test_get_timestamps( self ):
        self.assertEqual( self.raster_data.get_timestamps(), [1396102179.0, 1396102188.56, 1396102198.0, 1396102207.38, 1396102216.53, 1396102225.91]  )

    def test_get_nsatpix( self ):
        self.assertEqual( self.raster_data.get_nsatpix( 4 ), 0 )
        
    def test_copy( self ):
        raster_data_copy = self.raster_data.copy()
        self.assertEqual( raster_data_copy is self.raster_data, False )
        for i in range( len( self.raster_data._raster_data ) ):
            self.assertEqual( self.raster_data._raster_data[i] is raster_data_copy._raster_data[i], False  )
