data: \
	sessions \
	download_1-112 \
	save_1-112 \
	download_113 \
	save_113_lookup \
	download_116 \
	save_116 \
	simplify \
	save_113_display \
	cleanup

sessions:
	python scripts/index_sessions.py

download_1-112:
	curl -o congressional-district-boundaries.zip -L https://github.com/JeffreyBLewis/congressional-district-boundaries/archive/master.zip
	unzip congressional-district-boundaries.zip

save_1-112:
	python scripts/save_1-112.py

download_113:
	mkdir -p tl_rd13_us_cd113
	curl -O https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_cd113.zip
	unzip -d tl_rd13_us_cd113 tl_rd13_us_cd113.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 tl_rd13_us_cd113.geojson tl_rd13_us_cd113/tl_rd13_us_cd113.shp
	mkdir -p cb_2013_us_cd113_5m
	curl -O https://www2.census.gov/geo/tiger/GENZ2013/cb_2013_us_cd113_5m.zip
	unzip -d cb_2013_us_cd113_5m cb_2013_us_cd113_5m.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 cb_2013_us_cd113_5m.geojson cb_2013_us_cd113_5m/cb_2013_us_cd113_5m.shp

save_113_lookup:
	python scripts/save_113_lookup.py

download_116:
	mkdir -p pa_116
	curl -o pa_116.zip http://www.pacourts.us/assets/files/setting-6061/file-6845.zip?cb=b6385e
	unzip -d pa_116 pa_116.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 pa_116.geojson pa_116/Remedial\ Plan\ Shapefile.shp

save_116:
	python scripts/save_116.py

simplify:
	python ./scripts/simplify.py

save_113_display:
	python scripts/save_113_lookup.py
	
cleanup:
	rm congressional-district-boundaries.zip
	rm -rf congressional-district-boundaries-master/
	rm tl_rd13_us_cd113.zip
	rm -rf tl_rd13_us_cd113/
	rm tl_rd13_us_cd113.geojson
	rm pa_116.zip
	rm -rf pa_116/
	rm pa_116.geojson
	rm cb_2013_us_cd113_5m.zip
	rm -rf cb_2013_us_cd113_5m/
	rm cb_2013_us_cd113_5m.geojson

spatialite:
	python scripts/index_spatialite.py

postgis:
	python scripts/index_postgis.py

datasette_inspect:
	datasette inspect us-congress.db --inspect-file inspect-data.json --load-extension=/usr/local/lib/mod_spatialite.dylib
