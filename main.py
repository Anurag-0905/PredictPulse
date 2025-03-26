import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import webview
import time
from threading import Thread
import base64
import io

uploaded_data = None

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "PredictPulse: Data Visualization"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("PredictPulse: Upload and Visualize Data", className="text-center text-light mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(["Drag and Drop or ", html.A("Select a File")]),
                        style={
                            "width": "100%", "height": "60px", "lineHeight": "60px",
                            "borderWidth": "1px", "borderStyle": "dashed",
                            "borderRadius": "5px", "textAlign": "center", "margin": "10px"
                        },
                        multiple=False
                    )
                ),
                className="mb-4"
            ),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Label("X-axis Column:", className="text-light"),
                    dcc.Dropdown(id="x-axis-dropdown", placeholder="Select X-axis column", style={"color": "black"}),
                    html.Br(),
                    html.Label("Y-axis Column:", className="text-light"),
                    dcc.Dropdown(id="y-axis-dropdown", placeholder="Select Y-axis column", style={"color": "black"})
                ]),
                className="mb-4"
            ),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("Visualize Data", id="visualize-button", color="success", className="mt-4 w-100"), width=12)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(dcc.Graph(id="scatter-graph", config={"displayModeBar": True}))
            , className="mb-4"),
            width=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(dcc.Graph(id="histogram-graph", config={"displayModeBar": True}))
            , className="mb-4"),
            width=6
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(dcc.Graph(id="boxplot-graph", config={"displayModeBar": True}))
            , className="mb-4"),
            width=12
        )
    ])
], fluid=True)

@app.callback(
    [Output("x-axis-dropdown", "options"),
     Output("y-axis-dropdown", "options"),
     Output("x-axis-dropdown", "value"),
     Output("y-axis-dropdown", "value")],
    Input("upload-data", "contents"),
    State("upload-data", "filename")
)
def update_dropdowns(contents, filename):
    global uploaded_data
    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            uploaded_data = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        except Exception as e:
            print(e)
            return [], [], None, None
        options = [{"label": col, "value": col} for col in uploaded_data.columns]
        return options, options, None, None
    return [], [], None, None

@app.callback(
    [Output("scatter-graph", "figure"),
     Output("histogram-graph", "figure"),
     Output("boxplot-graph", "figure")],
    Input("visualize-button", "n_clicks"),
    State("x-axis-dropdown", "value"),
    State("y-axis-dropdown", "value")
)
def generate_graphs(n_clicks, x_col, y_col):
    if n_clicks and uploaded_data is not None:
        # Scatter plot figure (requires both X and Y)
        if x_col and y_col:
            scatter_fig = px.scatter(uploaded_data, x=x_col, y=y_col, title="Scatter Plot")
            scatter_fig.update_layout(template="plotly_dark")
        else:
            scatter_fig = px.scatter(title="Select both X and Y columns for scatter plot")
            scatter_fig.update_layout(template="plotly_dark")
        # Histogram figure (requires X)
        if x_col:
            histogram_fig = px.histogram(uploaded_data, x=x_col, title="Histogram")
            histogram_fig.update_layout(template="plotly_dark")
        else:
            histogram_fig = px.histogram(title="Select X column for histogram")
            histogram_fig.update_layout(template="plotly_dark")
        # Box plot figure: if both X and Y selected, group box plot by X; otherwise, plot distribution of Y or X
        if x_col and y_col:
            boxplot_fig = px.box(uploaded_data, x=x_col, y=y_col, title="Box Plot")
            boxplot_fig.update_layout(template="plotly_dark")
        elif y_col:
            boxplot_fig = px.box(uploaded_data, y=y_col, title="Box Plot of Y")
            boxplot_fig.update_layout(template="plotly_dark")
        elif x_col:
            boxplot_fig = px.box(uploaded_data, y=x_col, title="Box Plot of X")
            boxplot_fig.update_layout(template="plotly_dark")
        else:
            boxplot_fig = px.box(title="Select at least one column for box plot")
            boxplot_fig.update_layout(template="plotly_dark")
        return scatter_fig, histogram_fig, boxplot_fig
    empty_fig = px.scatter(title="Upload a file to visualize data")
    empty_fig.update_layout(template="plotly_dark")
    return empty_fig, empty_fig, empty_fig

def run_dash():
    app.run(debug=False, use_reloader=False)

if __name__ == "__main__":
    dash_thread = Thread(target=run_dash)
    dash_thread.daemon = True
    dash_thread.start()
    time.sleep(2)
    window = webview.create_window("PredictPulse", "http://127.0.0.1:8050")
    webview.start()
