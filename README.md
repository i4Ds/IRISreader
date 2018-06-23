# <img src="irisreader.png" width="100" height="100"/> &nbsp; IRISreader #

The _IRISreader_ library provides functionality to read IRIS level 2 data
by the [IRIS satellite](https://www.nasa.gov/mission_pages/iris/index.html) and to process it for big data applications. 

_Warning_:
IRISreader is currently under heavy development and not yet available in a
stable version.

## Installation ##

To install the library run (needs superuser privileges, only tested on Linux):

    sudo python3 setup.py install

To test it go to the Python console, cd to the irisreader directory and run:

    from irisreader.data import sample_sji
    sji_data = sample_sji()
    sji_data.plot(0)

## Documentation ##

The documentation is available [here](https://www.cs.technik.fhnw.ch/iris/irisreader_docs/).