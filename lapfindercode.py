import geocoder
import pandas as pd
import pymysql as mdb
import numpy as np
import time
from geopy.distance import vincenty
import pickle

#the function takes a user entered address
def addresscoord(startaddress):
    g = geocoder.google(startaddress)
    lon=g.geojson['geometry']['coordinates'][0]
    lat=g.geojson['geometry']['coordinates'][1]
    #converts the address to a tuple of latitude and longitude
    me = (lat, lon)
    #open an dictionary of the NYC rec centers with indoor pools and their lat and lon coordinates
    poolsdict = pickle.load(open("app/static/poolsandcoords.p", "rb"))
    mindict = {}
    localmin = 0
    #this compares the distance between the users address and each pool and finds the closest one
    #as the crow flies
    for i in poolsdict:
        dist = vincenty(me, poolsdict[i]).miles
        if localmin == 0:
            localmin = dist
        if dist < localmin:
            localmin = dist
            mindict[localmin] = i
        else:
            continue
    #retrieve closest pool
    closepool = mindict[localmin]
    #get the current day of the week
    now = time.strftime("%A")
    #connect to the database
    con = mdb.connect('localhost', 'root', '', 'lap_schedule')
    #select from two tables, the information for the closest pool:lap hours and address
    poolhoursplace = pd.read_sql('SELECT p.Pool, a.address, p.%s FROM lap_schedule_table5 AS p JOIN pool_table6 AS a ON p.Pool = a.swimming_pool WHERE Pool = "%s"' %(now, closepool) , con)
    pooladdress = poolhoursplace['address'].iloc[0]
    #get laps for the day
    laplist = poolhoursplace.ix[:, 2:].values.tolist()
    laphours = []
    for i in laplist:
        if i[0] == 'None':
            continue
        else:
            laphours.append(i[0])
    #get day and date
    today = time.strftime("%A %D")
    #retrieve the pool website to return to the user
    poolswebsdict = pickle.load(open("app/static/poolsandwebsites.p", "rb"))
    website = poolswebsdict[closepool]
    #get full lap schedule for the closest pool
    cur = con.cursor()
    cur.execute('SELECT Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday FROM  lap_schedule_table5 WHERE Pool = "%s";' %(closepool))
    query_results = cur.fetchall()
    #get the results for each day
    hours = []
    for result in query_results:
        hours.append(dict(Monday=result[0], Tuesday=result[1], Wednesday=result[2], Thursday=result[3], Friday=result[4],Saturday=result[5], Sunday=result[6]))
  
    return closepool, pooladdress, laphours, today, website, hours