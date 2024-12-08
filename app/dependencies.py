from datetime import datetime

import pyproj
from sqlalchemy.sql import func

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


def getCategoryCode(category):
    category_mapping = {
        "한식": [210],
        "일식": [220],
        "중식": [230],
        "양식": [240],
        "아시아식": [250],
        "주점": [260],
        "미분류": [270],
        "카페": [201, 202],
        "명소": list(range(101, 110)) + list(range(401, 408)),
    }
    return category_mapping.get(category, [])


def getHaversine(lat1, lon1, lat2, lon2):
    R = 6371.0 

    lat1_rad = func.radians(lat1)
    lon1_rad = func.radians(lon1)
    lat2_rad = func.radians(lat2)
    lon2_rad = func.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = func.pow(func.sin(dlat / 2), 2) + func.cos(lat1_rad) * func.cos(lat2_rad) * func.pow(func.sin(dlon / 2), 2)
    c = 2 * func.atan2(func.sqrt(a), func.sqrt(1 - a))

    distance = R * c
    return distance
