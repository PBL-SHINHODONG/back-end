from datetime import datetime

import pyproj

grs80 = pyproj.Proj(init="epsg:5174")
wgs84 = pyproj.Proj(init="epsg:4326")

def toLatLng(x, y):
    return pyproj.transform(grs80, wgs84, x, y)


def getSeason():
    month = datetime.now().month
    if month in [3, 4, 5]:
        season = 0 
    elif month in [6, 7, 8]:
        season = 1 
    elif month in [9, 10, 11]:
        season = 2 
    else:
        season = 3
    
    return season


def isWeekend():
     return 1 if datetime.now().weekday() >= 5 else 0