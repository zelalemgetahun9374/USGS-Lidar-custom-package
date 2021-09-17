# USGS-Lidar-custom-package

## Overview
This Python package allows you to retrieve, manipulate, and visualize point cloud data. The main features of the package are the following.
1. The ability to accept a field boundary polygon in a geopandas dataframe in any coordinate reference system (CRS) and a desired output CRS and return a python dictionary with all available years of data and a geopandas grid point file with elevations encoded in the requested CRS.
2. The ability to provide an option to graphically display the returned elevation files as a 3D render plot.
3. The ability to apply sub-sampling to point cloud data based on resolution.

## Dependancies
This package is dependent on the following python packages.
* PDAL
* Laspy
* Geopandas

