from setuptools import setup, find_packages

setup(name='irisreader',
      version='0.3.0',
      description='IRISreader is a Python library that allows for efficient browsing through IRIS satellite data in order to simplify machine learning applications',
      url='https://www.github.com/i4Ds/IRISreader',
      author='Cedric Huwyler',
      author_email='cedric.huwyler@fhnw.ch',
      license='MIT',
      packages=find_packages(),
      package_data={'irisreader': ['data/*.fits', 'data/20140518_151415_3820607204/*.fits', 'data/*.npz'] },
      install_requires=['numpy', 'pandas', 'matplotlib', 'astropy', 'scipy', 'scikit-learn', 'requests', 'beautifulsoup4', 'tqdm', 'ipython'],
      download_url='https://github.com/i4Ds/IRISreader/archive/v0.3.0.tar.gz',
      zip_safe=False)

