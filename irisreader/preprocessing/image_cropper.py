#!/usr/bin/env python

# import libraries
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import matplotlib.pyplot as plt

class image_cropper( BaseEstimator, TransformerMixin ):
    """Implements a transformer that cuts out only the non-null regions of an
    IRIS image (be it SJI or spectra). Null pixels of the image are encoded as
    -200.
    
    The bounds are found by moving in lines from all sides towards the center
    until the number of nonzero pixels stops increasing. To make sure everything
    worked well, the cropped image is checked for negative pixels at the end,
    throwing an error if more than 5% of the image border pixels or the whole image
    are negative. In this way, bounds for the image are determined with the `fit`
    method while the `transform` method returns a the cropped image.
    
    Parameters
    ----------
    offset : integer
        Number of pixels that are removed as a safety border from all sides
        after the cropping.
    
    """
    
    # constructor
    def __init__( self, offset=0 ):
        self._xmin = self._xmax = self._ymin = self._ymax = 0
        self._image_ref = None
        self._offset = offset

    # fit method: find boundaries
    def fit( self, X, y=None ):
        """
        Determines bounds for the supplied image with the sliding lines approach
        mentioned in the class description.
        
        Parameters
        ----------
        X : numpy.ndarray
            2D image data that is to be cropped.
        
        Returns
        -------
        image_cropper
            Returns this object with fitted variables.
        """
        
        # set image reference for access outside the fit function
        self._image_ref = np.transpose( X ) # images are usually in the format [y,x]
        
        # define NULL
        NULL = -200
        
        # raise exception if the image is NULL (-200) everywhere
        if np.all( self._image_ref==NULL ):
            raise NullImageException("Null image cannot be cropped")
        
        # functions to get bounds on the image from all sides:
        # A line is moved from the outside towards the center until the number 
        # of nonzero pixels stops increasing 
        def get_lower_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[1] ):
                nonzero_pixels = np.sum( image[:,i] > NULL )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return i
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[1] #i?

        def get_upper_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[1] ):
                nonzero_pixels = np.sum( image[:,image.shape[1]-i-1] > NULL )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return image.shape[1]-i
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[1]

        def get_left_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[0] ):
                nonzero_pixels = np.sum( image[i,:] > NULL )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return i
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[0]

        def get_right_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[0] ):
                nonzero_pixels = np.sum( image[image.shape[0]-i-1,:] > NULL )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return image.shape[0]-i
        
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[0]

        # set image boundaries (plus add a possible defined offset)
        self._ymin = get_lower_bound( self._image_ref ) + self._offset
        self._ymax = get_upper_bound( self._image_ref ) - self._offset
        self._xmin = get_left_bound( self._image_ref ) + self._offset
        self._xmax = get_right_bound( self._image_ref ) - self._offset
        
        # raise a corrupt image exception if more than 5% of the image or the
        # image border are still NULL
        if np.mean( self._image_ref[self._xmin:self._xmax,self._ymin:self._ymax] == NULL ) > 0.05:
            raise CorruptImageException("Image might contain a corrupt patch, more than 5% have value -200!")
        
        if np.mean( self._image_ref[self._xmin,self._ymin:self._ymax]==NULL ) > 0.05 or np.mean( self._image_ref[self._xmax,self._ymin:self._ymax]==NULL ) > 0.05 or np.mean( self._image_ref[self._xmin:self._xmax,self._ymin]==NULL ) > 0.05 or np.mean( self._image_ref[self._xmin:self._xmax,self._ymax]==NULL ) > 0.05:
            raise CorruptImageException("Image border contains more than 5% of -200 pixels!")
        return self
    
    
    # transform method: return bounded image
    def transform( self, X ):
        """Returns the bounded image.
        
        Parameters
        ----------
        X : numpy.ndarray
            2D image data that is to be cropped.
        
        Returns
        -------
        numpy.ndarray
            Cropped image data.
        """
        if self._image_ref is None:
            raise ValueError("Please pass an image first using the fit method.")
        else:
            return X[ self._xmin:self._xmax, self._ymin:self._ymax ] # <---------------------------------------------------------------------------!!!!
            # question: does this really make sense? or how should images be passed?
    
    # function to return bounds computed by the fit function
    def get_bounds( self ):
        """
        Gets the bounds computed by image_cropper.
        
        Returns
        -------
        int
            List [ xmin, xmax, ymin, ymax ] for the given image.
        """
        if self._image_ref is None:
            raise ValueError("Please pass an image first using the fit method.")
        else:
            return [self._xmin, self._xmax, self._ymin, self._ymax]
    
    # function to return bounded coordinates
    def transform_coordinates( self, coordinates ):
        """
        Gets the coordinates of the cropped image.
        
        Parameters
        ----------
        units : float
            List of coordinates of the original image (via :py:meth:`sji_cube.get_coordinates()` or :py:meth:`raster_cube.get_coordinates()`).
        
        Returns
        -------
        float
            List [coordinates along first axis, coordinates along second axis].
        """
        return [ coordinates[0][self._xmin:self._xmax], coordinates[1][self._ymin:self._ymax] ]
    
    # helper function: plot image with boundary
    def plot_bounding_boxed( self ):
        """Plots the supplied image and places a bounding box around it."""
        if self._image_ref is None:
            raise ValueError("Please pass an image first using the fit method.")
        else:
            plt.imshow( np.transpose( self._image_ref ), cmap="gist_heat", vmax=900, origin="lower" )
            plt.plot( [self._xmin,self._xmax], [self._ymin,self._ymin], color='white' ); plt.plot( [self._xmin,self._xmax], [self._ymax,self._ymax], color='white' ) 
            plt.plot( [self._xmax,self._xmax], [self._ymin,self._ymax], color='white' ); plt.plot( [self._xmin, self._xmin], [self._ymin,self._ymax], color='white' )
            plt.show()

# Exception classes for null images and corrupt images
class NullImageException(Exception):
    pass
class CorruptImageException(Exception):
    pass


