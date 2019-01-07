from setuptools import setup, find_packages

setup(name='irisreader',
      version='0.3.0',
      description='IRISreader is a Python library that allows for efficient browsing through IRIS satellite data in order to simplify machine learning applications',
      url='https://www.github.com/i4Ds/IRISreader',
      download_url='https://www.github.com/i4Ds/IRISreader',
      author='Cedric Huwyler',
      author_email='cedric.huwyler@fhnw.ch',
      license='MIT',
      packages=find_packages(),
      package_data={'irisreader': ['data/*.fits', 'data/20140518_151415_3820607204/*.fits', 'data/*.npz'] },
      install_requires=['numpy>=1.14.3', 'pandas>=0.23.0', 'matplotlib>=2.2.2', 'astropy>=3.0.2', 'scipy>=1.1.0', 'scikit-learn>=0.19.1', 'requests>=2.18.4', 'beautifulsoup4>=4.6.0', 'tqdm>=4.19.6'],
      test_suite='irisreader.test',
      zip_safe=False)

