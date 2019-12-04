### Original code by Brandon Panos <brandon.panos@fhnw.ch>

import numpy as np
import warnings
warnings.filterwarnings("ignore")

def get_mg2k_features(nprof, dn_nprof, verbose=True):
    '''
    Function extracts Mg II line features from obsevrations.

        Inputs
        ---------
        nprof: array
            data in form [m_examples, lambda] from level 2C data
        dn_nprof: array
            data in from [m_examples, lambda] from level 2B data

        Returns
        ---------
        features: array
            features in form [feature, m_examples]
            each column contains different features:
            col_0 = intensity
            col_1 = triplet intensity
            col_2 = line center
            col_3 = line width
            col_4 = line asymmetry
            col_5 = total_continium
            col_6 = triplet emission
            col_7 = k/h ratio integrated
            col_8 = kh ratio max
            col_9 = k hight
            col_10 = peak ratios
            col_11 = peak separation

        Example:
        ---------
        obs = np.load( path_to_lvl2C_obs )
        data = obs['data']
        nprof = profile_rep( data )

        dn_obs = np.load( path_to_lvl2B_obs )
        dn_data = dn_obs['data']
        dn_nprof = profile_rep( dn_data )

        features = feature_transform( nprof, dn_nprof, dn_hdr )
    '''
    #---------------------------- parameters for Mg II feature exctraction ---------------------
    lambda_min = 2794.14
    lambda_max = 2805.72
    n_bins = 240
    window_width = 3
    nprofxax = np.linspace( lambda_min, lambda_max, n_bins )
    #---------------------------- h&k line core vacuum wavelengths -----------------------------
    k_core = 2796.34
    h_core = 2803.52
    #------------------------------ psoitions ito data units -----------------------------------
    k = np.abs( (k_core) - nprofxax ).argmin()
    h = np.abs( (h_core) - nprofxax ).argmin()
    kl = np.abs( (k_core-window_width/2.) - nprofxax ).argmin()
    kr = np.abs( (k_core+window_width/2.) - nprofxax ).argmin()
    hl = np.abs( (h_core-window_width/2.) - nprofxax ).argmin()
    hr = np.abs( (h_core+window_width/2.) - nprofxax ).argmin()
    k2l = np.abs( (k_core-1) - nprofxax ).argmin()
    k2r = np.abs( (k_core+1) - nprofxax ).argmin()
    #------------------------------------ triplet -----------------------------------------------
    sl = np.abs( 2798.22  - nprofxax ).argmin()
    sm = np.abs( 2798.77  - nprofxax ).argmin()
    wing = np.abs( 2799.32 - nprofxax ).argmin()
    #------------------------------- extract 12 features ----------------------------------------
    #---------------- intensity -----------------
    if verbose: print("1) intensity")
    intensity = np.max(dn_nprof, axis=1)
    trip_intensity = np.max(dn_nprof[:,sl:wing], axis=1)
    #------------- quartiles --------------------
    if verbose: print("2) quartile analysis ")
    NCDFs = NCDF( nprof[:,kl:kr] )
    q1 = np.abs(NCDFs - .25).argmin(axis=1)
    q2 = np.abs(NCDFs - .50).argmin(axis=1)
    q3 = np.abs(NCDFs - .75).argmin(axis=1)
    line_center = q2 + kl
    line_width = q3-q1
    line_asymmetry = ( (q3-q2)-(q2-q1) )/(q3-q1)
    #---------------- k2 peaks -------------------
    if verbose: print("3) k2 peak analysis")
    k3_h_list = []
    peak_ratios_list= []
    peak_separation_list = []
    for prof in nprof:
        k3_h, peak_ratios, peak_separation = peak_locs(prof, k2l, k2r, k)
        k3_h_list.append(k3_h)
        peak_ratios_list.append(peak_ratios)
        peak_separation_list.append(peak_separation)

    k3_h = np.asarray(k3_h_list)
    peak_ratios = np.asarray(peak_ratios_list)
    peak_separation = np.asarray(peak_separation_list)
    #----------------- sum of continium ---------
    if verbose: print("4) continuum")
    total_continium = np.sum( nprof[:, kr:hl],axis=1)
    #----------- tripplet feature ----------------
    if verbose: print("5) triplet emission")
    trip = np.log(nprof[:, sm]/nprof[:,wing])
    #---------------- k/h ratio --------------------
    if verbose: print("6) k/h ratio")
    kh_ratio_int = np.sum( nprof[:, kl:kr], axis=1)/np.sum(nprof[:, hl:hr], axis=1 ) # integrated version
    kh_ratio_max = np.max( nprof[:, kl:kr], axis=1)/np.max(nprof[:, hl:hr], axis=1 ) # max version
    #----------- put all together 12 features into a matrix ---------------
    features = np.concatenate( (intensity.reshape(nprof.shape[0],1),
                                trip_intensity.reshape(nprof.shape[0],1),
                                line_center.reshape(nprof.shape[0],1),
                                line_width.reshape(nprof.shape[0],1),
                                line_asymmetry.reshape(nprof.shape[0],1),
                                total_continium.reshape(nprof.shape[0],1),
                                trip.reshape(nprof.shape[0],1),
                                kh_ratio_int.reshape(nprof.shape[0],1),
                                kh_ratio_max.reshape(nprof.shape[0],1),
                                k3_h.reshape(nprof.shape[0],1),
                                peak_ratios.reshape(nprof.shape[0],1),
                                peak_separation.reshape(nprof.shape[0],1)),
                              axis=1 )
    return features


