PRAGMA main.journal_mode = OFF;

ATTACH DATABASE 'import/blockdata.sqlite' AS bd;
ATTACH DATABASE 'import/geometries.sqlite' AS geo;

INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 102003, 'esri', 102003, '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs ', 'PROJCS["USA_Contiguous_Albers_Equal_Area_Conic",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["longitude_of_center",-96],PARAMETER["Standard_Parallel_1",29.5],PARAMETER["Standard_Parallel_2",45.5],PARAMETER["latitude_of_center",37.5],UNIT["Meter",1],AUTHORITY["EPSG","102003"]]');

CREATE TABLE bufferedblocks (
	gisjoin TEXT,
	arealand INTEGER -- square meters!
);

SELECT AddGeometryColumn('bufferedblocks', 'Geometry', 102003, 'MULTIPOLYGON', 'XY');

INSERT INTO bufferedblocks (gisjoin, arealand, Geometry)
SELECT gisjoin, geo.blocks.arealand, CastToMultiPolygon(Buffer(Geometry, {{BUFFERSIZE}}))
FROM geo.blocks
INNER JOIN bd.blocks USING (gisjoin)
WHERE 1.0*bd.blocks.activepopulation/bd.blocks.arealand >= {{DENSITYMIN}};

SELECT CreateSpatialIndex('bufferedblocks', 'Geometry');
