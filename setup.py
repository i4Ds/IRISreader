from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='irisreader',
      version='0.3.2',
      description='IRISreader is a Python library that allows for efficient browsing through IRIS satellite data in order to simplify machine learning applications',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://www.github.com/i4Ds/IRISreader',
      author='Cedric Huwyler',
      author_email='cedric.huwyler@fhnw.ch',
      license='MIT',
      packages=find_packages(),
      package_data={'irisreader': ['data/*.fits', 'data/20140518_151415_3820607204/*.fits', 'data/*.npz'] },
      install_requires=['numpy', 'pandas', 'matplotlib', 'astropy', 'scipy', 'scikit-learn', 'requests', 'beautifulsoup4', 'tqdm', 'ipython'],
      download_url='https://github.com/i4Ds/IRISreader/archive/v0.3.2.tar.gz',
      zip_safe=False)

