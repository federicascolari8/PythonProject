import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, Input, Output, State, html
import plotly.express as px
import openpyxl
from statistical_analyzer import *
from utils import *

import pandas as pd
from config import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)
style_upload = {
    'width': '100%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': '10px'
}

app.layout = html.Div([  # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    html.H1("Sediment Analyst", style={'text-align': 'center'}),  # header
    dcc.Textarea(  # Web description
        id='text-intro',
        value='A web application for interactive sedimentological analyses',
        style={'width': '100%', 'height': 100}
    ),
    html.Br(),

    # manual inputs
    dcc.Input(id="header", type="number", placeholder="table's header"),
    dcc.Input(id="gs_clm", type="number", placeholder="grain sizes table column number (start from zero)"),
    dcc.Input(id="cw_clm", type="number", placeholder="class weight column number (start from zero)"),
    dcc.Input(id="n_rows", type="number", placeholder="class weight column number (start from zero)"),
    dcc.Input(id="porosity", type="number", placeholder="porosity index"),
    dcc.Input(id="SF_porosity", type="number", placeholder="SF_porosity index"),
    dcc.Input(id="index_lat", type="number", placeholder="latitute index"),
    dcc.Input(id="index_long", type="number", placeholder="longitude index"),
    dcc.Input(id="index_sample_name", type="number", placeholder="sample name index"),
    dcc.Input(id="sample_date", type="number", placeholder="sample date index"),
    dcc.Input(id="projection", type="text", placeholder="projection ex: epsg:3857"),
    html.Button("run", id="btn_run"),
    dcc.Store(id="store_manual_inputs"),

    # map
    dcc.Graph(id="map"),

    # files upload
    dcc.Upload(  # drop and drag upload area for inputing files
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style=style_upload,
        multiple=True  # Allow multiple files to be uploaded
    ),

    # html.Div(id='output-div'),
    html.Div(id='output-messages'),

])


def parse_contents(contents, filename, date, input):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), engine="openpyxl", header=None)

        # clean dataset
        dff = df.copy()
        columns_to_get = [input["gs_clm"], input["cw_clm"]]
        dff_gs = dff.iloc[input["header"]: input["header"] + input["n_rows"], columns_to_get]
        dff_gs.reset_index(inplace=True, drop=True)
        dff_gs = dff_gs.astype(float)

        # Get metadata from the dataframe
        # get sample name
        try:
            samplename = dff.iat[input["index_sample_name"][0], input["index_sample_name"][1]]
        except:
            samplename = None
            pass

        # get sample date
        try:
            sampledate = dff.iat[input["index_sample_date"][0], input["index_sample_date"][1]]
        except:
            sampledate = None
            pass

        # get sample coordinates
        try:
            lat = dff.iat[input["index_lat"][0], input["index_lat"][1]]
            long = dff.iat[input["index_long"][0], input["index_long"][1]]
        except:
            lat, long = None, None
            pass

        # get porosity
        try:
            porosity = dff.iat[input["porosity"][0], input["porosity"][1]]
        except Exception as e:
            porosity = None
            print(e)
            pass

        # get sf_porosity
        try:
            sf_porosity = dff.iat[input["SF_porosity"][0], input["SF_porosity"][1]]
        except Exception as e:
            sf_porosity = 6.1  # default for rounded sediments
            print(e)
            pass

        metadata = [samplename, sampledate, (lat, long), porosity, sf_porosity]

        # Rename and standardize the Grain Size dataframe
        dff_gs.rename(columns={dff_gs.columns[0]: "Grain Sizes [mm]", dff_gs.columns[1]: "Fraction Mass [g]"},
                      inplace=True)

        analyzer = StatisticalAnalyzer(input=input, sieving_df=dff_gs, metadata=metadata)

    except Exception as e:
        print(e)
        return html.Div([filename,
                         ': There was an error processing the file. Ensure that your file does not contain too many columns (< 15).'
                         ])

    return analyzer, html.Div([filename, ': File successfully read'])


