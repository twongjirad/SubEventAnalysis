import json
from datetime import datetime

f = open( '../../data/pmtratedata/README_v2.json' )
j = json.load(f)

runs = j.keys()
runs.sort()

start = datetime.strptime( "9/16/2015 14:30", "%m/%d/%Y %H:%M" )


fout = open('filter_runlist.txt','w')

for strrun in runs:
    run = int(strrun)
    if run<2378 or run>2478:
        continue
    date = j[strrun]["date"]
    t = datetime.strptime( date, "%m/%d/%Y %H:%M" )
    if "condition" not in j[strrun] or "filter" not in j[strrun]["condition"]:
        continue
    tdiff = t-start
    diff = tdiff.days*(24*3600) + (t-start).seconds
    hrs = diff/3600.0
    days = hrs/24.0
    print run,date,hrs
    print >>fout,"%d %f" % ( run, days)
