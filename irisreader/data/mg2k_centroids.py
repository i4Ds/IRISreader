#!/usr/bin/env python3

import pkg_resources
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestCentroid
from scipy.interpolate import interp1d

from irisreader.utils import date

DATA_PATH = pkg_resources.resource_filename( 'irisreader', 'data/' )

# wavelength window
LAMBDA_MIN = 2793.8500976562500
LAMBDA_MAX = 2799.3239974882454

# number of centroids
N_CENTROIDS = 53

def get_mg2k_centroids( bins=216 ):
    """
    Returns Mg II k centroids found in the study
    'Identifying typical Mg II flare spectra using machine learning', by
    B. Panos et. al. 2018.
    
    The data contains 53 centroids with 216 wavelength bins between LAMBDA_MIN = 2793.8500976562500
    and LAMBDA_MAX = 2799.3239974882454.
    
    In order to assign an observed spectrum to a centroid, it has to be interpolated, normalized by dividing it through its maximum
    and then a 1-nearest neighbour method has to be used.
    
    Interpolation on a raster object:
    ```
    raster_image = raster.get_interpolated_image_step( 
        step = <step>, 
        lambda_min = LAMBDA_MIN, 
        lambda_max = LAMBDA_MAX, 
        n_breaks = 216 
    )
    ```
    
    Normalization:
    ```
    raster_image /= np.max( raster_image, axis=1 ).reshape(-1,1)
    ```
    
    Nearest neighbour assignment:
    ```
    from sklearn.neighbors import NearestCentroid
    knc = NearestCentroid()
    knc.fit( X=centroids, y=list( range( centroids.shape[0] ) ) )
    
    assigned_centroids = knc.predict( raster_image )
    ```
    
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


def assign_mg2k_centroids( X ):
    """
    Assigns Mg II k centroids found in the study
    'Identifying typical Mg II flare spectra using machine learning', by
    B. Panos et. al. 2018 to the Mg II k spectra supplied in X. The centroids
    are assigned using a nearest neighbour procedure.
    
    The spectra in X have to be interpolated to 216 wavelength bins between 
    LAMBDA_MIN = 2793.8500976562500 and LAMBDA_MAX = 2799.3239974882454. For example:
        
    ```
    X = raster.get_interpolated_image_step( 
        step = <step>, 
        lambda_min = LAMBDA_MIN, 
        lambda_max = LAMBDA_MAX, 
        n_breaks = 216 
    )
    ```
    
    Parameters
    ----------
    X : numpy.array
        interpolated raster image of shape (_,bins)
    
    Returns
    -------
    assigned_mg2k_centroids
        numpy vector with shape (X.shape[1],)
    """

    # load centroids
    bins = X.shape[1]
    centroids = get_mg2k_centroids( bins )
    centroid_ids = list( range( centroids.shape[0] ) )
    
    # check whether X comes in the correct dimensions
    if not X.shape[1] == centroids.shape[1]:
        raise ValueError( "Expecting X to have shape (_,{}). Please interpolate accordingly (More information with 'help(assign_mg2k_centroids)').".format( centroids.shape[1] ) )
    
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

def interpolate( raster, step, bins=216 ):
    """
    Assigns Mg II k centroids found in the study
    'Identifying typical Mg II flare spectra using machine learning', by
    B. Panos et. al. 2018 to the Mg II k spectra supplied in X. The centroids
    are assigned using a nearest neighbour procedure.
    
    The spectra in X have to be interpolated to 216 wavelength bins between 
    LAMBDA_MIN = 2793.8500976562500 and LAMBDA_MAX = 2799.3239974882454. For example:
    
    Parameters
    ----------
    raster : irisreader.raster_cube
        raster_cube instance
    step : int
        image step in the raster
    bins : int
        number of bins to interpolate to (defaults to 216)
        
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
        lambda_min = LAMBDA_MIN, 
        lambda_max = LAMBDA_MAX, 
        n_breaks = bins 
    )

