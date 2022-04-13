import sqlite3

# "Holds" data from blockconnections
class ConnectionData:
	# dbs = { state: sqlite3, ... }
	def __init__(self, dbfilenames):
		self.init_db(dbfilenames)
		self.init_data()
		
	def init_db(self, dbfilenames):
		self.dbs = {}
		for state in dbfilenames:
			self.dbs[state] = sqlite3.connect(dbfilenames[state])

		self.curs = {}
		for state in self.dbs:
			self.curs[state] = self.dbs[state].cursor()
	
	def init_data(self):
		blocks = []
		for state in self.curs:
			for row in self.curs[state].execute("SELECT gisjoin FROM blockconnections"):
				blocks.append(row[0])
		self.unprocessedblocks = set(blocks)
	
	def has_any_unprocessed(self):
		return len(self.unprocessedblocks) > 0
	
	def is_unprocessed(self, id):
		return id in self.unprocessedblocks
	
	def get_next(self):
		return next(iter(self.unprocessedblocks))
	
	def process_connections(self, id):
		state = id[1:3]
		row = self.curs[state].execute("SELECT blocks FROM blockconnections WHERE gisjoin = ?", (id,)).fetchone()
		self.unprocessedblocks.remove(id)
		return row[0].split(",")
	
	def close(self):
		for state in self.dbs:
			self.dbs[state].close()

# Given an id (key) from `connections`, add it to the `cluster` set, and remove from `connections`.
# Return set of unprocessed connected IDs.
def add_to_cluster(id, cluster, connections):
	cluster.add(id)
	connectedblocks = connections.process_connections(id)
	return set([cid for cid in connectedblocks if connections.is_unprocessed(cid) ])

def generate_clusters(connections):
	while connections.has_any_unprocessed():
		cluster = set()
		queue = set([connections.get_next()])
		while len(queue) > 0:
			id = queue.pop()
			queue = queue.union(add_to_cluster(id, cluster, connections))
		yield cluster

def write_assignments(dbfilename, clustergenerator, removedupes):
	db = sqlite3.connect(dbfilename)
	cur = db.cursor()
	cur.execute("""CREATE TABLE blockassignments (
					gisjoin TEXT,
					clusterid INTEGER
				)""")
	
	clusterid = 1
	for cluster in clustergenerator:
		values = [ (id, clusterid) for id in cluster ]
		cur.executemany("INSERT INTO blockassignments (gisjoin, clusterid) VALUES (?, ?)", values)
		clusterid += 1
	
	cur.execute("CREATE INDEX blockassignmentsgisjoin ON blockassignments (gisjoin)")
	cur.execute("CREATE INDEX blockassignmentsclusterid ON blockassignments (clusterid)")
	
	if removedupes:
		print("merging duplicates")
		# get gisjoin, clusterid, numblocks
		# for any block assigned to >1 cluster
		result = cur.execute("""SELECT a.gisjoin, a.clusterid, COUNT(*) ct FROM blockassignments a
							INNER JOIN blockassignments b ON b.clusterid = a.clusterid
							WHERE a.gisjoin IN (SELECT gisjoin FROM blockassignments GROUP BY gisjoin HAVING COUNT(*) > 1)
							GROUP BY a.gisjoin, b.clusterid
							ORDER BY a.gisjoin, COUNT(*) DESC""")
		prevclusterid = 0
		for row in result:
			if row["clusterid"] == prevclusterid:
				print("dropping assignment: " + row["gisjoin"] + "-" + row["clusterid"])
				cur.execute("DELETE FROM blockassignments WHERE gisjoin = ? AND clusterid = ?", (row["gisjoin"], row["clusterid"]))
			prevclusterid = row["clusterid"]
	
	db.commit()
	db.close()
