#!/usr/bin/env python

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from astropy.convolution import Gaussian1DKernel, convolve

class spectrum_smoother( BaseEstimator, TransformerMixin ):
    """
    Smoothes supplied noisy spectra using a Gaussian kernel.
    
    Parameters
    ----------
    method : string
        Smoothing method - currently only "gaussian_blur" is supported.
    width : float
        Width parameter of the Gaussian kernel.
    """
    
    def __init__( self, method="gaussian_blur", width=1 ):
        self._method = method
        self._width = width
        
    def fit( self, X, y=None ):
        """Does nothing."""
        return self
    
    def transform( self, X ):      
        """Convolves the Gaussian kernel with the array of spectra.
        
        Parameters
        ----------
        X : numpy.ndarray
            Array of spectra to smooth (rows are different spectra and columns are wavelength bins)
            
        Returns
        -------
        numpy.ndarray
            Array with smoothed spectra.
        """
        if self._method == "gaussian_blur":
            smoothed_signals = np.zeros( X.shape )
            gauss_kernel = Gaussian1DKernel( stddev = self._width )
            for i in range( X.shape[0] ):
                 smoothed_signals[i,:] = convolve(X[i,:], gauss_kernel)
            return smoothed_signals
    