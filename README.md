# Wildfire-Risk-Model
This is the code for my final project in my GIS with Python course in the fall for 2025.  

# Fire Risk Tool

## Data Used:

https://usu.box.com/s/uslmhcxyr7ecbin8djrfu0z2mv5lpe0j

## Purpose:

This tool is used for creating a fire risk model using 4 criteria. These criteria are as follows

- Slope with 25% grade or higher
- South facing aspects
- Areas that are within 1km of a road
- Using Rothermel’s 40 Surface Fire Spread Model, areas with a rate of spread that is medium or higher and a flame length that is medium or higher

These 4 criteria create a model with values of 0 to 4 of no risk to very high risk

## Inputs:

A DEM layer - raster layer .tif

A road layer - feature layer .shp

Landfire Rothermel’s 40 Surface Fire Spread Model data - raster layer .tif

A target boundary - feature layer .shp
Input Tips:

The Fuel model data needs to be from Landfire's data due to attribute naming.

The target boundary is something you set up yourself. It needs to have a projection as the model will end in the same projection as the boundary

## Output:

The fire risk model - raster layer .tif

This will display in Arcgis once run

## Other Details:

Required ArcGIS extensions: ArcGIS Spatial Analyst

Common errors or troubleshooting tips: Currently none, report any that are found

Credits: Landfire.gov
