# <img src="irisreader.png" width="100" height="100"/> &nbsp; IRISreader #

The __IRISreader__ library provides functionality to read IRIS level 2 data
by the [IRIS satellite](https://www.nasa.gov/mission_pages/iris/index.html) and to process it for big data applications. 
IRISreader works best with a Jupyter notebook.

__Warning__:

IRISreader is currently under heavy development and not yet available in a
stable version. Documentation is available but might not reflect the newest
additions.

## Installation ##

To install the latest stable release fro pypi, run

    pip install irisreader

To install the current development version, clone the repository

    git clone https://github.com/i4Ds/IRISreader.git

and run

    sudo python3 setup.py install

to install the library.

To test it go to the Python console, cd to the IRISreader directory and run:

    from irisreader.data import sample_sji
    sji_data = sample_sji()
    sji_data.plot(0)

## Documentation ##

The documentation is available [here](https://i4ds.github.io/IRISreader/).

## Contact ##

For questions, suggestions and feedback please contact me via
[email](mailto:cedric.huwyler@fhnw.ch).