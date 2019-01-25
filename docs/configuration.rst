Configuration
******************************************

IRISreader can be configured over irisreader.config, an instance of the 
irisreader.config_template class. Below is the documentation of the different available
options.

The current settings can be printed out with::
	
	>>> import irisreader as ir
	>>> print( ir.config )
	IRISreader configuration:
	---------------------------
	default_mirror: lmsal
	goes_base_url: https://satdat.ngdc.noaa.gov/sem/goes/data/full/
	hek_url: http://www.lmsal.com/hek/her
	max_open_files: 256
	mirrors: {'lmsal': 'http://www.lmsal.com/solarsoft/irisa/data/level2_compressed/', 'uio': 'http://sdc.uio.no/vol/fits/iris/level2/', 'fhnw': 'http://server1071.cs.technik.fhnw.ch/data/'}
	use_memmap: False
	verbosity_level: 1

And options can be set via::

	>>> ir.config.option = value


==========================================
irisreader.config_template
==========================================
 
.. autoclass:: irisreader.config_template
   :members:
   :inherited-members:
