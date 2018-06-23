import unittest
from irisreader import sji_cube, raster_cube, has_line

class test_has_line( unittest.TestCase ):
    
    def setUp( self ):
        self.sji_data = sji_cube( "irisreader/data/IRIS_SJI_test.fits" )
        self.raster_data = raster_cube( "irisreader/data/IRIS_raster_test1.fits" )
    
    def tearDown( self ):
        self.sji_data.close()
        self.raster_data.close()

    def test_function( self ):
        # SJI
        self.assertEqual( has_line( self.sji_data, "Mg II h/k" ), True )
        self.assertEqual( has_line( self.sji_data, "Si" ), False )
        self.assertEqual( has_line( "irisreader/data/IRIS_SJI_test.fits", "Mg II h/k" ), True )
        self.assertEqual( has_line( "irisreader/data/IRIS_SJI_test.fits", "Si" ), False )
        
        # Raster
        self.assertEqual( has_line( self.raster_data, "C II" ), True )
        self.assertEqual( has_line( self.raster_data, "Si IV 1403" ), False )
        self.assertRaises( ValueError, has_line, self.raster_data, "II" )
        self.assertEqual( has_line( "irisreader/data/IRIS_raster_test1.fits", "C II" ), True )
        self.assertEqual( has_line( "irisreader/data/IRIS_raster_test1.fits", "Si IV 1403" ), False )
        self.assertRaises( ValueError, has_line, "irisreader/data/IRIS_raster_test1.fits", "II" )