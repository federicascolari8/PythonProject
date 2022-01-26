import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

df = px.data.iris()
all_dims = ['sepal_length', 'sepal_width',
            'petal_length', 'petal_width']

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id="dropdown",
        options=[{"label": x, "value": x}
                 for x in all_dims],
        value=all_dims[:2],
        multi=True
    ),
    dcc.Graph(id="splom"),
])

@app.callback(
    Output("splom", "figure"),
    [Input("dropdown", "value")])
def update_bar_chart(dims):
    fig = px.scatter_matrix(
        df, dimensions=dims, color="species")
    return fig

app.run_server(debug=True)