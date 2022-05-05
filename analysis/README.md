# Notebook Structure

The modeling notebooks (`Power Law Modeling.ipynb` and `Lognormal Modeling.ipynb`) run two main tasks:

- fitting the power law (or lognormal) model to each dataset
    - some figures are produced in the process, such as plots of tails and model fits
- writing batch files for bootstrapping

This is a bit time-consuming. Previously run results from these are aggregated in TSV files in `results/` and `batch/`.

The summary notebook (`Summaries and Figures.ipynb`) uses this output to produce most of the tables and figures from the paper.

# Downloading Datasets

Datasets should be downloaded separately. The path to the main datasets folder should be updated accordingly in `data.py` (`PATH_TO_DATASETS`).

# About the Datasets

Each dataset is located in a SQLite databases. The tables in these databases take different forms depending on the underlying data. A main `data.py` script is provided for easy and relatively consistent access of data from each of the datasets. The available functions are:

- Census CBSA: `get_census_cbsa_data()`
- Census Place: `get_census_place_data()`
- Census UA/UC: `get_census_uauc_data()`
- CCA Tract: `get_cca_tract_data(l)`
    - `l`: clustering distance (meters)
- CCA Raster: `get_cca_raster_data(dmin, l)`
    - `dmin`: mininum population density (people/sq km)
    - `l`: clustering distance (km)
- CCA Street Network: `get_cca_street_network_data(method, limit)`
    - `method`: counting/allocation method, one of two values (see paper for more details):
        - `"areal"`{.python}: areal weighting
        - `"full"`{.python}: full and equal allocation
    - `limit` (optional): when specified, selects only the *n* most populous cities. (The full list contains 2.9 million cities.)
- CCA Block: `get_cca_block_data(dmin, l)`
    - `dmin`: mininum density (units/sq km)
    - `l`: clustering distance (meters)

The following functions exist to expose the available parameter values for the relevant functions:

- `get_cca_tract_params()`
- `get_cca_raster_data()`
- `get_cca_block_params()`

Additionally, the following methods exist for prior year data:

- `get_cca_tract_19902000_data(l)`
- `get_census_cbsa_2000_data()`
- `get_census_cbsa_1990_data()`

## Data Fields

Every dataset has these fields at a minimum for each city or cluster:

- `population`: total population
- `jobs`: total jobs
- `area`: total (land and water) area, in sq km

Some datasets include additional fields (e.g., per-capita income, number of street nodes, number of Census tracts, total land area).

## Years Covered

The primary datasets cover the year 2010. Data for prior years are available for the Census geographies. In some cases, additional data may be available in the SQLite files that is not exposed through the functions in `data.py`. (Specifically, the SQLite DBs hold data for each of the Census geographies in 1980, 1990, 2000, and 2010.)

## Geographic Extent

All datasets cover the lower 48 states (including the District of Columbia). Some of the original datasets contain data for additional areas (e.g., Alaska and Hawaii), but for the sake of consistency, the functions in `data.py` will only return data from the cities in the lower 48.

# Running the Notebooks

These are Jupyter notebooks. To run the notebooks, fire up Jupyter in the directory containing `data.py`. If you have Docker installed, this can be accomplished with the following command:

```docker run --rm -it -p 8888:8888 -v /path/to/this/dir:/home/jovyan/analysis jupyter/scipy-notebook```
