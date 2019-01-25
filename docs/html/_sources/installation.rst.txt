Installation
**************

IRISreader requires Python >= 3.5, make sure you have a clean Python installation.

To install the library, download the latest code from Github::

        $ git clone https://github.com/i4Ds/IRISreader.git

run::

	$ python3 setup.py install --user
	(or in sudo mode without --user for global installation)


To test it, go to the Python 3 console and run::

	>>> from irisreader.data import sample_observation
	>>> obs = sample_observation()
	>>> obs.sji("Mg II h/k").plot(0)



