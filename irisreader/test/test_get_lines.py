import unittest
from irisreader import sji_cube, raster_cube, get_lines

class test_get_lines( unittest.TestCase ):
    
    def setUp( self ):
        self.sji_data = sji_cube( 'irisreader/data/IRIS_SJI_test.fits' )
        self.raster_data = raster_cube( 'irisreader/data/IRIS_raster_test1.fits' )
    
    def tearDown( self ):
        self.sji_data.close()
        self.raster_data.close()

    def test_function( self ):
        self.assertEqual( get_lines( self.sji_data )['description'][0], 'Mg II h/k 2796' )
        self.assertEqual( get_lines( self.sji_data )['description'][0], get_lines( 'irisreader/data/IRIS_SJI_test.fits'  )['description'][0] )    
        
        self.assertEqual( get_lines( self.raster_data )['description'].tolist(), ['C II 1336', 'Fe XII 1349', 'Mg II k 2796'] )
        self.assertEqual( get_lines( self.raster_data )['description'].tolist(), get_lines( 'irisreader/data/IRIS_raster_test1.fits' )['description'].tolist() )
 