# callback function for the Upload box
@app.callback(Output('output-messages', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              Input("store_manual_inputs", 'data'))
def update_output(list_of_contents, list_of_names, list_of_dates, input):
    if list_of_contents is not None:
        df_global = pd.DataFrame()
        children = []
        analyzers = []

        # iterating through files and appending reading messages as well as
        # analysis objects (analyzers)
        for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
            from_parsing = parse_contents(c, n, d, input)
            children.append(from_parsing[1])
            analyzers.append(from_parsing[0])
        # append all information from the list of analyzers into a global df
        for inter_analyzer in analyzers:
            df_global = append_global(obj=inter_analyzer,
                                      df=df_global
                                      )
        # return children
        data2 = df_global.to_dict("split")
        children.append(html.Div([
            dcc.Store(id='stored-data', data=data2),
            html.Button("Download Summary Statistics", id="btn_download"),
            dcc.Download(id="download-dataframe-csv"),
        ])
        )

        return children


@app.callback(
    Output("download-dataframe-csv", "data"),
    State('stored-data', 'data'),
    Input("btn_download", "n_clicks"),
    prevent_initial_call=True,
)
def func(data, n_clicks):
    dataframe_global = pd.DataFrame(data=data["data"], columns=data["columns"])
    return dcc.send_data_frame(dataframe_global.to_csv, "overall_statistics.csv")


@app.callback(
    Output('map', 'figure'),
    Input('stored-data', 'data'))
def update_figure(data):
    df = pd.DataFrame(data=data["data"], columns=data["columns"])
    fig = create_map(df)
    fig.update_layout(transition_duration=500)

    return fig


@app.callback(
    Output("store_manual_inputs", "data"),
    State('header', 'value'),
    State('gs_clm', 'value'),
    State('cw_clm', 'value'),
    State('n_rows', 'value'),
    State('porosity', 'value'),
    State('SF_porosity', 'value'),
    State('index_lat', 'value'),
    State('index_long', 'value'),
    State('index_sample_name', 'value'),
    State('sample_date', 'value'),
    State('projection', 'value'),
    Input("btn_run", "n_clicks"),
)
def save_inputs(header, gs_clm, cw_clm, n_rows, porosity,
                sf_porosity, index_lat, index_lon,
                sample_name_index, sample_date_index,
                projection, clicks):
    # transform float values into list
    porosity_index = list(map(int, str(porosity).split("."))) if porosity is not None else None
    sf_porosity_index = list(map(int, str(sf_porosity).split("."))) if sf_porosity is not None else None
    lat_index = list(map(int, str(index_lat).split("."))) if index_lat is not None else None
    lon_index = list(map(int, str(index_lon).split("."))) if index_lon is not None else None
    name_index = list(map(int, str(sample_name_index).split("."))) if sample_name_index is not None else None
    date_index = list(map(int, str(sample_date_index).split("."))) if sample_date_index is not None else None

    # create dictionary with all inputs
    input = dict(header=header, gs_clm=gs_clm, cw_clm=cw_clm, n_rows=n_rows, porosity=porosity_index,
                 SF_porosity=sf_porosity_index, index_lat=lat_index, index_long=lon_index,
                 index_sample_name=name_index, index_sample_date=date_index, projection=projection)
    return input


# @app.callback(Output('output-div', 'children'),
#               Input('submit-button', 'n_clicks'),
#               State('stored-data', 'data'),
#               State('xaxis-data', 'value'),
#               State('yaxis-data', 'value'))
# def make_graphs(n, data, x_data, y_data):
#     if n is None:
#         return dash.no_update
#     else:
#         bar_fig = px.bar(data, x=x_data, y=y_data)
#         # print(data)
#         return dcc.Graph(figure=bar_fig)


if __name__ == '__main__':
    app.run_server(debug=True)
