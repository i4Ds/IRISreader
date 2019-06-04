#!/usr/bin/env python3

from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML

def animate( data_cube, raster_pos=None, index_start=None, index_stop=None, interval_ms=50, gamma=0.4, figsize=(7,7), cutoff_percentile=99.9, save_path=None ):
    """
    Creates an animation from the individual images of a data cube.
    This function can be pretty slow and take 1-2 minutes.
    Faster alternatives than matplotlib will be researched in the future.
    
    Parameters
    ----------
    data_cube : iris_data_cube
        instance of sji_cube or raster_cube
    raster_pos : int
        If not None, only display images at raster postion *raster_pos*
    index_start : int
        index where to start animation (defaults to None -> will be set to 0)
    index_stop : int
        index where to stop animation (defaults to None -> will be set to n)
    interval_ms : int
        number of milliseconds between two frames
    gamma : float
        gamma correction for plotting: number between 0 (infinitely gamma correction) and 1 (no gamma correction)
    figsize : tuple
        figure size: (width,height)
    cutoff_percentile : float
            Often the maximum pixels shine out everything else, even after gamma correction. In order to reduce 
            this effect, the percentile at which to cut the intensity off can be specified with cutoff_percentile
            in a range between 0 and 100.
    save_path : str
        path to file where animation output will be written to (use .mp4 extension)
    
    Returns
    -------
    IPython.HTML :
        HTML object with the animation
    """

    # get number of steps    
    if raster_pos is None:
        n = data_cube.shape[0]        
    else:
        n = data_cube.get_raster_pos_steps( raster_pos )

    # set default values for index_start and index_stop
    if index_start is None:
        index_start=0
    if index_stop is None:
        index_stop=n

    # raise exception if there is a problem with i_start / i_stop
    if index_stop > n or index_stop <= index_start:
        raise Exception("Please make sure that index_start < index_stop < n_steps")
    
    # release a duration warning
    if index_stop-index_start > 100:
        print( "Creating animation with {} frames (this may take while)".format(index_stop-index_start) )
    
    # initialize plot
    fig = plt.figure( figsize=figsize )
    image = data_cube.get_image_step( 0, raster_pos ).clip(min=0.01)**gamma
    vmax = np.percentile( image, cutoff_percentile )
    im = plt.imshow( image, cmap="gist_heat", vmax=vmax, origin='lower' )

    # do nothing in the initialization function
    def init():
        return im,

    # animation function
    def animate(i, index_start):
        xcenix = data_cube.headers[i+index_start]['XCENIX']
        ycenix = data_cube.headers[i+index_start]['YCENIX']
        date_obs = data_cube.headers[i+index_start]['DATE_OBS']
        im.axes.set_title( "Frame {}: {}\nXCENIX: {:.3f}, YCENIX: {:.3f}".format( i+index_start, date_obs, xcenix, ycenix ) )
        im.set_data( data_cube.get_image_step( i+index_start, raster_pos ).clip(min=0.01)**gamma )
        return im,

    # Call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, lambda i: animate(i, index_start), init_func=init, frames=index_stop-index_start, interval=interval_ms, blit=True)
    
    # Close the plot
    plt.close(anim._fig)
    
    # Save animation if requested
    if save_path is not None:
        anim.save( save_path )
    
    return HTML(anim.to_html5_video())