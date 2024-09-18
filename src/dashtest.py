#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 20:38:18 2024

@author: alonso-pinar_a
"""


import dash
from dash import dcc, Input, Output
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import json
import yaml 
from attrdictionary import AttrDict as attributedict

from utils.json_manager import extract_rescoordinates


#############################################################
## Load configs parameter
#############################################################

# Import parameters values from config file by generating a dict.
# The lists will be imported as tuples.
with open("./../configs/main.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
# Create a config dict from which we can access the keys with dot syntax
config = attributedict(config)
pathtofolder = config.dashboard.data.reseaux.folder
keptfiles = list(config.dashboard.data.reseaux.keptfiles) 



#############################################################
## Load files
#############################################################

ext = '.geojson'

bt_aerien_path = pathtofolder + keptfiles[0] + ext
hta_aerien_path = pathtofolder + keptfiles[1] + ext 
htb_aerien_path = pathtofolder + keptfiles[2] + ext
pylones_path = pathtofolder + keptfiles[3] + ext


with open(bt_aerien_path) as f:
    geojson_bt_aerien = json.load(f)

with open(hta_aerien_path) as f:
    geojson_hta_aerien = json.load(f)

with open(htb_aerien_path) as f:
    geojson_htb_aerien = json.load(f)

with open(pylones_path) as f:
    geojson_pylones = json.load(f)


    
#############################################################
## Dash app
#############################################################


bt_aerien_coord = extract_rescoordinates(geojson_bt_aerien)
hta_aerien_coord = extract_rescoordinates(geojson_hta_aerien)
htb_aerien_coord = extract_rescoordinates(geojson_htb_aerien)
pylones_coord = extract_rescoordinates(geojson_pylones)



# Create a Dash application
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Tabs(id="tabs-example", value='tab-1', children=[
        dcc.Tab(label='EDF', value='tab-1'),
        dcc.Tab(label='Environnement', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])

# Callback to render content based on selected tab
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-example', 'value')
)



def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H1("Risque sur le réseau electrique aérien"),
            dcc.Graph(
                id='geojson-map',
                figure={
                    'data': [
                        # First scatter layer
                        go.Scattermapbox(
                            lat=[point['lat'] for point in bt_aerien_coord],
                            lon=[point['lon'] for point in bt_aerien_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='blue'  # Set color for the first set of points
                            ),
                            text=[point['statut'] for point in bt_aerien_coord],
                            name='BT aérien'
                        ),
                        # Second scatter layer
                        go.Scattermapbox(
                            lat=[point['lat'] for point in hta_aerien_coord],
                            lon=[point['lon'] for point in hta_aerien_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='red'  # Set a different color for the second set of points
                            ),
                            text=[point['statut'] for point in hta_aerien_coord],
                            name='HTA aérien'
                        ),
                        go.Scattermapbox(
                            lat=[point['lat'] for point in htb_aerien_coord],
                            lon=[point['lon'] for point in htb_aerien_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='orange'  # Set a different color for the second set of points
                            ),
                            text=[point['statut'] for point in htb_aerien_coord],
                            name='HTB aérien'
                        ),
                        go.Scattermapbox(
                            lat=[point['lat'] for point in pylones_coord],
                            lon=[point['lon'] for point in pylones_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='black'  # Set a different color for the second set of points
                            ),
                            text=[point['statut'] for point in pylones_coord],
                            name='Pylones'
                        )
                    ],

                    'layout': go.Layout(
                        title="Réseau aérien",
                        mapbox_style="open-street-map",
                        mapbox=dict(
                            zoom=7,
                            center={"lat": 42.16, "lon": 9.13}  # Center map on the data
                        ),
                        height=800,
                        width=800
                    )
                }
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H1("Risques environnement"),
            dcc.Graph(
                id='geojson-map',
                figure={
                    'data': [
                        # First scatter layer
                        go.Scattermapbox(
                            lat=[point['lat'] for point in bt_aerien_coord],
                            lon=[point['lon'] for point in bt_aerien_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='blue'  # Set color for the first set of points
                            ),
                            text=[point['statut'] for point in bt_aerien_coord],
                            name='BT aérien'
                        ),
                        # Second scatter layer
                        go.Scattermapbox(
                            lat=[point['lat'] for point in hta_aerien_coord],
                            lon=[point['lon'] for point in hta_aerien_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='red'  # Set a different color for the second set of points
                            ),
                            text=[point['statut'] for point in hta_aerien_coord],
                            name='HTA aérien'
                        ),
                        go.Scattermapbox(
                            lat=[point['lat'] for point in htb_aerien_coord],
                            lon=[point['lon'] for point in htb_aerien_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='orange'  # Set a different color for the second set of points
                            ),
                            text=[point['statut'] for point in htb_aerien_coord],
                            name='HTB aérien'
                        ),
                        go.Scattermapbox(
                            lat=[point['lat'] for point in pylones_coord],
                            lon=[point['lon'] for point in pylones_coord],
                            mode='markers',
                            marker=go.scattermapbox.Marker(
                                size=10,
                                color='black'  # Set a different color for the second set of points
                            ),
                            text=[point['statut'] for point in pylones_coord],
                            name='Pylones'
                        )
                    ],
                    'layout': go.Layout(
                        title="Réseau aérien",
                        mapbox_style="open-street-map",
                        mapbox=dict(
                            zoom=7,
                            center={"lat": 42.16, "lon": 9.13}  # Center map on the data
                        ),
                        height=800,
                        width=800
                    )
                }
            )
        ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)