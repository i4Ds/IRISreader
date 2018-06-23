import unittest
from irisreader.obs_iterator import obs_iterator

class test_obs_iterator( unittest.TestCase ):
    
    def setUp( self ):
        self.obsit = obs_iterator( path="irisreader/data/" )

    def test_init( self ):
        self.assertEqual( len( self.obsit ), 1 )
        
    def test_iterations( self ):
        self.assertEqual( list( map( lambda obs: obs.n_raster, self.obsit ) ), [2] )


        
