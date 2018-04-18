#!/bin/env python

import json, os, sys, optparse
import us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils
import postgres_db, simplify

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

opt_parser = optparse.OptionParser()
opt_parser.add_option('-s', '--start', dest='start', type='int', action='store', default=None, help='Start session (e.g. 113)')
opt_parser.add_option('-e', '--end', dest='end', type='int', default=None, action='store', help='End session (e.g. 115)')
opt_parser.add_option('-t', '--type', dest='type', action='store', default=None, help='Either display or lookup.')
opt_parser.add_option('-i', '--include', dest='include', default=None, action='store', help='States to include (fl,nc,va)')
opt_parser.add_option('-x', '--exclude', dest='exclude', default=None, action='store', help='States to exclude (fl,nc,va)')
options, args = opt_parser.parse_args()

if options.include:
	options.include = options.include.split(",")

if options.exclude:
	options.exclude = options.exclude.split(",")

district_prop = "CD%sFP" % options.start

base = "%s_%s" % (options.start, options.type)
path = "%s/sources/%s/%s.geojson" % (root_dir, base, base)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("SELECT id, start_date, end_date FROM sessions")
rs = cur.fetchall()
sessions = {}
if rs:
	for row in rs:
		id = row[0]
		sessions[id] = {
			"start_date": str(row[1]),
			"end_date": str(row[2])
		}

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading %s.geojson" % base)
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state_fips = props["STATEFP"]
	state = us.states.lookup(state_fips).abbr
	state = str(state).lower()

	if options.include and state not in options.include:
		continue

	if options.exclude and state in options.exclude:
		continue

	if props[district_prop] == "ZZ":
		continue

	district = int(props[district_prop])

	id = "%s_%s_to_%s_%s" % (state, options.start, options.end, district)
	name = "%s.%s.geojson" % (id, options.type)
	path = "%s/data/%s/%s" % (root_dir, state, name)

	feature["properties"] = {
		"state": state,
		"start_session": options.start,
		"start_date": sessions[options.start]["start_date"],
		"end_session": options.end,
		"end_date": sessions[options.end]["end_date"],
		"district": district
	}
	feature["id"] = id

	mapzen.whosonfirst.utils.ensure_bbox(feature)
	feature["properties"]["area"] = area.area(feature["geometry"])

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	print("Saving %s" % name)
	with open(path, 'w') as outfile:
		if options.type == "display":
			json.dump(feature, outfile)
		else:
			encoder.encode_feature(feature, outfile)

	if options.type == "display":
		print("Simplifying %s" % name)
		simplify.simplify(path)