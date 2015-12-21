# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 13:10:10 2015

@author: Derek
"""

#This script is going to check whether or not a property is
#in the tsunami inundation zone. The inputs will be:
#1: GIS layer of inundation zone (polygon)
#2: Point features from a flat file. 
#Result will be a database with each entity and its associated
#--- inundation status: YES or NO (1 or 0)
#Process will use a check to verify if the layers intersect each other. 
import csv
import sqlite3
from osgeo import ogr
#--- Utility Functions ---
#OPEN FLAT FILE using csv
entities = "C:/Users/Derek/dropbox/Thesis/recoverysim/HousingwithCoords.csv"
addresses = []

with open(entities, 'rb') as myfile:
    reader = csv.reader(myfile)
    count = -1
    for row in reader:
        addresses.append([count,row[6],row[7],row[8]])
        count += 1
    addresses.pop(0)
    
#connect to database (open a schema file or write one on fly)
db = "C:/Users/Derek/dropbox/Thesis/recoverysim/housingDB.db"
con = sqlite3.connect(db, isolation_level=None) #Connect obj
cur = con.cursor() #cursor obj

# --- load inundation data as an OGR polygon class for use later ---

#Shapefile path
daShapefile = r"C:\Users\Derek\Dropbox\Thesis\PacCountyGIS\maybe.shp"
driver = ogr.GetDriverByName("ESRI Shapefile") #get driver from ogr
dataSource = driver.Open(daShapefile, 0) #use driver's open method to return the file object
print 'Opened %s' % (daShapefile)
layer = dataSource.GetLayer() #getting our layer from the file

#This gets the feature geometry from the layer, we can use this to compare
inun = layer.GetFeature(0)
geometry = inun.GetGeometryRef()

#Get the spatial ref, we're gonna feed this to our points.
ref = geometry.GetSpatialReference()
# --- Main Logic ---
#For each item in addresses:

T = 0 #Number of Matches
F = 0 #Number outside of boundaries
after = []
for row in addresses:
    
    coords = [row[2],row[3]] #Extract coordinates
    
    #instantiate each as an OGR point object
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(float(coords[0]), float(coords[1]))
    #Give each point the proper reference system (WGS84)
    point.AssignSpatialReference(ref) 
    result = point.Within(geometry) #Check if containment exists
#These are just helpful as counters    
    #if yes: set value of "inundation" to 1; if no set to 0 in a list constructor
    if result == True:
        T+=1
        after.append([row[0], row[1], row[2], row[3], 1])
    else:
        F+=1
        after.append([row[0], row[1], row[2], row[3], 0])
    print "{0} True; {1} False".format(T, F)

# run the saving logic
with open("entity_inundation.csv", 'wb') as writer:
    
    written = csv.writer(writer)
    written.writerow([
                     "id",
                     "address",
                     "longitude",
                     "latitude",
                     "inundation"
                     ])
    for i in xrange(len(after)-1):
        written.writerow([
                         after[i][0],
                         after[i][1],
                         after[i][2],
                         after[i][3],
                         after[i][4]
                         ])
    
# ----- the list is for saving the output

# loop to next line in file and repeat above


# --- Saving logic ---
#parse list into schema parts (names, lat, long, quals, etc...)
#use execute() to add line to tables
#finally, after the main logic is over (no more rows to read) commit the 
#-- changes to the database, which should be ~9000 entities for our case




