PRAGMA main.journal_mode = OFF;

ATTACH DATABASE '{{BUFFEREDBLOCKDB}}' AS bb;

CREATE TABLE blockconnections (
	gisjoin TEXT,
	blocks TEXT
);

INSERT INTO blockconnections
SELECT
	source.gisjoin,
	GROUP_CONCAT(inter.gisjoin)
FROM bb.bufferedblocks source, bb.bufferedblocks inter
WHERE
	source.gisjoin LIKE 'G{{STATECODE}}%'
	AND
	source.arealand >= {{MINPRIMARYLAND}}
	AND
	Intersects(source.Geometry, inter.Geometry)
	AND
	inter.ROWID IN (SELECT pkid FROM idx_bufferedblocks_Geometry
					WHERE xmin <= MbrMaxX(source.Geometry)
						AND ymin <= MbrMaxY(source.Geometry)
						AND xmax >= MbrMinX(source.Geometry)
						AND ymax >= MbrMinY(source.Geometry))
GROUP BY source.gisjoin;

CREATE INDEX blockconnectionsgisjoin ON blockconnections (gisjoin);
