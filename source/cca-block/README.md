# CCA Block Generation

## Overview and Requirements

The source code here is made up of a mix of Spatialite SQL and Python scripts. There are generally very few dependencies here, but if you want to run this, you'll need:

- the input data (see below)
- Python (tested with version 2.7.9)
	- argparse
- Spatialite (tested with version 4.1.1)
- GDAL (optional: `gdal_rasterize` required for generating raster maps; tested with version 1.10.1)

You'll also need a good amount of free storage space. (This will often create very large temporary files.) Having many CPUs would be helpful too, as some of the heavy lifting here will attempt to parallelize over the available CPU cores.

## Input Data

The input data is available in two files: `blockdata.sqlite` and `geometries.sqlite`. Combined, these take up about 13 GB. `blockdata.sqlite` was created by joining tabular data from the Census. `geometries.sqlite` was generated from the block Shapefiles for each of the 48 states + DC.

## How to Run

The majority of the work is performed by the `intersect.py` script:

	python intersect.py [-h] [--minprimaryland MINPRIMARYLAND] dmin l

You can ignore the `--minprimaryland` parameter. This is a parameter we developed but ultimately did not use. (It will default to 0.) What you need to provide are the positional params `dmin` (in persons/sq km) and `l` (in meters). So for example, for dmin = 3000 persons/sq km, l = 1000 m, you'd run `python intersect.py 3000 1000`. Depending on the parameters and the number of CPU cores available, this may take a long time (hours).

`intersect.py` will output a block assignment database (e.g., `output/blockassignments-X-Y-Z.sqlite`) that assigns blocks to certain clusters. If you want a nice table of cluster populations, areas, etc., you'll need to run `aggregate-clusters.py`:

	python aggregate-clusters.py

This will take all block assignment DBs in the `output` directory and create a DB called `aggregate-clusters.sqlite` with cluster data ready for analysis.

## Visualizing Clusters

If you want to view the clusters you've generated, there are two options.

### Vector (not entirely recommended)

Vectorized clusters are hard to work with, since there are millions of block polygons involved. The best way to view vectorized data is to view only a subset of the data—e.g., a given county or state. This can be done (with a bit of work) by joining the block assignments to the geometries and filtering on the `GISJOIN` column (which contains the FIPS code for each block). If you're okay with each block as its own polygon, this won't be too bad. If you want clusters to be a single polygon, you'd need to do a groupwise union (`GUnion()` in Spatialite) of the clusters, which isn't bad for small clusters but is nearly hopeless for massive clusters.

An example script, `export-buffalo-vector.sql`, is provided that exports unioned clusters for the Erie and Niagara counties of New York State. This would be called by running `spatialite buffalo-vector.sqlite < export-buffalo-vector.sql`. The Spatialite file that results (`buffalo-vector.sqlite`) can be opened in QGIS or ArcGIS, among others.

### Raster 

If you want to view a map of all clusters, your best bet is to generate a raster file. You'll lose some fidelity in the rasterization process, but the upside is that your computer won't catch fire. To generate a raster map from the block assignment DB `output/blockassignments-X-Y-Z.sqlite`, run the following:

	python rasterize.py blockassignments-X-Y-Z.sqlite

This may take a bit, but it will eventually output a GeoTIFF file at `output/blockassignments-X-Y-Z.tif`. You can open this file up with QGIS, ArcGIS, etc. The value written to band 1 is the cluster ID.
