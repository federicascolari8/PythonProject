import plotly.express as px
# import fiona
# import geopandas as gpd
import pandas as pd
from pyproj import Proj, transform, CRS


def convert_to_mercator(df, inProj):
    # output projection
    outProj = CRS.from_string('epsg:3857')  # mercator

    iter = 0
    for x1, y1 in df[["lat", "lon"]].itertuples(index=False):
        x2, y2 = transform(inProj, outProj, x1, y1)

        # solution with out correction
        df.at[iter, "lat"] = y2
        df.at[iter, "lon"] = x2

        iter = +1

    return df, outProj


def test_projections(df, key):
    if key == "utm":
        # # UTM32
        df.at[0, "lat"] = 5348344.1937498
        df.at[0, "lon"] = 761896.1022197
        df.at[1, "lat"] = 5348320.1937498
        df.at[1, "lon"] = 761890.1022197
    else:
        # Gauss-Kruger
        df.at[0, "lat"] = 5344158.38566
        df.at[0, "lon"] = 4539265.74577
        df.at[1, "lat"] = 5344140.38566
        df.at[1, "lon"] = 4539230.74577

    print("original coordinates overwriten into new projection")
    print(df[["lat", "lon"]])
    print("---------------------------------")

    return df


def convert_coordinates(df, inProj):
    # output projection
    outProj = CRS.from_string('epsg:4326')  # WGS 83 degrees

    iter = 0
    for y1, x1 in df[["lat", "lon"]].itertuples(index=False):
        x2, y2 = transform(inProj, outProj, x1, y1)
        print(x2, y2)

        # solution with out correction
        df.at[iter, "lat"] = x2
        df.at[iter, "lon"] = y2

        iter = +1
    return df


# input projection

# inProj = CRS.from_string('epsg:3857')  # Pseudo mercator
# inProj = CRS.from_string('epsg:25832')  # UTM 32
inProj = CRS.from_string('epsg:5834')  # Gauss
# inProj = Proj('epsg:25832') # any other projection (solution without correciton)

# import and organize
df = pd.read_excel("C:\\Users\\beatr\\PythonProject\\plot\\global_dataframe.xlsx", engine="openpyxl")
geo_df = df.filter(items=df.columns[1:len(df.columns)].to_list())
print("original coordinates in mercator from excel")
print(geo_df[["lat", "lon"]], "\n")

# convert points to a different projection (avoid messing with excel)
geo_df = test_projections(df=geo_df, key="")

# # convert back to mercator to fix the bug of street maps
# geo_df, inProj = convert_to_mercator(df=geo_df, inProj=inProj)
# print("coordinates conveted back to mercator")
# print(geo_df[["lat", "lon"]], "\n")

# convert mercator to degree
print("original coordinates epsg:4326")
geo_df = convert_coordinates(df=geo_df, inProj=inProj)

# force correction to the small shift
print("\n", "corrected coordinates epsg:4326")
print(geo_df[["lat", "lon"]])

# plot into the browser
fig = px.scatter_mapbox(geo_df,
                        lat=geo_df["lat"],
                        lon=geo_df["lon"],
                        hover_name="sample name",
                        hover_data=geo_df.columns[4:33],
                        zoom=11)
fig.update_layout(
    mapbox_style="open-street-map",
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
