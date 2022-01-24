import plotly.express as px
# import fiona
# import geopandas as gpd
import pandas as pd
from pyproj import Proj, transform


def convert_coordinates(df):
    # import projections
    inProj = Proj('epsg:3857')  # Pseudo mercator
    # inProj = Proj('epsg:25832') # any other projection (solution without correciton)
    outProj = Proj('epsg:4326')  # WGS 83 degrees

    iter = 0
    for x1, y1 in df[["lat", "lon"]].itertuples(index=False):
        x2, y2 = transform(inProj, outProj, x1, y1)
        print(x2, y2)

        # correction from epsg 3857
        df.at[iter, "lat"] = y2 - 6.9752575
        df.at[iter, "lon"] = x2 + 0.098607

        # # solution with out correction
        # df.at[iter, "lat"] = y2
        # df.at[iter, "lon"] = x2

        iter = +1
    return df


df = pd.read_excel("plot/global_dataframe.xlsx", engine="openpyxl")

geo_df = df.filter(items=df.columns[1:len(df.columns)].to_list())

geo_df = convert_coordinates(df=geo_df)

print(geo_df[["lat", "lon"]])

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
#
# print()

## cool example
# us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
#
#
# fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", hover_name="City", hover_data=["State", "Population"],
#                         color_discrete_sequence=["fuchsia"], zoom=3, height=300)
# fig.update_layout(mapbox_style="open-street-map")
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()