def compare_plot( raster, step, i ):
    """
    Compares spectrum <i> of image <step> of raster <raster> visually to its assigned centroid.
    
    Parameters
    ----------
    raster : irisreader.raster_cube
        raster_cube instance
    step : int
        image step in the raster
    i : int
        row index of the spectrum in raster image <step>
        
    """
    
    # make sure we are dealing with a Mg II - raster
    if not "Mg II k" in raster.line_info:
        raise ValueError("This is not a Mg II k raster!")
    
    centroids = get_mg2k_centroids()
    distances = compute_distances( raster, step, i )
    sorted_distances = sorted( distances )
    X = normalize( interpolate( raster, step ) )
    
    best_centroid = np.where( distances == sorted_distances[0] )[0][0]
    second_best_centroid = np.where( distances == sorted_distances[1] )[0][0]
    
    print( best_centroid, second_best_centroid )
    
    plt.plot( centroids[best_centroid], label="best centroid" )
    plt.plot( centroids[second_best_centroid], label="second-best centroid" )
    plt.plot( X[i,:], label="data" )
    plt.legend()
    plt.show()
    
def compute_distances( raster, step, i ):
    """
    Computes euclidean distances to all centroids for spectrum <i> of image <step> of raster <raster>
    
    Parameters
    ----------
    raster : irisreader.raster_cube
        raster_cube instance
    step : int
        image step in the raster
    i : int
        row index of the spectrum in raster image <step>

    Returns
    -------
    distances : np.array
        vector with euclidean distances to each centroid
    """        
    
    # make sure we are dealing with a Mg II - raster
    if not "Mg II k" in raster.line_info:
        raise ValueError("This is not a Mg II k raster!")
    
    centroids = get_mg2k_centroids()
    x = normalize( interpolate( raster, step ) )[i,:]
    distances = np.sqrt( np.sum( (centroids - x)**2, axis=1 ) )
    return distances

def get_mg2k_centroid_table( obs, crop_raster=False ):
    """
    Returns a data frame with centroid counts for each raster image of a given
    observation.
    
    Parameters
    ----------
    obs_path : str
        Path to observation
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
    
    # empty list for assigned centroids
    assigned_centroids = []
    
    # empty data frame for centroid counts
    df = pd.DataFrame( columns=["full_obsid", "date", "image_no", "centroid", "count"] )
    
    # assign centroids for each image and create aggregated data frame
    for step in range( raster.n_steps ):
        
        # fetch assigned centroids
        img = interpolate( raster, step )
        img_assigned_centroids = assign_mg2k_centroids( img )
        assigned_centroids.append( img_assigned_centroids )
        
        # count centroids
        centroids, counts = np.unique( img_assigned_centroids, return_counts=True )
        
        # append to data frame
        df = df.append( 
                pd.DataFrame(
                        {'full_obsid': obs.full_obsid, 
                         'date': date.from_Tformat( raster.headers[step]['DATE_OBS'] ), 
                         'image_no': step, 
                         'centroid': centroids, 
                         'count': counts }
                        ),
                sort = False
            )
    
    # create pivot table
    df = df.pivot_table(index=['full_obsid', 'date', 'image_no'], columns='centroid', values='count', aggfunc='first', fill_value=0 )
    df.reset_index( inplace=True )
    
    # make sure all centroids are represented
    for i in range( N_CENTROIDS ):
        if i not in df:
            df[i] = 0
    
    # make sure columns are sorted
    df = df.reindex( ["full_obsid", "date", "image_no"] + [i for i in range(N_CENTROIDS)], axis=1 )
    df.columns.name = ''
    
    # rename number columns into string columns
    cols = df.columns.values
    cols[3:] = ["c" + str(col) for col in df.columns[3:]]
    df.columns = cols
    
    # close observation
    obs.close()
    
    # return data frame
    return df, assigned_centroids

if __name__ == "__main__":
    #from irisreader.data import sample_raster
    #raster = sample_raster()
    #compare_plot( raster, 2, 10 )
    
    from irisreader import observation
    obs_path = '/home/chuwyler/Desktop/FITS/20140128_073021_3860259280/'
    d, c = get_mg2k_centroid_table( observation( obs_path ) )