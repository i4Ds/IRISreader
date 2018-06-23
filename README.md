# <img src="irisreader.png" width="100" height="100"/> &nbsp; irisreader #

The _irisreader_ library provides functionality to read level 2 data of the [IRIS satellite](https://www.nasa.gov/mission_pages/iris/index.html) and to preprocess it for big data applications. 
It is designed to read the data similiar to solar soft's [read_iris_l2](http://iris.lmsal.com/itn26/iris_level2.html).


## Installation ##

To install the library run (needs superuser privileges, only tested on Linux):

    sudo python3 setup.py install

To test it go to the Python console, cd to the irisreader directory and run:

    from irisreader.data import sample_sji
    sji_data = sample_sji()
    sji_data.plot(0)

## Documentation ##

The documentation is available [here](https://www.cs.technik.fhnw.ch/iris/irisreader_docs/).