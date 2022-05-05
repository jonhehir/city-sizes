import sqlite3
import pandas
import os


PATH_TO_DATASETS = "./datasets"

def query_db(dbname, sql, params=()):
    dbs = {
        "censuscbsa": "census/msas.sqlite",
        "censusplace": "census/places.sqlite",
        "censusuauc": "census/urbanareas.sqlite",
        "ccablock": "cca-block/clusters.sqlite",
        "ccaraster": "cca-raster/all.sqlite",
        "ccatract19902000": "cca-tract/original.sqlite",
        "ccatract": "cca-tract/2010.sqlite",
        "ccastreetnetwork": "cca-street-network/combined.sqlite"
    }
    
    db = sqlite3.connect(os.path.join(PATH_TO_DATASETS, dbs[dbname]))
    results = pandas.read_sql(sql, db, params=params)
    db.close()
    return results

def get_cca_tract_19902000_data(l, mintracts=1):
  return query_db("ccatract19902000",
    "SELECT clusterid AS id, SUM(pop2000) AS population, SUM(area_sqkm) AS area, numtracts \
    FROM tracts \
    INNER JOIN tractassignments USING (fips) \
    INNER JOIN clustersizes USING (clusterid, l) \
    WHERE tractassignments.l = ? AND clustersizes.numtracts >= ? \
    GROUP BY clusterid \
    ORDER BY population DESC", (l, mintracts))

def get_cca_tract_19902000_params():
  return query_db("ccatract19902000", "SELECT DISTINCT l FROM clustersizes")

def get_cca_tract_data(l, mintracts=1):
    return query_db("ccatract",
    "SELECT clusterid AS id, SUM(population) AS population, SUM(area_sqkm) AS area, SUM(arealand_sqkm) AS arealand, SUM(jobs) AS jobs, numtracts \
    FROM tracts \
    INNER JOIN tractassignments USING (fips) \
    INNER JOIN clustersizes USING (clusterid, l) \
    WHERE tractassignments.l = ? AND clustersizes.numtracts >= ? \
    GROUP BY clusterid \
    ORDER BY population DESC", (l, mintracts))

def get_cca_tract_params():
  return query_db("ccatract", "SELECT DISTINCT l FROM clustersizes")

def get_cca_raster_data(dmin, l):
  return query_db("ccaraster",
    "SELECT clusterid AS id, SUM(blockpopulation) AS population, SUM(blockjobs) AS jobs, SUM(area) AS area \
    FROM cells \
    INNER JOIN cellassignments \
    ON \
      cellassignments.dmin = ? \
      AND cellassignments.l = ? \
      AND cellassignments.x = cells.x \
      AND cellassignments.y = cells.y \
    GROUP BY clusterid \
    ORDER BY population DESC", (dmin, l))

def get_cca_raster_params():
    return query_db("ccaraster", "SELECT DISTINCT dmin, l FROM cellassignments")

def get_cca_block_data(dmin, l):
  return query_db("ccablock",
          "SELECT clusterid AS id, population, jobs, arealand, areatotal AS area, numblocks \
          FROM clusters \
          WHERE ptype = 'A' AND minprimaryarea = 0 \
          AND dmin = ? AND l = ? \
          AND population >= 50 \
          ORDER BY population DESC", (dmin, l))

def get_cca_block_params():
  # There are a couple of other parameters in this dataset (ptype, minprimaryarea), but we're not using them.
  # (Really, we're always setting them to A and 0, respectively.)
  # These were from some alterations to the algorithm that we experimented with and ultimately rejected.
  # Pretend they don't exist.
  return query_db("ccablock",
          "SELECT DISTINCT dmin, l \
          FROM clusters \
          WHERE ptype = 'A' AND minprimaryarea = 0 \
          ORDER BY population DESC")

def get_cca_street_network_data(method, limit=10000000):
  if not method in ["areal", "full"]:
    print("method must be either \"areal\" or \"full\"")
    return
  
  return query_db("ccastreetnetwork",
            "SELECT id, population_" + method + " AS population, \
            jobs_" + method + " AS jobs, junctioncount, area \
            FROM naturalcities \
            ORDER BY population DESC LIMIT ?", (limit,))

def get_census_cbsa_data():
  return query_db("censuscbsa",
          "SELECT msaid AS id, name, population, totaljobs AS jobs, percapitaincome, totalincome, area, arealand \
          FROM msas2010 \
          WHERE lower48 = 1 \
          ORDER BY population DESC")

def get_census_cbsa_2000_data():
  return query_db("censuscbsa",
          "SELECT msaid AS id, name, population, percapitaincome, totalincome \
          FROM msas2000 \
          WHERE lower48 = 1 \
          ORDER BY population DESC")

def get_census_cbsa_1990_data():
  return query_db("censuscbsa",
          "SELECT msaid AS id, name, population, percapitaincome, totalincome \
          FROM msas1990 \
          WHERE lower48 = 1 \
          ORDER BY population DESC")

def get_census_place_data():
  return query_db("censusplace",
          "SELECT placegeoid AS id, name, statename, population, totaljobs AS jobs, percapitaincome, totalincome, area, arealand \
          FROM places2010 \
          WHERE lower48 = 1 \
          ORDER BY population DESC")

def get_census_uauc_data():
  return query_db("censusuauc",
          "SELECT urbanid AS id, name, population, totaljobs AS jobs, percapitaincome, totalincome, area, arealand \
          FROM urbanareas2010 \
          WHERE lower48 = 1 \
          ORDER BY population DESC")
