#!/usr/bin/env python3

import pkg_resources
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestCentroid
from scipy.interpolate import interp1d

from irisreader.utils import date

DATA_PATH = pkg_resources.resource_filename( 'irisreader', 'data/' )

# default wavelength window
LAMBDA_MIN = 2793.8500976562500
LAMBDA_MAX = 2799.3239974882454

def get_mg2k_centroids( bins=216 ):
    """
    Returns Mg II k centroids found in the study
    'Identifying typical Mg II flare spectra using machine learning', by
    B. Panos et. al. 2018.
    
    The data contains 53 centroids with 216 wavelength bins between LAMBDA_MIN = 2793.8500976562500
    and LAMBDA_MAX = 2799.3239974882454.
    
    In order to assign an observed spectrum to a centroid, it has to be interpolated, normalized by dividing it through its maximum
    and then a 1-nearest neighbour method has to be used.
    
    Interpolation on a raster_cube instance::

        raster_image = raster.get_interpolated_image_step( 
                step = <step>, 
                lambda_min = LAMBDA_MIN, 
                lambda_max = LAMBDA_MAX, 
                n_breaks = 216 
                )
    
    Normalization::
    
        raster_image /= np.max( raster_image, axis=1 ).reshape(-1,1)
    
    Nearest neighbour assignment::
    
        from sklearn.neighbors import NearestCentroid
        knc = NearestCentroid()
        knc.fit( X=centroids, y=list( range( centroids.shape[0] ) ) )
        assigned_centroids = knc.predict( raster_image )
    
    Parameters
    ----------
    bins : int
        Number of bins to interpolate to (defaults to 216)
        
    
    Returns
    -------
    mg2k_centroids
        array with shape (216, 53)
    """
    
    # load centroids
    centroids = np.load( DATA_PATH + "/mg2k_centroids.npz" )['centroids'].T
    
    # interpolate centroids to other binsize if necessary
    if bins != 216:
        f = interp1d( np.linspace( 0, 1, num=centroids.shape[1] ), centroids )
        x_new = np.linspace( 0, 1, num=bins )
        centroids = f( x_new )
    
    # make sure centroids are properly divided by their maximum
    centroids = normalize( centroids )
    
    return centroids


def assign_mg2k_centroids( X, centroids=None ):
    """
    Assigns Mg II k centroids found in the study
    'Identifying typical Mg II flare spectra using machine learning', by
    B. Panos et. al. 2018 to the Mg II k spectra supplied in X. The centroids
    are assigned using a nearest neighbour procedure.
    
    The spectra in X have to be interpolated to 216 wavelength bins between 
    LAMBDA_MIN = 2793.8500976562500 and LAMBDA_MAX = 2799.3239974882454. For example::
        
        X = raster.get_interpolated_image_step( 
                step = <step>, 
                lambda_min = LAMBDA_MIN, 
                lambda_max = LAMBDA_MAX, 
                n_breaks = 216  
                )
    
    Parameters
    ----------
    X : numpy.array
        interpolated raster image of shape (_,bins)
    centroids : numpy.array
        If None, the centroids defined in the above study will be used, otherwise an array of shape (n_centroids, n_bins) should be passed.
        Important: both the spectra in 'X' and in 'centroids' should be constrained to the same wavelength region!
    
    Returns
    -------
    assigned_mg2k_centroids
        numpy vector with shape (X.shape[1],)
    """

    # load default centroids if no centroids are passed
    if centroids is None:
        centroids = get_mg2k_centroids( bins=X.shape[1] )

    # create list of numbered centroid ids        
    centroid_ids = list( range( centroids.shape[0] ) )
    
    # check whether X comes in the correct dimensions
    if not X.shape[1] == centroids.shape[1]:
        raise Exception( "Expecting X to have shape (_,{}). Please interpolate accordingly (More information with 'help(assign_mg2k_centroids)').".format( centroids.shape[1] ) )
    
    # create nearest centroid finder instance and fit it
    knc = NearestCentroid()
    knc.fit( X=centroids, y=centroid_ids )
    
    # predict nearest centroids for the supplied spectra
    # (making sure that X is normalized)
    assigned_mg2k_centroids = knc.predict( normalize(X) )

    # return vector of assigned centroids
    return assigned_mg2k_centroids    

def normalize( X ):
    """
    Divides each row of X by its maximum to make sure that the maximum value per row is 1.
    
    Parameters
    ----------
    X : numpy.array
        raster image to normalize
    """
    
    return X / np.max( X, axis=1 ).reshape(-1,1)

