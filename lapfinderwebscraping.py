import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import pymysql as mdb
import geocoder
from bs4 import BeautifulSoup
import urllib 
import pickle
import pymysql as mdb



#read in csv with pools, their websites and their address
pools = pd.read_csv('pools.csv')

#get latitude and longitude for every pool
poolist = pools['address'].values.tolist()
poolcoord = {}
for i in poolist:
    g = geocoder.google(i)
    lon=g.geojson['geometry']['coordinates'][0]
    lat=g.geojson['geometry']['coordinates'][1]
    poolcoord[i] = (lat, lon)

#get separate latitude and longitude columns from tuples and place in dataframe
latitude = []
longitude = []
for i in pools['location']:
    i = str(i)
    latitude.append(make_tuple(i)[0])
    longitude.append(make_tuple(i)[1])

#using beautiful soup to explore and clean data
r = urllib.urlopen('http://www.nycgovparks.org/facilities/recreationcenters/B085/schedule#Pool').read()
soup = BeautifulSoup(r)
print type(soup)
#<class 'bs4.BeautifulSoup'>
soup.title
#<title>Metropolitan Recreation Center Schedule : NYC Parks</title>

#i want the swim programs in between the building hours, each time building hours shows up it represents the next day
other = ["program", "center-hrs"]
letters = soup.find_all(["p", "div"], other ) 

#want lap swim programs and building hours which separate schedule for each day
swimposting = []
otherposting = []
for i in letters:
	 #not every pool website is organized the same, some say 'Adut Lap Swim', some 'Lap Swim', some 'Adult Swim'
    if str(i).find('Adult Lap Swim') > 0:#this i changed as needed
        swimposting.append(str(i))
    if str(i).find('Building Hours') > 0:
        swimposting.append(str(i))
    else:
        otherposting.append(str(i))

days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

#make a loop that saves lap swim programs and substitutes the days of the week for the building hours which separate them
metropolitan_sched = {}
count = 0
for i in metropolitan:
    if str(i).find('Building Hours') > 0:
        metropolitan_sched[days_of_week[count]] = []
        count = count + 1
    if str(i).find('Adult Lap Swim') > 0:
        metropolitan_sched[days_of_week[count-1]].append(re.findall('[0-9]*:[0-9]*\s[a-z]\s-\s[0-9]*:[0-9]*\s[a-z]'  ,str(i)))

df = pd.DataFrame.from_dict(metropolitan_sched, orient='index')
df = df.transpose()
del df['Metropolitan Pool'] 
df['Pool'] = 'Metropolitan Pool'

'''
#will need to get ride of the list brackets
df
Monday	Tuesday	Friday	Wednesday	Thursday	Sunday	Saturday	Pool
0	[7:00 a - 9:15 a]	[7:00 a - 11:00 a]	[7:00 a - 9:15 a]	[7:00 a - 9:15 a]	[7:00 a - 11:00 a]	[10:00 a - 12:30 p]	[7:00 a - 8:45 a]	Metropolitan Pool
1	[1:30 p - 3:30 p]	[2:00 p - 3:00 p]	[5:30 p - 9:15 p]	[1:30 p - 3:30 p]	[1:30 p - 3:00 p]	None	[4:00 p - 5:15 p]	Metropolitan Pool
2	[6:30 p - 9:15 p]	[5:30 p - 9:15 p]	None	[6:30 p - 9:15 p]	[5:30 p - 9:15 p]	None	None	Metropolitan Pool
'''

#pipeline to scrape each pool, collect times for days of the week, convert to a dataframe then concatenate with the other dataframes
#this doesn't work due to inconsistencies on the different pool websites, some say lap swim, others adult lap swim and others adult swim.
#there are other non-lap swim programs so i have to scrape each separately and check.
dflist = ['df1','df2','df3', 'df4','df5', 'df6', 'df7', 'df8', 'df9', 'df10', 'df11', 'df12']
poolist = ['asser_levy', 'chelsea', 'gertrude_erdel','hansborough','tony_dapolito','brownsville','metropolitan','st.johns','flushing','roy_wilkins','st.marys','rec_center54']
failist = []

for j in range(4, 13):
    try:
        r = urllib.urlopen(pools['website_source'][j]).read()
        soup = BeautifulSoup(r)
        letters  = soup.find_all(["p", "div"], ["program", "center-hrs"] ) 
        swimposting = []
        otherposting = []
        for i in letters:
            if str(i).find('Lap Swim') > 0:
                swimposting.append(str(i))
            if str(i).find('Building Hours') > 0:
                swimposting.append(str(i))
            else:
                otherposting.append(str(i))
        pools['swimming_pool'][j] = swimposting[7:-7]
        sched = {}
        count = 0
        for s in pools['swimming_pool'][j]:
            if str(s).find('Building Hours') > 0:
                sched[days_of_week[count]] = []
                count = count + 1
            if str(s).find('Lap Swim') > 0:
                sched[days_of_week[count-1]].append(re.findall('[0-9]*:[0-9]*\s[a-z]\s-\s[0-9]*:[0-9]*\s[a-z]'  ,str(s)))
        dflist[j] = pd.DataFrame.from_dict(sched, orient='index')
        dflist[j] = dflist[j].transpose()
        specificpool = poolist[j]
        dflist[j]['Pool'] = specificpool
    except:
        failist.append(j)


#combine all dataframes from each scraped pool
allpools = pd.concat([df0,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11]) 
#need to clean up pool names and get rid of list brackets

#allpools['Monday'].iloc[1][0] removing list containing times, just want the times
f = lambda x: 'None' if x==None else x[0]
allpools['Monday']= allpools['Monday'].map(f)
allpools['Tuesday'] = allpools['Tuesday'].map(f)
allpools['Wednesday'] = allpools['Wednesday'].map(f)
allpools['Thursday'] = allpools['Thursday'].map(f)
allpools['Friday'] = allpools['Friday'].map(f)
allpools['Saturday'] = allpools['Saturday'].map(f)
allpools['Sunday'] = allpools['Sunday'].map(f)

#making sure pool names are consisitent
g = lambda x : 'Asser Levy' if x == 'asser levy' else x
allpools['Pool'] = allpools['Pool'].map(g)
h = lambda x : 'Chelsea' if x == 'chelsea' else x
allpools['Pool'] = allpools['Pool'].map(h)

#want a dictionary with the pools and their websites so i can direct users to the rec center websites for more information
poolswebsites= pd.read_csv('pools.csv')
poolswebs = poolswebsites[['swimming_pool', 'website_source']]
poolswebsdict = poolswebs.set_index('swimming_pool')['website_source'].to_dict()
poolswebsdict
pickle.dump( poolswebsdict, open("poolsandwebsites.p", "wb" ) )







