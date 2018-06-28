# <img src="irisreader.png" width="100" height="100"/> &nbsp; IRISreader #

The __IRISreader__ library provides functionality to read IRIS level 2 data
by the [IRIS satellite](https://www.nasa.gov/mission_pages/iris/index.html) and to process it for big data applications. 

__Warning__:

IRISreader is currently under heavy development and not yet available in a
stable version.

## Installation ##

To install the library run (Linux / OSX):

    sudo python3 setup.py install

To test it go to the Python console, cd to the IRISreader directory and run:

    from irisreader.data import sample_sji
    sji_data = sample_sji()
    sji_data.plot(0)

## Documentation ##

The documentation is available [here](https://www.cs.technik.fhnw.ch/iris/irisreader_docs/).

## Contact ##

For questions and suggestions, please contact me via
[email](mailto:cedric.huwyler@fhnw.ch).