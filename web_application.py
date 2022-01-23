import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import openpyxl
from statistical_analyzer import *
from utils import *

import pandas as pd
from config import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([  # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    html.H1("Sediment Analyst", style={'text-align': 'center'}),  # header
    dcc.Textarea(  # Web description
        id='text-intro',
        value='A web application for interactive sedimentological analyses',
        style={'width': '100%', 'height': 100}
                ),
    dcc.Upload(  # drop and drag upload area for inputing files
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
                ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
            },
        multiple=True  # Allow multiple files to be uploaded
    ),
    # html.Div(id='output-div'),
    html.Div(id='output-messages')
])


def parse_contents(contents, filename, date):
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

        metadata = [samplename, sampledate, (lat, long)]

        # Rename and standardize the Grain Size dataframe
        dff_gs.rename(columns={dff_gs.columns[0]: "Grain Sizes [mm]", dff_gs.columns[1]: "Fraction Mass [g]"},
                      inplace=True)

        analyzer = StatisticalAnalyzer(sieving_df=dff_gs, metadata=metadata)

    except Exception as e:
        print(e)
        return html.Div([filename,
                         ': There was an error processing the file. Ensure that your file does not contain too many columns (< 15).'
                         ])

    return analyzer, html.Div([filename, ': File successfully read'])
    # html.H5(filename),
    # html.H6(datetime.datetime.fromtimestamp(date)),
    # html.P("Inset X axis data"),
    # dcc.Dropdown(id='xaxis-data',
    #              options=[{'label':x, 'value':x} for x in df.columns]),
    # html.P("Inset Y axis data"),
    # dcc.Dropdown(id='yaxis-data',
    #              options=[{'label':x, 'value':x} for x in df.columns]),
    # html.Button(id="submit-button", children="Create Graph"),
    # html.Hr(),  # horizontal line

    # Print grains izes and class weights
    # dash_table.DataTable(
    #     data=dff_gs.to_dict('records'),
    #     columns=[{'name': i, 'id': i} for i in dff_gs.columns],
    #     page_size=30
    # ),
    # dcc.Store(id='stored-data', data=dff_gs.to_dict('records')),

    # For debugging, display the raw contents provided by the web browser
    # html.Div('Raw Content'),
    # html.Pre(contents[0:200] + '...', style={
    #     'whiteSpace': 'pre-wrap',
    #     'wordBreak': 'break-all'
    # })


# callback function for the Upload box
@app.callback(Output('output-messages', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        df_global = pd.DataFrame()
        children = []
        analyzers = []

        # iterating through files and appending reading messages as well as
        # analysis objects (analyzers)
        for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
            from_parsing = parse_contents(c, n, d)
            children.append(from_parsing[1])
            analyzers.append(from_parsing[0])
        # append all information from the list of analyzers into a global df
        for inter_analyzer in analyzers:
            df_global = append_global(obj=inter_analyzer,
                                      df=df_global
                                      )
        # return children
        children.append(html.Div(
            [dcc.Store(id='stored-data', data=df_global.to_dict('records')),
             html.Button("Download Summary Statistics", id="btn_download"),
             dcc.Download(id="download-dataframe-csv")
             ]
        ))
        return children


@app.callback(
    Output("download-dataframe-csv", "data"),
    State('stored-data', 'data'),
    Input("btn_download", "n_clicks"),
    prevent_initial_call=True,
)
def func(data, n_clicks):
    dataframe_global = pd.DataFrame(data)
    return dcc.send_data_frame(dataframe_global.to_csv, "overall_statistics.csv")


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