def profile_rep( data ):
    '''
    [steps, rasters, y, lamda] -> [m_example, lambda]
    '''
    data_transposed = np.transpose(data, (1,0,2,3))
    nprof = data_transposed.reshape( data.shape[0] * data.shape[1] * data.shape[2], data.shape[3], order='C' )
    return nprof

def NCDF( profile ):
    '''
    matrix of normalised cumulative distribution function
    '''
    row, col = profile.shape[0], profile.shape[1]
    summed_area = np.zeros( (1, row) )
    running_area = np.empty_like( profile )
    for i in range(col):
        summed_area = np.sum(profile[:, 0:i], axis=1).T
        running_area[:, i] = summed_area
    return running_area/np.max(running_area, axis=1).reshape(row, 1 )

def peak_locs(prof, k2l, k2r, k):
    '''
    Find k2, k3 peak locations
    '''
    p1 = k2l + (prof[k2l:k2r]).argmax()
    if p1 < k:
        grads = np.gradient(prof[p1:k2r])
        try: # try is for single peaks, grad keeps going down so this sets them ontop of eachother
            p2 = np.where(np.diff(np.sign(grads)))[0][1] + p1
            k3 = np.where(np.diff(np.sign(grads)))[0][0] + p1
        except:
            p2 = p1
            k3 = p2
    if p1 > k:
        grads = np.gradient(prof[k2l:p1])
        grads = -np.flip(grads)
        try: # try is for single peaks, grad keeps going down so this sets them ontop of eachother
            p2 = p1 - np.where(np.diff(np.sign(grads)))[0][1] -2
            k3 = p1 - np.where(np.diff(np.sign(grads)))[0][0] -2
        except:
            p2 = p1
            k3 = p2
    if p1 == k:
        p2 = p1
        k3 = p2
    # for single peaks, stops p2 from sliding off the edge because there is no second change in the derivative
    if prof[k3] < .15:
        p2 = p1
        k3 = p2
    k2vio = np.min( [p1, p2] )
    k2red = np.max( [p1, p2] )
    k2vio_h = prof[k2vio]
    k2red_h = prof[k2red]
    k3_h = prof[k3]
    peak_ratios = k2vio_h/k2red_h
    peak_separation = abs( k2red - k2vio )
    return k3_h, peak_ratios, peak_separation
