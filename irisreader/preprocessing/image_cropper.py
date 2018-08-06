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
    check_coverage : boolean
        Whether to check the coverage of the cropped image. It can happen that
        there are patches of negative values in images, either due to loss of
        data during transmission (typically a band or a large rectangular patch 
        of negative data) or due to overall low data counts (missing data is no
        data). 
        image_cropper labels an image as corrupt if >5% of its pixels are still
        negative after cropping. This might be problematic for lines with low 
        data counts (and therefore many missing pixels) and the user is advised 
        to disable the coverage check for such lines. 
        A method that is able to distinguish missing data arising from 
        transmission errors from missing data due to low data counts could be 
        helpful here.
    """
    
    # constructor
    def __init__( self, offset=0, check_coverage=True ):
        self._xmin = self._xmax = self._ymin = self._ymax = 0
        self._image_ref = None
        self._offset = offset
        self._check_coverage = check_coverage

    # fit method: find boundaries
    def fit( self, X, y=None ):
        """
        Determines bounds for the supplied image with the sliding lines approach
        mentioned in the class description.
        
        Parameters
        ----------
        X : numpy.ndarray
            2D image data that is to be cropped, format [y,x]
        
        Returns
        -------
        image_cropper
            Returns this object with fitted variables.
        """
        
        # set image reference for access outside the fit function
        self._image_ref = X

        # raise exception if the image is NULL (-200) everywhere
        if np.all( self._image_ref < 0 ):
            raise NullImageException("Null image cannot be cropped")
        
        # functions to get bounds on the image from all sides:
        # A line is moved from the outside towards the center until the number 
        # of nonzero pixels stops increasing 
        def get_lower_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[1] ):
                nonzero_pixels = np.sum( image[:,i] >= 0 )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return i
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[1]

        def get_upper_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[1] ):
                nonzero_pixels = np.sum( image[:,image.shape[1]-i-1] >= 0 )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return image.shape[1]-i
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[1]

        def get_left_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[0] ):
                nonzero_pixels = np.sum( image[i,:] >= 0 )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return i
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[0]
        
        def get_right_bound( image ):
            previous_nonzero_pixels = 0
            for i in range( image.shape[0] ):
                nonzero_pixels = np.sum( image[image.shape[0]-i-1,:] >= 0 )
                if nonzero_pixels > 0 and previous_nonzero_pixels-nonzero_pixels>=0 and i>0:
                    return image.shape[0]-i
        
                previous_nonzero_pixels = nonzero_pixels
            return image.shape[0]

        # set image boundaries (plus add a possible defined offset)
        self._xmin = get_lower_bound( self._image_ref ) + self._offset
        self._xmax = get_upper_bound( self._image_ref ) - self._offset
        self._ymin = get_left_bound( self._image_ref ) + self._offset
        self._ymax = get_right_bound( self._image_ref ) - self._offset
        
        # raise a corrupt image exception if more than 5% of the image or the
        # image border are still negative
        # This check can be disable with check_coverage = False
        if self._check_coverage:
            if np.mean( self._image_ref[self._ymin:self._ymax,self._xmin:self._xmax] < 0 ) > 0.05:
                raise CorruptImageException("Image might contain a corrupt patch, more than 5% have a negative pixel value!")
        
            if np.mean( self._image_ref[self._ymin,self._xmin:self._xmax] < 0 ) > 0.05 or np.mean( self._image_ref[self._ymax,self._xmin:self._xmax] < 0 ) > 0.05 or np.mean( self._image_ref[self._ymin:self._ymax,self._xmin] < 0 ) > 0.05 or np.mean( self._image_ref[self._ymin:self._ymax,self._xmax] < 0 ) > 0.05:
                raise CorruptImageException("Image border contains more than 5% negative pixels!")
        
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
            return X[ self._ymin:self._ymax, self._xmin:self._xmax ] 
    
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
    
    # helper function: plot image with boundary
    def plot_bounding_boxed( self ):
        """Plots the supplied image and places a bounding box around it."""
        if self._image_ref is None:
            raise ValueError("Please pass an image first using the fit method.")
        else:
            plt.imshow( self._image_ref.clip(min=0)**0.4, cmap="gist_heat", vmax=10, origin="lower" )
            plt.plot( [self._xmin,self._xmax], [self._ymin,self._ymin], color='white' ); plt.plot( [self._xmin,self._xmax], [self._ymax,self._ymax], color='white' ) 
            plt.plot( [self._xmax,self._xmax], [self._ymin,self._ymax], color='white' ); plt.plot( [self._xmin, self._xmin], [self._ymin,self._ymax], color='white' )
            plt.show()

# Exception classes for null images and corrupt images
class NullImageException(Exception):
    pass
class CorruptImageException(Exception):
    pass

# Test code
if __name__ == "__main__":
    
    from irisreader import observation
    
    obs = observation( "/home/chuwyler/Desktop/FITS/20140906_112339_3820259253/" )
    X = obs.sji[0].get_image_step( 0 )
    plt.imshow( X.clip(min=0)**0.4, cmap="gist_heat", origin="lower", vmax=7 )

    cropper = image_cropper()
    X_cropped = cropper.fit_transform( X )

    plt.imshow( X_cropped.clip(min=0)**0.4, cmap="gist_heat", origin="lower", vmax=7 )
