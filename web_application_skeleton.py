import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)

app = Dash(__name__)

# TODO
# -- Import and clean data (importing csv into pandas)
df = pd.read_csv("global_dataframe.csv")
# df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
# df.reset_index(inplace=True)


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Sediment Analyst", style={'text-align': 'center'}),

    # upload files/ to create a drag and upload box
    dcc.Upload(
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
            'margin': '10px'},
        multiple=True # allow multiple files to be uploaded from the suer
        ),

    # TODO: isolate time components and implement time slider
    dcc.RangeSlider(
        min=0,
        max=10,
        step=None,
        marks={ # here should come a method/function for creating the dictionary
            0: '0°F',
            3: '3°F',
            5: '5°F',
            7.65: '7.65°F',
            10: '10°F'
        },
        value=[3, 7.65]
    ),

    # TODO: isolate samples
    # dcc.Dropdown(id="slct_timeobjct",
    #              options=[
    #                  {"label": "", "value": 2015}, # here we need to filter samples according to the time component (see above)
    #                  {"label": "2016", "value": 2016},
    #                  {"label": "2017", "value": 2017},
    #                  {"label": "2018", "value": 2018}],
    #              multi=False,
    #              value=None,
    #              style={'width': "40%"}
    #              ),

    html.Div(id='output_container', children=[]),
    html.Br(),  # break between the last item and the next

    dcc.Graph(id='cum_gsd', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='cum_gsd', component_property='figure')],
    [Input(component_id='slct_timeobjct', component_property='value'),
     Input(component_id='upload-data', component_property='')]
)
def update_graph(slct_timeobjct, slct_sample):
    container = "The time chosen by user was: {}".format(slct_timeobjct)
    dff = df.copy()  # always a good idea to copy the dataframe to ensure
    dff = dff[dff["Time Option"] == slct_timeobjct]
    # dff = dff[dff["Sample"] == slct_sample]

    # Plotly Express
    fig = px.scatter_mapbox(dff,
                            hover_name='Sample name',
                            hover_data=['d50', 'dm'], # for example
                            lat='lat',
                            lon='lon',
                            zoom=3,
                            height=300,
                            color_discrete_sequence=['green'])

    fig.update_layout(mapbox_style='open-street-maps')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
