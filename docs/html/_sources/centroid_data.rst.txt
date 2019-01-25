Centroid data
*************************

IRISreader contains functionality to access the 53 Mg II k centroids that
were found by the study

| `Identifying typical Mg II flare spectra using machine learning <https://arxiv.org/abs/1805.10494>`_.
| *B. Panos, L. Kleint, C. Huwyler, S. Krucker, M. Melchior, D. Ullmann, S. Voloshynovskiy*. 2018
| Astrophysical Journal, Volume 861, Number 1
|
 
The centroids were created in a semi-supervised way to provide a dictionary
for the different observed solar flare physics in the Mg II k line.

IRISreader provides functions to assign these centroids to arbitrary
observations containing the Mg II k line window.





=================================================
irisreader.data.mg2k_centroids.get_mg2k_centroids
=================================================

.. autofunction:: irisreader.data.mg2k_centroids.get_mg2k_centroids

====================================================
irisreader.data.mg2k_centroids.assign_mg2k_centroids
====================================================

.. autofunction:: irisreader.data.mg2k_centroids.assign_mg2k_centroids

==========================================
irisreader.data.mg2k_centroids.normalize
==========================================

.. autofunction:: irisreader.data.mg2k_centroids.normalize

==========================================
irisreader.data.mg2k_centroids.interpolate
==========================================

.. autofunction:: irisreader.data.mg2k_centroids.interpolate

======================================================
irisreader.data.mg2k_centroids.get_mg2k_centroid_table
======================================================

.. autofunction:: irisreader.data.mg2k_centroids.get_mg2k_centroid_table

