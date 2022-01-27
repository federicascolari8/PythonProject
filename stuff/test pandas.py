import plotly.express as px
# import fiona
# import geopandas as gpd
import pandas as pd
from pyproj import Proj, transform, CRS

mercartor = CRS.from_string('epsg:3857')  # mercator
utm = CRS.from_string('epsg:25832')  # UTM 32
gauss = CRS.from_string('epsg:5834')  # Gauss

# UTM32
latu = 5348344.1937498
lonu = 761896.1022197

# Gauss-Kruger
latg = 5344158.38566
long = 4539265.74577

#mercartor
latm = 6145885.6
lonm = 1394515.6

# WBS84 -- degrees
latwbs = 48.234181979
lonwbs = 12.527199145

print("form UTM to mercartor")
print(transform(utm, mercartor, lonu, latu))
print((lonm,latm))
print("from mercartor back to UTM")
print(transform(mercartor,utm, lonm, latm))
print((lonu,latu))
print("-------------------------------------------------")
print("form gauss to mercartor")
print(transform(gauss, mercartor, long, latg))
print((lonm,latm))
print("from mercartor back to gauss")
print(transform(mercartor,gauss, lonm, latm))
print((long,latg))
print("-------------------------------------------------")