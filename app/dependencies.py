import pyproj

grs80 = pyproj.Proj("epsg:5174")
wgs84 = pyproj.Proj("epsg:4326")

def toLatLng(x, y):
    return pyproj.transform(grs80, wgs84, x, y)
