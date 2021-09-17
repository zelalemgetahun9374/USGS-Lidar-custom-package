# USGS-Lidar-custom-package

**Table of Contents**

- [USGS-Lidar-custom-package](#USGS-Lidar-custom-package)
  - [Overview](#overview)
  - [Scenario](#scenario)
  - [Approach](#approach)
  - [Project Structure](#project-structure)
    - [assets](#assets)
    - [notebooks](#notebooks)
    - [scripts](#scripts)
    - [tests](#tests)
    - [logs](#logs)
    - [root folder](#root-folder)
  - [Dependancies](#Dependancies)

## Overview

This Python package allows you to retrieve, manipulate, and visualize USGS 3DEP lidar point cloud data.

## Scenario
You work at an AgriTech, which has a mix of domain experts, data scientists, data engineers. As part of the data engineering team, you are tasked to produce an easy to use, reliable and well designed python module that domain experts and data scientists can use to fetch, visualise, and transform publicly available satellite and LIDAR data. In particular, your code should interface with USGS 3DEP and fetch data using their API. 

## Approach
The project is divided and implemented by the following phases
- Fetching point cloud data of all available year of given a boundary polygon in any coordinate reference system (CRS)
- Graphically displaingy returned elevation files as a 3D render plot.
- Sub-sampling point cloud data based on given resolution.

## Project Structure
The repository has a number of files including python scripts, jupyter notebooks, pdfs and text files. Here is their structure with a brief explanation.

### assets:
- `get_data.json`: a json template used for fetching data using pdal
- `usgs_3dep_metadata.csv`: a csv file scrapped from [usgs.entwine.io](https://usgs.entwine.io/) containing data about regions and their boundary points along with the year it is collected

### notebooks:
- `example.ipynb`: a jupyter notebook showing how to use this custom package

### scripts:
- `app_logger.py`: a python script for logging
- `file_handler.py`: a python script for handling reading and writing of csv, pickle and other files
- `lidar_processor.py`: the main python script of this project that does the fetching, displaying and sub-sampling

### tests:
- the folder containing unit tests for components in the scripts

### logs:
- the folder containing log files (if it doesn't exist it will be created once logging starts)

### root folder
- `10 Academy Batch 4 - Week 6 Challenge.pdf`: the challenge document
- `requirements.txt`: a text file lsiting the projet's dependancies
- `setup.py`: a configuration file for installing the scripts as a package
- `README.md`: Markdown text with a brief explanation of the project and the repository structure.

## Dependancies
This package is dependent on the following python packages.
* PDAL
* Shapely
* Geopandas
* Matplotlib
