#!/usr/bin/env python

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import irisreader as ir
from irisreader.preprocessing import image_cropper, CorruptImageException, NullImageException

class image_cube_cropper( BaseEstimator, TransformerMixin ):
    """Implements a transformer that can crop all images of an observed line 
    (be it SJI or spectra) by applying image_cropper to every individual
    image and identifying corrupt images and outliers.
    
    Corrupt images can either be identified directly when :py:class:`image_cropper`
    throws an error because more than 5% of the pixels of the border or the
    overall image are negative or, however, they can appear as outliers in the
    bound data returned by :py:class:`image_cropper`: sometimes whole stripes of
    data are corrupt, resulting in a rectangular image with for example half the
    width and the height of the valid image. We thus look for outliers in the data
    returned by :py:class:`image_cropper` and degrade them to corrupt images.
    Outliers are defined here as values that deviate more than 1.5% from the 
    median bound (15 pixels on 1000 pixels).
    
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
        self._data_cube_object = None
        self._offset = offset
        self._check_coverage = check_coverage
        self._corrupt_images = []
        self._null_images = []

    # function to crop a single image (in order to parallelize it later)
#    def _crop_image( self, step ):
#        cropper = image_cropper( offset=self._offset )
#        image_bounds = []
#        corrupt_images = []
#        null_images = []
#
#        try:
#            cropper.fit( self._data_cube_object.get_image_step( step ) )
#            image_bounds = cropper.get_bounds()
#            
#        except CorruptImageException:
#            image_bounds = [0,0,0,0]
#            corrupt_images.append( step )
#            
#        except NullImageException:
#            image_bounds = [0,0,0,0]
#            null_images.append( step )
#            
#        return image_bounds, corrupt_images, null_images
    
    # fit method: find boundaries
    def fit( self, X, y=None ):
        """
        Determines the overall cropping bounds and the corrupt images for the supplied data cube.
        
        Parameters
        ----------
        X : irisreader.iris_data_cube (irisreader.sji_cube / irisreader.raster_cube)
            Data cube object that has to be cropped.
        
        Returns
        -------
        image_cube_cropper
            This object with fitted variables.
        """
        
        # make sure only iris_data_cube objects are taken as input
        if isinstance( X, ir.iris_data_cube ) or isinstance( X, ir.sji_cube ) or isinstance( X, ir.raster_cube ):
            self._data_cube_object = X
        else:
            raise ValueError("This is not a valid data cube object.")
        
        # make sure observation is a sit-and-stare if the observation is a slit-jaw image
        if self._data_cube_object.type == 'sji' and self._data_cube_object.mode != "sit-and-stare":
            raise ValueError("Only sit-and-stare observation can be cropped as a cube!")
        
        # set up image cropper
        cropper = image_cropper( offset=self._offset, check_coverage=self._check_coverage )
        
        # get bounds on all images in the cube and store null and corrupt images
        image_bounds = []
        
        for step in range( self._data_cube_object.n_steps ):
            try:
                cropper.fit( self._data_cube_object.get_image_step( step ) )
                image_bounds.append( cropper.get_bounds() )
            
            except CorruptImageException:
                image_bounds.append( [0,0,0,0] )
                self._corrupt_images.append( step )
            
            except NullImageException:
                image_bounds.append( [0,0,0,0] )
                self._null_images.append( step )
                
        
#        pool = multiprocessing.Pool()
#        res = pool.map( self._crop_image, range( self._data_cube_object.n_steps ) )
#        
#        return res
        
        image_bounds = np.vstack( image_bounds )
        
        # define outliers as values that deviate more than 1.5% from the 
        # median bound (20 pixels on 1000 pixels)
        # TODO: how to put this onto a more rigourous footing?
        outlier_threshold = 0.02
        width, height = self._data_cube_object.get_image_step( 0 ).shape
        outlier_score = np.max(np.abs(image_bounds - np.median(image_bounds, axis=0)) / (np.array([width, width, height, height])), axis=1)
        
        # add outliers to corrupt images and remove null images from corrupt images
        self._corrupt_images += ( np.where( outlier_score >= outlier_threshold )[0].tolist() )
        self._corrupt_images = sorted( list( set( self._corrupt_images ) - set( self._null_images ) ) )
        self._null_images = sorted( self._null_images )
        
        # set boundaries as the value closest to the center of the image of all
        # the inlier images
        self._xmin = np.max( image_bounds[outlier_score < outlier_threshold, 0] )
        self._xmax = np.min( image_bounds[outlier_score < outlier_threshold, 1] )
        self._ymin = np.max( image_bounds[outlier_score < outlier_threshold, 2] )
        self._ymax = np.min( image_bounds[outlier_score < outlier_threshold, 3] )
        
        return self
        
    # function to return boundaries
    def get_bounds( self ):
        """
        Gets the overall bounds recovered by image_cube_cropper.
        
        Returns
        -------
        int
            List [ xmin, xmax, ymin, ymax ] for the given data cube.
        """
        if self._data_cube_object is None:
            raise ValueError("Please pass a data cube first using the fit method.")
        else:
            return [self._xmin, self._xmax, self._ymin, self._ymax]
    
    # function to return corrupt images
    def get_corrupt_images( self ):
        """
        Gets time-step indices of corrupt images in the data cube.
        
        Returns
        -------
        int
            Time-step indices of corrupt images in the data cube.
        """
        if self._data_cube_object is None:
            raise ValueError("Please pass a data cube first using the fit method.")
        else:
            return self._corrupt_images

    # function to return corrupt images
    def get_null_images( self ):
        """
        Gets time-step indices of null images in the data cube (if any, usually data cubes are read with keep_null=False).
        
        Returns
        -------
        int
            Time-step indices of null images in the data cube.
        """
        if self._data_cube_object is None:
            raise ValueError("Please pass a data cube first using the fit method.")
        else:
            return self._null_images
        
# Test code
if __name__ == "__main__":
    
    from irisreader import observation
    obs = observation( "/home/chuwyler/Desktop/FITS/20140906_112339_3820259253/" )
    sji = obs.sji[0]
    
    sji.plot(0)
    
    cropper = image_cube_cropper()
    cropper.fit( sji )

    sji._set_bounds( cropper.get_bounds() )
    sji.n_steps
    sji._remove_steps( cropper.get_null_images() )
    sji.n_steps
    sji._remove_steps( cropper.get_corrupt_images() )
    sji.n_steps

    sji.plot(400)


    raster3_dir = "/home/chuwyler/Desktop/FITS/20150404_155958_3820104165"
    raster3_files = sorted( [raster3_dir + "/" + file for file in os.listdir( raster3_dir ) if 'raster' in file] )
    raster3 = raster_cube( raster3_files, line="Mg" )
    raster3.plot(0)

    cropper = image_cube_cropper()
    cropper.fit( raster3 )