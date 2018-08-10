#!/usr/bin/env python3

# import libraries
import re, os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import gzip, shutil, tarfile
import math
import pandas as pd
import irisreader as ir

# Function to parse directory listing
def parse_url_content( url ):
    page = requests.get( url ).text
    soup = BeautifulSoup( page, 'html.parser' )
    rows = soup.find_all( "tr" )
    ret = []
            
    for i in range( 3, len(rows)-1 ):
        cols = rows[i].find_all( "td" )
        filename = cols[1].find_all( 'a', href=True)[0]['href']
        if filename[-3:] == '.gz':
            ret.append( {'file': filename, 'modified': cols[2].get_text(), 'size': cols[3].get_text() } )
        
    return pd.DataFrame( ret )

# Function to download a single file
def download_file( url, path ):
    r = requests.get(url, stream=True)

    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0)); 
    block_size = 1024
    wrote = 0 

    filename = path + "/" + os.path.basename( url )
    if os.path.exists( filename[:-3] ) or os.path.exists( filename[:-7] + "_t000_r00000.fits" ) or (os.path.exists( filename ) and os.path.getsize( filename ) == total_size ):
        print( os.path.basename(url) + ": File already exists" )
        return True
    else:
        print( "\nDownloading " + os.path.basename(url) )

    with open( filename, 'wb' ) as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
            wrote = wrote  + len(data)
            f.write(data)
    if total_size != 0 and wrote != total_size:
        raise Exception("Download error - something went wrong")
        return False
    else:
        return True
    
# Function to extract all files in a path
def extract_all( path ):
    
    # extract all gzip files
    gz_files = [file for file in os.listdir( path ) if file[-3:]=='.gz']
    if len( gz_files ) > 0:
        print( "extracting files.." )
    
    for f in gz_files:
        #print( "extracting " + path + "/" + f )
        with gzip.open( path + "/" + f, 'rb') as gzip_file:
            with open( path + "/" + f[:-3], 'wb') as extracted_file:
                shutil.copyfileobj( gzip_file, extracted_file )
                os.remove( path + "/" + f )
    
    # extract tar files if necessary
    tar_files = [file for file in os.listdir( path ) if file[-4:]=='.tar']
    for f in tar_files:
        #print( "extracting " + path + "/" + f )
        tar = tarfile.open( path + "/" + f )
        tar.extractall( path=path )
        tar.close()
        os.remove( path + "/" + f )
       
# Function to download an observation
def download( obs_identifier, target_directory, type='all', uncompress=True, open_obs=True, mirror=None ):
        """
        Downloads a given IRIS observation.
        
        Parameters
        ----------
        obs_identifier : str
            Observation identifier in the form yyyymmdd_hhmmss_oooooooooo, e.g. 20140323_052543_3860263227
        
        target_directory : str
            Path to store downloaded observation to (defaults to home directory)
            
        type : str
            Type of data to download:
            'all': all data
            'sji': only SJI files
            'raster': only raster files
        
        uncompress : bool
            Uncompress files after download? (automatically set to True if open_obs is True)
        
        open_obs : bool
            Immediately open observation and return observation object? Otherwise a boolean indicating download success is returned
        
        mirror : str
            Mirror to be used:
            'lmsal': LMSAL (http://www.lmsal.com/solarsoft/irisa/data/level2_compressed/)
            'uio': University of Oslo (http://sdc.uio.no/vol/fits/iris/level2/)
            
        Returns
        -------
        An open observation handle or a boolean indicating download success.
        """
        
        # if user desires to open observation then uncompress anyway
        if open_obs: uncompress = True
        
        # set mirror url
        if mirror is None: mirror = ir.config.DEFAULT_MIRROR
        
        if not mirror in ir.config.MIRRORS.keys():
            raise ValueError("The mirror you specified does not exist! Available mirrors: ", ir.config.MIRRORS.keys() )
        else:
            download_url = ir.config.MIRRORS[ mirror ]
        
        # extract year, month and day from obs identifier
        m = re.search('([\d]{4})([\d]{2})([\d]{2})_([\d]{6})_([\d]{10})', obs_identifier )
        if m:
            year, month, day, time, obsid = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        else:
            raise ValueError("Please pass an obs identifier in the form of yyyymmdd_hhmmss_oooooooooo.")
        
        # create directory url
        obs_url = download_url + year + "/" + month + "/" + day + "/" + obs_identifier
        
        # get directory listing and filter for SJI or raster if necessary
        listing = parse_url_content( obs_url )
        listing_sji = listing[[('_SJI_' in filename and filename[-2:] == 'gz') for filename in listing['file']]]
        listing_raster = listing[[('_raster' in filename and filename[-2:] == 'gz') for filename in listing['file']]]
                
        if type == 'sji':
            listing = listing_sji
        elif type == 'raster':
            listing = listing_raster
        else:
            listing = listing_sji.append( listing_raster )
                        
        # create directory if necessary
        local_path = target_directory + "/" + obs_identifier
        if not os.path.exists( local_path ):
            os.mkdir( local_path )

        # download files
        download_status = True
        for filename in listing['file']:
            url = obs_url + "/" + filename
            ret = download_file( url, path=target_directory + "/" + obs_identifier )
            download_status = ret and download_status
        
        # uncompress if desired
        if uncompress:
            extract_all( local_path )
        
        # return observation object if desired - otherwise return download status
        if open_obs:
            from irisreader import observation
            return observation( target_directory + "/" + obs_identifier )

