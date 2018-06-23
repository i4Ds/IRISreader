import unittest
from irisreader.observation import observation
from .header_regression_test import header_regression_test, read_saved_headers, headers_to_exclude_raster, headers_to_exclude_sji

class test_observation( unittest.TestCase ):
    
    def setUp( self ):
        self.obs = observation( 'irisreader/data/20140518_151415_3820607204', keep_null=True )

    def tearDown( self ):
        self.obs.close()

    def test_init( self ):
        self.assertEqual( self.obs.raster("Fe").n_steps, 6 )
        self.assertEqual( self.obs.sji[0].n_steps, 3 )
        self.assertEqual( self.obs.n_raster, 2 )
        self.assertEqual( self.obs.n_sji, 1 )

    def test_get_lines( self ):
        self.assertEqual( len(self.obs.sji.get_lines()), 1 )
        self.assertEqual( len(self.obs.raster.get_lines()), 3 )
        
    def test_has_line( self ):
        self.assertEqual( self.obs.sji.has_line("Mg II h/k"), True )
        self.assertEqual( self.obs.sji.has_line("C II"), False )
        self.assertEqual( self.obs.raster.has_line("C II"), True )
        self.assertEqual( self.obs.raster.has_line("Si"), False )
        self.assertRaises( ValueError, self.obs.raster.has_line, "II" )
        
    def test_regression( self ):
        print("\n--------------------------------------------------------------------")
        print("Performing regression test with headers preprocessed by read_iris_l2")
        print("--------------------------------------------------------------------")

        # SJI File
        irisreader_headers = self.obs.sji[0].headers
        idl_headers = read_saved_headers( 'irisreader/data/sji_headers.sav'  )
        header_regression_test( irisreader_headers, idl_headers, headers_to_exclude_sji )
   
        # Combined raster (all three lines)
        irisreader_headers = self.obs.raster[0].headers
        idl_headers = read_saved_headers( 'irisreader/data/raster1_headers_ext0.sav'  ) + read_saved_headers( "irisreader/data/raster2_headers_ext0.sav" )
        header_regression_test( irisreader_headers, idl_headers, headers_to_exclude_raster )
   
        irisreader_headers = self.obs.raster[1].headers
        idl_headers = read_saved_headers( 'irisreader/data/raster1_headers_ext1.sav'  ) + read_saved_headers( "irisreader/data/raster2_headers_ext1.sav" )
        header_regression_test( irisreader_headers, idl_headers, headers_to_exclude_raster )
  
        irisreader_headers = self.obs.raster[2].headers
        idl_headers = read_saved_headers( 'irisreader/data/raster1_headers_ext2.sav'  ) + read_saved_headers( "irisreader/data/raster2_headers_ext2.sav" )
        header_regression_test( irisreader_headers, idl_headers, headers_to_exclude_raster )        
