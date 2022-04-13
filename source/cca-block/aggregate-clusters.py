import glob
import re
import sqlite3

db = sqlite3.connect("output/aggregate-clusters.sqlite")
cur = db.cursor()

cur.execute("ATTACH DATABASE 'import/blockdata.sqlite' AS bd")
cur.execute("""CREATE TABLE clusters (
					clusterid INTEGER,
					dmin INTEGER, -- min density parameter (units/km^2)
					l INTEGER, -- allowable distance parameter (m)
					ptype TEXT, -- population type parameter (P = population, A = "all" = max { jobs, population })
					minprimaryarea INTEGER, -- minimum land area parameter for primary blocks (m^2)
					population INTEGER,
					jobs INTEGER,
					arealand NUMERIC,
					areatotal NUMERIC,
					numblocks INTEGER,
					PRIMARY KEY (ptype, dmin, l, minprimaryarea, clusterid)
				)""")

def insert_clusters(dbfilename, dmin, l, ptype, minprimaryarea):
	print(dbfilename)
	cur.execute("ATTACH DATABASE '" + dbfilename + "' AS ba")
	cur.execute("""INSERT INTO clusters
					SELECT
						a.clusterid,
						?,
						?,
						?,
						?,
						SUM(b.population),
						SUM(b.jobs),
						SUM(b.arealand),
						SUM(b.areatotal),
						COUNT(*)
					FROM bd.blocks b
					INNER JOIN ba.blockassignments a USING (gisjoin)
					GROUP BY a.clusterid""", (dmin, l, ptype, minprimaryarea))
	cur.execute("DETACH DATABASE ba")

assignmentdbs = glob.glob("output/blockassignments*.sqlite")
for f in assignmentdbs:
	match = re.search("blockassignments-([AP])-([0-9]+)-([0-9]+)-([0-9]+)\.sqlite", f)
	if match:
		type = match.group(1)
		dmin = int(match.group(2))
		l = int(match.group(3))
		minprimaryarea = int(match.group(4))
		
		insert_clusters(f, dmin, l, type, minprimaryarea)

db.commit()
db.close()
