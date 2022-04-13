import argparse
import os
import subprocess
import re

parser = argparse.ArgumentParser()
parser.add_argument("db", help="Name of blockassignmnents sqlite file (e.g., blockassignments-1500-1000.sqlite)")
parser.add_argument("--resolution", type=int, default=100, help="Resolution (in meters)")

args = parser.parse_args()
db = "output/" + args.db
paramstring = re.sub("[a-z.]", "", args.db) # e.g., "-A-1500-1000-0"
resolution = args.resolution

if not os.path.exists(db):
	raise ValueError(db + " doesn't exist.")

sql = """
PRAGMA main.journal_mode = OFF;

ATTACH DATABASE '{{DBFILE}}' AS ba;
ATTACH DATABASE 'import/geometries.sqlite' AS geo;

INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 102003, 'esri', 102003, '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs ', 'PROJCS["USA_Contiguous_Albers_Equal_Area_Conic",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["longitude_of_center",-96],PARAMETER["Standard_Parallel_1",29.5],PARAMETER["Standard_Parallel_2",45.5],PARAMETER["latitude_of_center",37.5],UNIT["Meter",1],AUTHORITY["EPSG","102003"]]');

CREATE TABLE blocks (
    clusterid INTEGER
);

SELECT AddGeometryColumn('blocks', 'Geometry', 102003, 'MULTIPOLYGON', 'XY');

INSERT INTO blocks
SELECT a.clusterid, Geometry
FROM geo.blocks b
INNER JOIN ba.blockassignments a USING (gisjoin);
"""

print("Start: " + db)
print("Creating vector DB...")


sqlfilename = "temp/rasterize" + paramstring + ".sql"
tempdbfilename = "temp/rasterize" + paramstring + ".sqlite"
with open(sqlfilename, "w+") as f:
	with open(os.devnull, "w") as out:
		f.write(sql.replace("{{DBFILE}}", db))
		f.flush()
		f.seek(0)
		subprocess.call([ "spatialite", tempdbfilename ], stdin=f, stdout=out, stderr=out)
os.remove(sqlfilename)

print "Rasterizing..."

outputfilename = db.replace(".sqlite", ".tif")

subprocess.call([ "gdal_rasterize", "-at", "-a", "clusterid", "-a_nodata", "0", "-l", "blocks", "-tr", str(resolution), str(resolution), "-ot", "Int32", "-co", "COMPRESS=LZW", tempdbfilename, outputfilename ])

os.remove(tempdbfilename)
print("End: " + db)
