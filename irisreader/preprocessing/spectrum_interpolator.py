#!/usr/bin/env python

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from scipy.interpolate import interp1d

class spectrum_interpolator( BaseEstimator, TransformerMixin ):
    """
    Interpolates supplied spectra to a certain range and size using cubic splines.
    
    Parameters
    ----------
    lambda_min : float
        Minimum wavelength.
    lambda_max : float
        Maximum wavelength.
    steps : integer
        Number of interpolation steps.
    """
    
    def __init__( self, lambda_min, lambda_max, steps ):
        self._lambda_min = lambda_min
        self._lambda_max = lambda_max
        self._steps = steps
        self._f = lambda x: x
    
    # X are the signals, y are the units
    def fit( self, X, y ):
        """
        Creates a cubic spline function fitting the supplied spectrum data.
        
        Parameters
        ----------
        X : numpy.ndarray
            Array of spectra to interpolate (rows are different spectra and columns are wavelength bins)
        y: float
            List of wavelength units.
            
        Returns
        -------
        spectrum_interpolator
            This object with fitted variables.
        """
        self._f = interp1d( y, X, kind="cubic" )
        return self
    
    def transform( self, X ):
        """
        Interpolates the supplied spectrum data to the desired range and size.
        
        Parameters
        ----------
        X : numpy.ndarray
            Array of spectra to interpolate (rows are different spectra and columns are wavelength bins)
            
        Returns
        -------
        numpy.ndarray
            Array with interpolated spectra.
        """
        return self._f( np.linspace( self._lambda_min, self._lambda_max, num=self._steps ) )
    
    def get_coordinates( self ):
        """
        Gets the units of the interpolated spectrum.
        
        Returns
        -------
        float
            List of wavelengths for each bin.
        """
        return np.linspace( self._lambda_min, self._lambda_max, num=self._steps )