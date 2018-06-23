import unittest
from irisreader.sji_cube import sji_cube
from .header_regression_test import header_regression_test, read_saved_headers, headers_to_exclude_sji

class test_sji_cube( unittest.TestCase ):
    
    def setUp( self ):
        self.sji_data = sji_cube( 'irisreader/data/IRIS_SJI_test.fits' )
    
    def tearDown( self ):
        self.sji_data.close()

    def test_init( self ):
        self.assertEqual( self.sji_data.n_steps, 3 )
        self.assertEqual( self.sji_data.type, 'sji' )
        self.assertRaises( ValueError, sji_cube, 'irisreader/data/IRIS_raster_test1.fits' )
        self.assertEqual( len( self.sji_data.primary_headers ), 147 )   
        self.assertEqual( self.sji_data.time_specific_headers[2]['DATE_OBS'], '2014-03-29T14:10:25.840' )
    
    def test_prepare_combined_headers( self ):
        self.assertEqual( self.sji_data.headers[2]['XCEN'], self.sji_data.headers[2]['XCENIX'] )

    def test_get_units( self ):
        self.assertEqual( len(self.sji_data.get_units(2)), 2 )
        self.assertEqual( self.sji_data.get_units(2)[0][100], 415.56120481526864 )
        self.assertEqual( self.sji_data.get_units(2)[1][100], 207.44186272392008 )