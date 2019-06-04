#!/usr/bin/env python3

"""
iris_data_cube class: abstraction that makes the data, the headers and a number
of auxiliary variables available
"""

import os
import numpy as np
import warnings
from datetime import timedelta

import irisreader as ir
from irisreader.utils.fits import line2extension, array2dict, CorruptFITSException
from irisreader.utils.date import from_Tformat, to_Tformat, to_epoch
from irisreader.utils.coordinates import iris_coordinates
from irisreader.utils import lazy_file_header_list
from irisreader.preprocessing import image_cube_cropper
from irisreader.coalignment import goes_data

# IRIS data cube class
class iris_data_cube:
    """
    This class implements an abstraction of an IRIS FITS file collection, 
    specifically it appears as one single data cube, automatically discarding
    images that are entirely null and concatenating multiple files. Moreover,
    it provides basic access to image headers. It provides the basic 
    functionalities needed for the classes sji_cube and raster_cube that then
    implement more sji and raster-specific details. Hence, this class should 
    only be used internally.
    
    Parameters
    ----------
    files : string
        Path or list of paths to the (sorted) IRIS FITS file(s).
    line : string
        Line to select: this can be any unique abbreviation of the line name (e.g. "Mg"). For non-unique abbreviations, an error is thrown.
    keep_null : boolean
        Controls whether images that are NULL (-200) everywhere are removed from the data cube (keep_null=False) or not (keep_null=True).
    force_valid_steps : boolean
        iris_data_cube intially creates a list of valid images that are in the
        data cube. This list is stored to the directory where the file resides
        and can then be loaded in the future instead of creating the list again.
        `force_valid_steps` forces iris_data_cube to create the list again even
        if it's already stored.
        
    Attributes
    ----------
    type : str
        Observation type: 'sji' or 'raster'.
    obsid : str
        Observation ID of the selected observation.
    desc : str
        Description of the selected observation.
    start_date : str
        Start date of the selected observation.
    end_date : str
        End date of the selected observation.
    mode : str
        Observation mode of the selected observation ('sit-and-stare' or 'raster').
    line_info : str
        Description of the selected line.
    n_steps : int
        Number of time steps in the data cube (this is affected by the keep_null argument).
    n_raster_pos : int
        Number of unique raster positions.
    n_files : int
        Number of FITS files (abstracted to one)
    primary_headers: dict
        Dictionary with primary headers of the FITS file (lazy loaded).
    time_specific_headers: dict
        List of dictionaries with time-specific headers of the selected line (lazy loaded).  
    shape : tuple
        Shape of the data cube (this is affected by the keep_null argument)
    """

    # constructor
    def __init__( self, files, line='', keep_null=False, force_valid_steps=False ):
                
        # if filename is not a list, create a list with one element:
        if not isinstance( files, list ):
            files = [ files ]

        # store arguments
        self._files = files
        self._line = line
        self._keep_null = keep_null
        self._force_valid_steps = force_valid_steps
        
        # request first file from filehub and get general info
        first_file = ir.file_hub.open( files[0] )
        
        # check whether the INSTRUMENT header is either set to SJI or raster:
        if 'INSTRUME' not in first_file[0].header.keys() or not first_file[0].header['INSTRUME'] in ['SJI', 'SPEC']:
            raise CorruptFITSException( "This is neither IRIS SJI nor raster! (according to the INSTRUME header)" )
        
        # set FITS type
        if first_file[0].header['INSTRUME'] == 'SJI':
            self.type = 'sji' 
        else:
            self.type = 'raster'

        # Check if data part of first extension has only two dimensions. 
        # If yes, this is a SJI with only one single image. Currently such files
        # cannot be handled, throw an error
        if hasattr( first_file[0], 'shape' ) and len( first_file[0].shape ) == 2:
            #first_file[0].data = np.array([first_file[0].data])
            raise CorruptFITSException( "SJI: first extension has only two dimensions (single image, not implemented)" )
            
        # get extensions with data cubes in them
        self._n_ext = len( first_file )
        data_cube_extensions = []
        for i in range( self._n_ext ):
            if hasattr( first_file[i], 'shape' ) and len( first_file[i].shape ) == 3:
                data_cube_extensions.append( i )
       
        if len( data_cube_extensions ) == 0:
            raise CorruptFITSException( "No data cubes found." )
        
        self._first_data_ext = min( data_cube_extensions )
        self._last_data_ext = max( data_cube_extensions )
        
        # find extension that contains selected line
        if line == '':
            self._selected_ext = self._first_data_ext # choose first line by default
        elif line2extension( first_file[0].header, line ) != -1: 
            self._selected_ext = line2extension( first_file[0].header, line )
        else:
            self.close()
            raise CorruptFITSException(('Change the line parameter: The desired spectral window is either not found or specified ambiguously.'))
        
        # check the integrity of this first file
        self._check_integrity( first_file )
        
        # set obsid
        self.obsid = first_file[0].header['OBSID']
        
        # set date
        self.start_date = first_file[0].header['STARTOBS']
        self.end_date = first_file[0].header['ENDOBS']

        # set description
        self.desc = first_file[0].header['OBS_DESC']

        # get observation mode
        if 'sit-and-stare' in self.desc:
            self.mode = 'sit-and-stare'
        else:
            self.mode = 'n-step raster'

        # set number of raster positions
        self.n_raster_pos = first_file[0].header['NRASTERP']
        
        # number of files
        self.n_files = len( self._files )
            
        # line information (SJI info is replaced by actual line information)
        self.line_info = first_file[0].header['TDESC'+str(self._selected_ext-self._first_data_ext+1)]
        self.line_info = self.line_info.replace( 'SJI_1330', 'C II 1330' )
        self.line_info = self.line_info.replace( 'SJI_1400', 'Si IV 1400' )
        self.line_info = self.line_info.replace( 'SJI_2796', 'Mg II h/k 2796' )
        self.line_info = self.line_info.replace( 'SJI_2832', 'Mg II wing 2832' )
        
        # no cropping: set variables to none
        self._xmin = None
        self._xmax = None
        self._ymin = None
        self._ymax = None
        self._cropped = False
        
        # set some variables that will be lazy loaded
        self.shape = None
        self._original_shape = None
        self.n_steps = None
        self._valid_steps = None
        self.primary_headers = None
        self.time_specific_headers = None
        self.line_specific_headers = None
        self.headers = None
        
        # initialize coordinate converter
        self._ico = iris_coordinates( header=first_file[self._selected_ext].header, mode=self.type )


    # close all files
    def close( self ):
        """
        Closes the FITS file(s)
        """
        
        for file in self._files:
            ir.file_hub.close( file )
    
    # some components are loaded only upon first access
    def __getattribute__( self, name ):
        if name=='primary_headers' and object.__getattribute__( self, "primary_headers" ) is None:
            self._prepare_primary_headers()
            return object.__getattribute__( self, "primary_headers" )
        elif name=='_valid_steps' and object.__getattribute__( self, "_valid_steps" ) is None:
            self._prepare_valid_steps()
            return object.__getattribute__( self, "_valid_steps" )
        elif name=='n_steps' and object.__getattribute__( self, "n_steps" ) is None:
            self._prepare_valid_steps()
            return object.__getattribute__( self, "n_steps" )
        elif name=='shape' and object.__getattribute__( self, "shape" ) is None:
            self._prepare_valid_steps()
            return object.__getattribute__( self, "shape" )
        elif name=='_original_shape' and object.__getattribute__( self, "_original_shape" ) is None:
            self._prepare_valid_steps()
            return object.__getattribute__( self, "_original_shape" )
        elif name=='time_specific_headers' and object.__getattribute__( self, "time_specific_headers" ) is None:
            self._prepare_time_specific_headers()
            return object.__getattribute__( self, "time_specific_headers" )
        elif name=='line_specific_headers' and object.__getattribute__( self, "line_specific_headers" ) is None:
            self._prepare_line_specific_headers()
            return object.__getattribute__( self, "line_specific_headers" )
        elif name=='headers' and object.__getattribute__( self, "headers" ) is None:
            self._prepare_combined_headers()
            return object.__getattribute__( self, "headers" )
        else:
            return object.__getattribute__( self, name )

    # prepare valid steps
    def _prepare_valid_steps( self ):
        if ir.config.verbosity_level >= 2: print("[iris_data_cube] Lazy loading valid image steps")

        valid_steps = []
        
        # generate the path to the file with the precomputed valid steps
        keep_null_str = "keep_null" if self._keep_null else "discard_null"
        valid_steps_file = "{}/.valid_steps_{}_{}.npy".format( os.path.dirname( self._files[0] ), self.line_info.replace(' ','_').replace('/','_'), keep_null_str )

        # generate valid steps without looking into files if keep_null = True
        # Warning: this routine needs to be checked thoroughly - it's unclear how this works for bad data    
        if self._keep_null:
        
                if ir.config.verbosity_level >= 2:
                    print("[iris_data_cube] Warning: Not testing for bad data if keep_null=True")
            
                # open first file
                f = ir.file_hub.open( self._files[ 0 ] ) # open first file to look up steps
                
                # n-step raster
                if self.mode == "n-step raster":
                    if self.type == 'sji':
                        steps = f[0].shape[0]
                        sweeps = int( steps / self.n_raster_pos )
                        
                        # raise error if sweeps is not an integer
                        if steps % self.n_raster_pos != 0:
                            raise Exception("This SJI does not contain an integer repetition of raster sweeps. IRISreader can't handle this currently in the keep_null=True mode. Please contact cedric.huwyler@fhnw.ch if you encounter this error.")
                        
                        valid_steps = np.zeros( [steps, 3] )
                        valid_steps[:,1] = np.arange( steps )
                        valid_steps[:,2] = np.tile( np.arange(self.n_raster_pos), sweeps )
                        
                    else:
                        valid_steps = np.zeros( [self.n_raster_pos * self.n_files, 3] )
                        valid_steps[:,0] = np.repeat( np.arange(self.n_files), self.n_raster_pos )
                        valid_steps[:,1] = np.tile( np.arange(self.n_raster_pos), self.n_files )
                        valid_steps[:,2] = valid_steps[:,1].copy()
                    
                
                # sit-and-stare
                else:
                    if self.type == "sji":
                        steps = f[0].shape[0]
                    else:
                        steps = f[1].shape[0]
                        
                    valid_steps = np.zeros( [steps, 3] )
                    valid_steps[:,1] = np.arange( steps )
    
        # valid steps have already been precomputed: try to load the file
        elif not self._force_valid_steps and os.path.exists( valid_steps_file ):
            if ir.config.verbosity_level >= 2: print("[iris_data_cube] using precomputed steps")
            try:
                valid_steps = np.load( valid_steps_file )
        
            except Exception as e:
                print( e )

        
        # no precomputed valid image steps: assess them now
        else:
            # go through all the files: make sure they are not corrupt with _check_integrity
            for file_no in range( len( self._files ) ):
            
                # request file from file hub
                f = ir.file_hub.open( self._files[ file_no ] )
            
                try:
                    # make sure that file is not corrupt
                    self._check_integrity( f )
                
                    # check whether some images are -200 everywhere and if desired
                    # (keep_null=False), do not label these images as valid
                    for file_step in range( f[self._selected_ext].shape[0] ):
                        
                        # assign the raster position
                        # raster: raster position is either file_step (n-step raster) or 0 everywhere (sit-and-stare)
                        # sji: there is only one file, raster position is file_step modulo the number of raster positions
                        if self.n_raster_pos == 1:
                            raster_pos = 0
                        else:
                            if self.type == 'raster':
                                raster_pos = file_step
                            else:
                                raster_pos = file_step % self.n_raster_pos
                        
                        # use the section or the data interface, depending on whether files are opened with memory mapping or not
                        if ir.config.use_memmap:
                            image_is_null = np.all( f[ self._selected_ext ].section[file_step,:,:] == -200 )
                        else:
                            image_is_null = np.all( f[ self._selected_ext ].data[file_step,:,:] == -200 )

                        if self._keep_null or not image_is_null:
                            valid_steps.append( [file_no, file_step, raster_pos] )
                        
                except CorruptFITSException as e:
                    warnings.warn("File #{} is corrupt, discarding it ({})".format( file_no, e ) )
            
            # store valid steps
            try:
                np.save( valid_steps_file, np.array( valid_steps ) )
            except Exception as e:
                print( e )
        
        
        
        # return an error if the data cube contains no valid steps    
        if len( valid_steps ) == 0:
            raise CorruptFITSException("This data cube contains no valid images!")
            
        # update class instance variables
        self._valid_steps = np.array( valid_steps, dtype=np.int )
        self.n_steps = len( valid_steps )
        f = ir.file_hub.open( self._files[ -1 ] )
        self.shape = tuple( [ self.n_steps ] + list( f[ self._selected_ext ].shape[1:] ) )
        self._original_shape = self.shape
        
    # prepare primary headers
    def _prepare_primary_headers( self ):
        if ir.config.verbosity_level >= 2: print("[iris_data_cube] Lazy loading primary headers")
        
        # request first file from file hub
        first_file = ir.file_hub.open( self._files[0] )
        
        # convert headers to dictionary and clean up some values
        self.primary_headers = dict( first_file[0].header )
        self.primary_headers['SAA'] = self.primary_headers['SAA'].strip() 
        self.primary_headers['NAXIS'] = 2
        
        # remove empty headers
        if '' in self.primary_headers.keys():
            del self.primary_headers['']
        
        # DATE_OBS may not always be there: set it to STARTOBS
        if not 'STARTOBS' in self.primary_headers.keys() or self.primary_headers['STARTOBS'].strip() == '':
            raise ValueError( "No STARTOBS in primary header!" )
        else:
            self.primary_headers['DATE_OBS'] = self.primary_headers['STARTOBS']

    # assign lazy_file_header_list to time_specific_headers        
    def _prepare_time_specific_headers( self ): 
        if ir.config.verbosity_level >= 2: print("[iris_data_cube] Assigning lazy_file_header_list object to time_specific_headers")
        self.time_specific_headers = lazy_file_header_list( self._valid_steps[:,:2], self._load_time_specific_header_file )
        
    # assign lazy_file_header_list to headers
    def _prepare_combined_headers( self ):
        if ir.config.verbosity_level >= 2: print("[iris_data_cube] Assigning lazy_file_header_list object to headers")
        self.headers = lazy_file_header_list( self._valid_steps[:,:2], self._load_combined_header_file )    
    
    # function to load time-specific headers from a file    
    def _load_time_specific_header_file( self, file_no ):
        if ir.config.verbosity_level >= 2: print("[iris_data_cube] Lazy loading time specific headers for file {}".format(file_no))

        # request file from file hub
        f = ir.file_hub.open( self._files[file_no] )
         
        # read headers from data array
        file_time_specific_headers = array2dict( f[self._n_ext-2].header, f[self._n_ext-2].data )
        
        # apply some corrections to the individual headers
        startobs = from_Tformat( self.primary_headers['STARTOBS'] )
        for i in range( len( file_time_specific_headers ) ):
        
            # set a DATE_OBS header in each frame as DATE_OBS = STARTOBS + TIME
            file_time_specific_headers[i]['DATE_OBS'] = to_Tformat( startobs + timedelta( seconds=file_time_specific_headers[i]['TIME'] ) )
        
            # if key 'DSRCNIX' exists: rename it to 'DSRCRCNIX'
            if 'DSRCNIX' in file_time_specific_headers[i].keys():
                file_time_specific_headers[i]['DSRCRCNIX'] = file_time_specific_headers[i].pop('DSRCNIX')
                
            # remove some keys (as IDL does it, currently disabled)
            # for key_to_remove in ['PC1_1IX', 'PC1_2IX', 'PC2_1IX', 'PC2_2IX', 'PC2_3IX', 'PC3_1IX', 'PC3_2IX', 'PC3_3IX', 'OPHASEIX', 'OBS_VRIX']:
            #     if key_to_remove in file_time_specific_headers[i].keys():
            #        del file_time_specific_headers[i][ key_to_remove ]
            
        # return headers
        return file_time_specific_headers

    # function to convert time-specific headers from a file to combined headers
    def _load_combined_header_file( self, file_no ):
        raise NotImplementedError( "This feature is not implemented in iris_data_cube, please use sji_cube or raster_cube" )
         
    # prepare line specific headers
    def _prepare_line_specific_headers( self ):
        if ir.config.verbosity_level >= 2: print("[iris_data_cube] Lazy loading line specific headers")
        
        # request first file from file hub
        first_file = ir.file_hub.open( self._files[0] )
        
        # get line-specific headers from data extension (if selected extension is not the first one)
        if self._selected_ext > 0:
            line_specific_headers = dict( first_file[ self._selected_ext ].header )
        else:
            line_specific_headers = {}
        
        # add wavelnth, wavename, wavemin and wavemax (without loading primary headers)
        line_specific_headers['WAVELNTH'] = first_file[0].header['TWAVE'+str(self._selected_ext-self._first_data_ext+1)]
        line_specific_headers['WAVENAME'] = first_file[0].header['TDESC'+str(self._selected_ext-self._first_data_ext+1)]
        line_specific_headers['WAVEMIN'] =  first_file[0].header['TWMIN'+str(self._selected_ext-self._first_data_ext+1)]
        line_specific_headers['WAVEMAX'] =  first_file[0].header['TWMAX'+str(self._selected_ext-self._first_data_ext+1)]
        line_specific_headers['WAVEWIN'] =  first_file[0].header['TDET'+str(self._selected_ext-self._first_data_ext+1)]

        self.line_specific_headers = line_specific_headers
        
    # function to remove image steps from valid steps (e.g. by cropper)
    def _remove_steps( self, steps ):
    
        # if steps is a single integer, put it into a list    
        if not isinstance( steps, (list, tuple) ):
            steps = [steps]
    
        # now remove the steps (make sure they are removed simultaneously)
        valid_steps = np.delete( self._valid_steps, steps, axis=0 )
        
        # raise a warning if the data cube contains no valid steps    
        if len( valid_steps ) == 0:
            raise CorruptFITSException("This data cube contains no valid images! You might want to set check_coverage=False or remove_bad=False when cropping (restored original state)")
        else:
            self._valid_steps = valid_steps

        # remove steps from headers if already loaded
        if not object.__getattribute__( self, "headers" ) is None:
            self.headers = [ self.headers[i] for i in range( self.n_steps ) if i not in steps ]
        
        # update n_steps and shape
        self.n_steps = len( self._valid_steps )
        self.shape = tuple( [ self.n_steps ] + list( self.shape[1:] ) )

    # function to find file number and file step of a given time step
    def _whereat( self, step, raster_pos=None ):
        if raster_pos is None:
            return self._valid_steps[ step, : ]
        else:
            return self._valid_steps[self._valid_steps[:,2]==raster_pos, :][ step, : ]
    
    # function to return valid steps in a file
    def _get_valid_steps( self, file_no ):
        return self._valid_steps[ self._valid_steps[:,0]==file_no, 1 ]
    
    # how to behave if called as a data array
    def __getitem__( self, index ):
        """
        Abstracts access to the data cube. While in the get_image_step function
        data is loaded through the the section method to make sure that only
        the image requested by the user is loaded into memory, this method
        directly accesses the data object of the hdulist, allowing faster slicing
        of data. Whenever only time slices are required (i.e. single images), 
        the get_image_step function should be used instead, since access 
        through the data object can lead to memory problems.
        
        If the data cube happens to be cropped, this method will automatically
        abstract access to the cropped data. If keep_null=False, null images
        will automatically be removed from the representation.
        """
        
        # check dimensions - this rules out the ellisis (...) for the moment
        if len( index ) != 3:
            raise ValueError("This is a three-dimensional object, please index accordingly.")

        # get involved file numbers and steps
        # if index[0] is a single number (not iterable, not a slice), make a list of it
        if not hasattr( index[0], '__iter__') and not isinstance( index[0], slice ):
            valid_steps = self._valid_steps[ [index[0]], :2 ]
        else:
            valid_steps = self._valid_steps[ index[0], :2 ]
        
        # if image should be cropped make sure that slices stay slices (is about 30% faster)
        if self._cropped:  
            if isinstance( index[1], slice ):
                a = self._ymin if index[1].start is None else index[1].start+self._ymin
                b = self._ymax if index[1].stop is None else index[1].stop+self._ymin  
                internal_index1 = slice( a, b, index[1].step )
                
            else:
                internal_index1 = np.arange( self._ymin, self._ymax )[ index[1] ]
                
            if isinstance( index[2], slice ):
                a = self._xmin if index[2].start is None else index[2].start+self._xmin
                b = self._xmax if index[2].stop is None else index[2].stop+self._xmin  
                internal_index2 = slice( a, b, index[2].step )
                
            else:
                internal_index2 = np.arange( self._xmin, self._xmax )[ index[2] ]

        else:
            internal_index1 = index[1]
            internal_index2 = index[2]

        # get all data slices and concatenate them (always use data interface here, regardless of whether memory mapping is used or not)
        slices = []
        for file_no in np.unique( valid_steps[:,0] ):
            file = ir.file_hub.open( self._files[file_no] )
            slices.append( file[ self._selected_ext ].data[ valid_steps[ valid_steps[:,0] == file_no, 1 ], internal_index1, internal_index2 ] )
        slices = np.vstack( slices )

        # remove first dimension if there is only one slice
        if slices.shape[0] == 1 and slices.ndim == 3:
           slices = slices[0,:,:]
            
        return slices

    # function to get an image step
    # Note: this method makes use of astropy's section method to directly access
    # the data on-disk without loading all of the data into memory
    def get_image_step( self, step, raster_pos=None ):
        """
        Returns the image at position step. This function uses the section 
        routine of astropy to only return a slice of the image and avoid 
        memory problems.
        
        Parameters
        ----------
        step : int
            Time step in the data cube.
        raster_pos : int
            Raster position. If raster_pos is not None, get_image_step will
            return the image_step on the given raster position.

        Returns
        -------
        numpy.ndarray
            2D image at time step <step>. Format: [y,x] (SJI), [y,wavelength] (raster).
        """
        
        # Check whether line and step exist
        if step < 0 or step >= self.n_steps:
            raise ValueError( "This image step does not exist!" )
            
        # Check whether this raster position exists
        if raster_pos is not None and raster_pos is not 0 and raster_pos >= self.n_raster_pos:
            raise Exception("This raster position is not available.")

        # get file number and file step            
        file_no, file_step, raster_pos = self._whereat( step, raster_pos=raster_pos )

        # put this into a try-except clause to catch too many open files
        # note: astropy opens multiple handles per file, file_hub can't control this
        try:
        
            # request file from file hub
            file = ir.file_hub.open( self._files[file_no] )
                    
            # get image (cropped if desired)
            if self._cropped:
                if ir.config.use_memmap: # use section interface if memory mapping is used
                    return file[self._selected_ext].section[file_step, self._ymin:self._ymax, self._xmin:self._xmax]
                else: # otherwise use data interface
                    return file[self._selected_ext].data[file_step, self._ymin:self._ymax, self._xmin:self._xmax]
            else:
            
                if ir.config.use_memmap: # use section interface if memory mapping is used
                    return file[self._selected_ext].section[file_step, :, :]
                else: # otherwise use data interface
                    return file[self._selected_ext].data[file_step, :, :]
        
        except OSError as oe:
            if oe.strerror.lower() == "too many open files":
                ir.config.max_open_files = int( ir.config.max_open_files / 2 )
                print( 
"""-------------------------------------------------------------------------------------------------------------
Too many open files! Setting maximum number of open files to half of the previous value ({}). 
Also resetting all open file handles, this might slow down things for a short moment.
This problem is due to the uncontrollable behaviour of astropy which can open multiple file handles per file.
The current output has been re-requested and is not affected. 
-------------------------------------------------------------------------------------------------------------""".format(ir.config.max_open_files) 
                )
                ir.file_hub.reset()
                
                # this recursive call is dangerous and should be tested more thoroughly
                return self.get_image_step( step )
            else:
                raise oe
                
            
                

    # crop data cube
    def crop( self, remove_bad=True, check_coverage=True ):
        """        
        Crops the images in the data cube.
        
        Parameters
        ----------
        remove_bad: boolean
            Whether to remove corrupt images.
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
        
        if not self._cropped:
            cropper = image_cube_cropper( check_coverage=check_coverage ).fit( self )

            # remove corrupt images if desired            
            if remove_bad:
                self._remove_steps( cropper.get_null_images() )
                self._remove_steps( cropper.get_corrupt_images() )

            # set new bounds and cropped cube indicator
            self._set_bounds( cropper.get_bounds() )
            self._cropped = True
            
        else:
            if ir.config.verbosity_level >= 1:
                print("This data cube has already been cropped")
 
    # uncrop data cube
    def uncrop( self ):
        """        
        Removes the cropping of the images in the data cube (but keeps the
        corrupt image steps removed).
        """
        
        if self._cropped:
            self._reset_bounds()
            self._cropped = False
        else:
            print("This data cube was not cropped")
     
    
    # some checks that should be run on every single file and not just the first
    def _check_integrity( self, hdu ):
    
        # raster: check whether the selected extension contains the right line
        if hdu[0].header['INSTRUME'] == 'SPEC' and not self._line in hdu[0].header['TDESC{}'.format( self._selected_ext )]:
            raise CorruptFITSException( "{}: This is not the right line".format( hdu._file.name  ) )
            
        # check whether the data part of the selected extension comes with the right dimensions
        if len( hdu[ self._selected_ext ].shape ) != 3:
            raise CorruptFITSException( "{}: The data extension does not contain a three-dimensional data cube!".format( hdu._file.name ) )
                
        # check whether the array with time-specific headers is valid
        if len( hdu[ self._n_ext-2 ].shape ) != 2:
            raise CorruptFITSException( "{}: The time-specific header extension does not contain a two-dimensional data cube!".format( hdu._file.name ) )
        
        # check whether the array with time-specific headers has the right amount of columns, as specified in the header
        keys_to_remove=['XTENSION', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'PCOUNT', 'GCOUNT']
        header_keys = dict( hdu[ self._n_ext-2 ].header )
        header_keys = {k: v for k, v in header_keys.items() if k not in keys_to_remove}

        if hdu[ self._n_ext-2 ].shape[1] != len( header_keys ):
            raise CorruptFITSException( "{}: Second extension has not the same amount of columns as number of headery keys.".format( hdu._file.name ) )    

    # functions to get, set and reset image bounds
    def _get_bounds( self ):
        return [self._xmin, self._xmax, self._ymin, self._ymax]
    
    def _set_bounds( self, bounds ):
        
        # update internal variables
        self._cropped = True
        self._xmin, self._xmax, self._ymin, self._ymax = bounds
        
        # update shape and number of spectra
        self.shape = tuple( [self.shape[0], self._ymax-self._ymin, self._xmax-self._xmin]  )
        
        # update coordinates
        self._ico.set_bounds( bounds )

    def _reset_bounds( self ):
        self._cropped = False
        self._xmin, self._xmax, self._ymin, self._ymax = None, None, None, None
        self.shape = self._original_shape
        self._ico.reset_bounds()

    # functions to enter and exit a context
    def __enter__( self ):
        return self

    def __exit__( self ):
        self.close()
        
    # function to convert pixels to coordinates
    def pix2coords( self, step, pixel_coordinates ):
        """
        Returns solar coordinates for the list of given pixel coordinates.
        
        **Caution**: This function takes pixel coordinates in the form [x,y] while
        images come as [y,x]
        
        Parameters
        ----------
        step : int
            The time step in the SJI to get the solar coordinates for. 
        pixel_coordinates : np.array
            Numpy array with shape (pixel_pairs,2) that contains pixel coordinates
            in the format [x,y]
            
        Returns
        -------
        float :
            Numpy array with shape (pixel_pairs,2) containing solar coordinates
        """

        return self._ico.pix2coords( step, pixel_coordinates )

    # function to convert coordinates to pixels (wrapper for wcs)
    def coords2pix( self, step, wl_solar_coordinates, round_pixels=True ):
        """
        Returns pixel coordinates for the list of given wavelength in angstrom / solar y coordinates.
        
        Parameters
        ----------
        step : int
            The time step in the SJI to get the pixel coordinates for. 
        wl_solar_coordinates : np.array
            Numpy array with shape (coordinate_pairs,2) that contains wavelength in 
            angstrom / solar y coordinates in the form [lat/lon] in units of arcseconds
            
        Returns
        -------
        float :
            Numpy array with shape (coordinate_pairs,2) containing pixel coordinates
        """
        
        return self._ico.coords2pix( step, wl_solar_coordinates, round_pixels=round_pixels )

    # function to get axis coordinates for a particular image
    def get_axis_coordinates( self, step ):
        """
        Returns coordinates for the image at the given time step.
        
        Parameters
        ----------
        step : int
            The time step in the SJI to get the coordinates for.

        Returns
        -------
        float :
            List [coordinates along x axis, coordinates along y axis]
        """

        return self._ico.get_axis_coordinates( step, self._original_shape )
        
    # function to get number of saturated pixels for an image
    def get_nsatpix( self, step ):
        """
        Returns the number of saturated pixels in an image. According to
        iris_prep.pro, a pixel is saturated if it has a data number >= 1.6e4.
        
        Parameters
        ----------
        step : int
            Time step in the data cube.
        
        Returns
        -------
        int :
            Number of saturated pixels at time step <step>.
        """
    
        return np.sum( self.get_image_step( step, divide_by_exptime=False ) >= 1.6e4 )
    
    # function to get millisecond timestamps of images
    def get_timestamps( self, raster_pos=None ):
        """
        Converts DATE_OBS to milliseconds since 1970 with the aim to make 
        timestamp comparisons easier.
        
        Parameters
        ----------
        raster_pos : int
            raster position (between 0 and n_raster_pos)
        
        Returns
        -------
        float :
            List of millisecond timestamps.
        """
        if raster_pos is None:
            headers = self.time_specific_headers
        else:
            headers = self.get_raster_pos_headers( raster_pos )
            
        return [to_epoch( from_Tformat( h['DATE_OBS'] ) ) for h in headers]
    
    # function to return exposure times
    def get_exptimes( self ):
        """
        Returns a list of exposure times throughout the observation.
        
        Returns
        -------
        list :
            List of exposure times.
        """
        return np.array([h['EXPTIME'] for h in self.headers])

    # function to get goes flux information
    def get_goes_flux( self ):
        """
        Interpolates GOES X-ray flux to time steps of the data cube.
        
        Returns
        -------
        float :
            List of X-ray fluxes
        """
        
        if self.n_steps > 0:
            g = goes_data( from_Tformat( self.start_date ), from_Tformat( self.end_date ), os.path.dirname( self._files[0] ) + "/goes_data", lazy_eval=True )
            return g.interpolate( self.get_timestamps() )
        else:
            return np.array([])
        
    # function to get data of a fixed raster position
    def get_raster_pos_data( self, raster_pos ):
        """
        Returns a data cube only for the given raster position.
        
        Parameters
        ----------
        raster_pos : int
            raster position (between 0 and n_raster_pos)
            
        Returns
        -------
        np.array :
            Data cube with dimensions [t,y,x/lambda]
        """
        
        if raster_pos >= self.n_raster_pos:
            raise Exception("This raster position is not available.")
        
        return self[self._valid_steps[:,2] == raster_pos,:,:]


    # function to get headers of a fixed raster position
    def get_raster_pos_headers( self, raster_pos ):
        """
        Returns headers only for the given raster position.
        
        Parameters
        ----------
        raster_pos : int
            raster position (between 0 and n_raster_pos)
            
        Returns
        -------
        list :
            List of header dictionaries for the given raster position
        """
        
        if raster_pos >= self.n_raster_pos:
            raise Exception("This raster position is not available.")
        
        return [self.headers[i] for i in range(self.n_steps) if self._valid_steps[i,2] == raster_pos]
    
    # function to return number of exposures for a given raster position
    def get_raster_pos_steps( self, raster_pos ):
        """
        Returns total number of image steps for the given raster position.
        
        Parameters
        ----------
        raster_pos : int
            raster position (between 0 and n_raster_pos)
            
        Returns
        -------
        int :
            Number of available image steps
        """
        
        if raster_pos >= self.n_raster_pos:
            raise Exception("This raster position is not available.")
        
        return np.sum( self._valid_steps[:,2] == raster_pos )
    
    # function to animate the data cube
    def animate( self, raster_pos=None, index_start=None, index_stop=None, interval_ms=50, gamma=0.4, figsize=(7,7), cutoff_percentile=99.9, save_path=None ):
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
        return ir.utils.animate( 
                self, raster_pos=raster_pos, index_start=index_start, index_stop=index_stop,
                interval_ms=interval_ms, gamma=gamma, figsize=figsize, 
                cutoff_percentile=cutoff_percentile, save_path=save_path 
        )
        

# Test code  
if __name__ == "__main__":


    fits_data1 = iris_data_cube( '/home/chuwyler/Desktop/FITS/20140329_140938_3860258481/iris_l2_20140329_140938_3860258481_SJI_1400_t000.fits' )
    fits_data2 = iris_data_cube( 
           [ "/home/chuwyler/Desktop/IRISreader/irisreader/data/IRIS_raster_test1.fits", 
            "/home/chuwyler/Desktop/IRISreader/irisreader/data/IRIS_raster_test2.fits" ],
            line="Mg"
    )

    # Test:
    # np.unique( sji._valid_steps[:,2] ) == ..