def interpolate( raster, step, bins=216, lambda_min=LAMBDA_MIN, lambda_max=LAMBDA_MAX ):
    """
    Returns an interpolated image step from the raster.
    
    Parameters
    ----------
    raster : irisreader.raster_cube
        raster_cube instance
    step : int
        image step in the raster
    bins : int
        number of bins to interpolate to (defaults to 216)
    lambda_min : float
        wavelength value where interpolation should start
    lambda_max : float
        wavelength value where interpolation should stop
        
    Returns
    -------
    assigned_mg2k_centroids
        numpy vector with shape (X.shape[1],)
    """
    
    # make sure we are dealing with a Mg II - raster
    if not "Mg II k" in raster.line_info:
        raise ValueError("This is not a Mg II k raster!")
    
    return raster.get_interpolated_image_step( 
        step = step, 
        lambda_min = lambda_min, 
        lambda_max = lambda_max, 
        n_breaks = bins 
    )

def get_mg2k_centroid_table( obs, centroids=None, lambda_min=LAMBDA_MIN, lambda_max=LAMBDA_MAX, crop_raster=False ):
    """
    Returns a data frame with centroid counts for each raster image of a given
    observation.
    
    Parameters
    ----------
    obs_path : str
        Path to observation
    centroids : numpy.array
        if None, the centroids defined in the above study will be used, otherwise an array of shape (n_centroids, n_bins) should be passed
    lambda_min : float
        wavelength value where interpolation should start
    lambda_max : float
        wavelength value where interpolation should stop
    crop_raster : bool
        Whether to crop raster before assigning centroids. If set to False,
        spectra which are -200 everywhere will be assigned to centroid 51 and
        spectra that are for some part -200 will be assigned to the nearest
        centroid.
    
    Returns
    -------
    centroids_df : pd.DataFrame
        Data frame with image ids and assigned centroids
    assigned_centroids : list
        List with array of assigned centroids for every raster image
    """   
    
    # open raster and crop it if desired
    if not obs.raster.has_line("Mg II k"):
        raise Exception("This observation contains no Mg II k line")
    
    raster = obs.raster("Mg II k")
    
    if crop_raster:
        raster.crop()

    # infer number of centroids and number of bins
    if centroids is None:
        n_centroids = 53
        bins = 216
    else:
        n_centroids = centroids.shape[0]
        bins = centroids.shape[1]
    
    # get goes flux
    try:
        goes_flux = raster.get_goes_flux()
    except Exception as e:
        print("Could not get GOES flux - setting to None")
        goes_flux = [None] * raster.n_steps
    
    # empty list for assigned centroids
    assigned_centroids = []
    
    # empty data frame for centroid counts
    df = pd.DataFrame( columns=["full_obsid", "date", "image_no", "goes_flux", "centroid", "count"] )
    
    # assign centroids for each image and create aggregated data frame
    for step in range( raster.n_steps ):

        # fetch assigned centroids            
        img = interpolate( raster, step, bins=bins, lambda_min=lambda_min, lambda_max=lambda_max )
        img_assigned_centroids = assign_mg2k_centroids( img, centroids=centroids )
        assigned_centroids.append( img_assigned_centroids )
        
        # count centroids
        recovered_centroids, counts = np.unique( img_assigned_centroids, return_counts=True )
        
        # append to data frame
        df = df.append( 
                pd.DataFrame(
                        {'full_obsid': obs.full_obsid, 
                         'date': date.from_Tformat( raster.headers[step]['DATE_OBS'] ), 
                         'image_no': step, 
                         'goes_flux': goes_flux[step],
                         'centroid': recovered_centroids, 
                         'count': counts }
                        ),
                sort = False
            )
    
    # create pivot table
    df = df.pivot_table(index=['full_obsid', 'date', 'image_no', 'goes_flux'], columns='centroid', values='count', aggfunc='first', fill_value=0 )
    df.reset_index( inplace=True )
    
    
    # make sure all centroids are represented
    for i in range( n_centroids ):
        if i not in df:
            df[i] = 0
    
    # make sure columns are sorted
    df = df.reindex( ["full_obsid", "date", "image_no", "goes_flux"] + [i for i in range(n_centroids)], axis=1 )
    df.columns.name = ''
    
    # rename number columns into string columns
    cols = df.columns.values
    cols[4:] = ["c" + str(col) for col in df.columns[4:]]
    df.columns = cols
    
    # close observation
    obs.close()
    
    # return data frame
    return df, assigned_centroids

# MOVE TO TEST
if __name__ == "__main__":
    #from irisreader.data import sample_raster
    #raster = sample_raster()
    #compare_plot( raster, 2, 10 )
    
    from irisreader import observation
    obs_path = '/home/chuwyler/Desktop/FITS/20140128_073021_3860259280/'
    d, c = get_mg2k_centroid_table( observation( obs_path ) )
    
    new_centroids = get_mg2k_centroids()[:10,:]
    d, c = get_mg2k_centroid_table( observation( obs_path ), centroids=new_centroids )
