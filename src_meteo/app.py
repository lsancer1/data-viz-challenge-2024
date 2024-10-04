import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from src.data_loader import load_csv
from src.data_cleaner import clean_data
from src.data_visualizer import create_plot  # Example plot function from data_visualizer

# Load and preprocess data
data_csv = clean_data(load_csv('data/data_source_1.csv'))

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Data Visualization Dashboard"),
    dcc.Graph(id='data-plot'),

    dcc.Dropdown(
        id='dropdown',
        options=[{'label': col, 'value': col} for col in data_csv.columns],
        value=data_csv.columns[0]
    )
])

# Callback for updating the plot based on dropdown selection
@app.callback(
    Output('data-plot', 'figure'),
    [Input('dropdown', 'value')]
)
def update_plot(selected_column):
    fig = create_plot(data_csv, selected_column)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)

