import cluster

import argparse
import datetime
from multiprocessing import Pool
import os
import subprocess

states = ["01", "04", "05", "06", "08", "09", "10", "11", "12", "13", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56"]

def print_with_timestamp(message):
	print(str(datetime.datetime.now()) + " " + message)

def write_sql_file(template, filename, replacements):
	with open(template) as ftpl:
		sql = ftpl.read()
		for key in replacements:
			sql = sql.replace("{{" + key + "}}", replacements[key])
	with open(filename, "w+") as fsql:
		fsql.write(sql)

def execute_spatialite(dbfilename, template, replacements):
	print_with_timestamp("Building " + dbfilename)
	
	# Generate the SQL
	sqlfilename = dbfilename[:-3] # .sqlite -> .sql
	write_sql_file(template, sqlfilename, replacements)
	
	# Call spatialite
	with open(sqlfilename) as input:
		with open(os.devnull, "w") as output:
			subprocess.call([ "spatialite", dbfilename ], stdin=input, stderr=output, stdout=output)
	
	# Delete SQL
	os.remove(sqlfilename)

def execute_spatialite_tuple(args):
	execute_spatialite(*args) # unpack from tuple

# Delete db if it exists, otherwise just be quiet.
# This makes life easier when you want to comment out parts of the script 
# and not have cleanup tasks throw fits.
def try_delete_db(db):
	try:
		os.remove(db)
	except OSError:
		pass

# Note: this will buffer blocks from all states, not just the states in the states list.
def buffer_blocks():
	template = "intersect-buffer.sql.tpl"
	db = "temp/buffered-A-" + str(dmin) + "-" + str(l) + ".sqlite"
	replacements = { "BUFFERSIZE": str(1.0*l/2), "DENSITYMIN": str(1.0*dmin) }
	
	print_with_timestamp("Begin buffering")
	execute_spatialite(db, template, replacements)
	print_with_timestamp("End buffering")
	
	return db

# This will, in fact, only handle the specified states.
# This is generally the slowest (or at least the most CPU-intensive) part of the process.
# For parallelization purposes, we process each state separately.
def intersect_states(bbdb):
	print_with_timestamp("Begin intersecting")
	
	executions = []
	statedbs = {}
	for state in states:
		template = "intersect-state.sql.tpl"
		db = "temp/intersect-A-" + str(dmin) + "-" + str(l) + "-" + str(minprimaryland) + "-" + state + ".sqlite"
		replacements = { "BUFFEREDBLOCKDB": bbdb, "STATECODE": state, "MINPRIMARYLAND": str(minprimaryland) }
		executions.append((db, template, replacements))
		statedbs[state] = db
	
	pool = Pool()
	pool.map(execute_spatialite_tuple, executions)
	pool.close()
	
	print_with_timestamp("End intersecting")
	
	return statedbs

def assign_blocks_to_clusters(statedbs):
	print_with_timestamp("Begin clustering")
	
	conndata = cluster.ConnectionData(statedbs)
	clustergen = cluster.generate_clusters(conndata)
	db = "output/blockassignments-A-" + str(dmin) + "-" + str(l) + "-" + str(minprimaryland) + ".sqlite"
	
	removedupes = minprimaryland > 0
	cluster.write_assignments(db, clustergen, removedupes)
	conndata.close()
	
	print_with_timestamp("End clustering")
	
	return db

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("dmin", type=int, help="Minimum density threshold parameter (in units/km^2)")
parser.add_argument("l", type=int, help="Clustering distance parameter (in meters)")
parser.add_argument("--minprimaryland", type=int, default=0, help="Minimum land area for primary blocks (in m^2)")
args = parser.parse_args()
dmin = args.dmin
l = args.l
minprimaryland = args.minprimaryland

print_with_timestamp("Starting (l = " + str(1.0*l/1000) + " km, dmin = " + str(dmin) + " units/km^2, minprimaryland = " + str(1.0*minprimaryland/1000**2) + " km^2)")

bbdb = buffer_blocks()
statedbs = intersect_states(bbdb)

print_with_timestamp("Deleting buffer DB")
try_delete_db(bbdb)

assign_blocks_to_clusters(statedbs)

print_with_timestamp("Deleting intersection DBs")
for state in statedbs:
	try_delete_db(statedbs[state])

print_with_timestamp("Done")
