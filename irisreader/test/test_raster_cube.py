import unittest
from irisreader.raster_cube import raster_cube

class test_raster_cube( unittest.TestCase ):
    
    def setUp( self ):
        self.raster_data = raster_cube( 'irisreader/data/IRIS_raster_test1.fits', line='Mg' )

    def tearDown( self ):
        self.raster_data.close()

    def test_init( self ):
        self.assertEqual( self.raster_data.n_steps, 3 )
        self.assertEqual( self.raster_data.type, 'raster' )
        self.assertRaises( ValueError, raster_cube, 'irisreader/data/IRIS_SJI_test.fits' )
        self.assertEqual( len( self.raster_data.primary_headers ), 215 )
        self.assertEqual( self.raster_data.time_specific_headers[2]['DATE_OBS'], '2014-03-29T14:09:58.000' )
    
    def test_prepare_combined_headers( self ):
        self.assertEqual( self.raster_data.headers[2]['XCEN'], self.raster_data.headers[2]['XCENIX'] )
        self.assertEqual( self.raster_data.headers[2]['WAVELNTH'], self.raster_data.headers[1]['WAVELNTH'] )
        self.assertEqual( self.raster_data.headers[2]['DATE_OBS'], self.raster_data.headers[2]['DATE_OBS'] )

    def test_get_units( self ):
        self.assertEqual( len(self.raster_data.get_units(2)), 2 )
        self.assertEqual( self.raster_data.get_units(2)[0][100], 2793.035286670886 )
        self.assertEqual( self.raster_data.get_units(2)[1][100], 207.4379752954392 )