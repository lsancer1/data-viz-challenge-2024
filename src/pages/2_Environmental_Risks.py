#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 15:46:31 2024

@author: alonso-pinar_a, lucas-sancere
"""

import streamlit as st
import plotly.express as px
import xarray as xr
import pandas as pd
import calendar
import numpy as np
import yaml
from attrdictionary import AttrDict as attributedict
import os
import zipfile
from datetime import datetime, timedelta
import cdsapi

import json
from utils.json_manager import extract_rescoordinates


#############################################################
## Load configs parameter
#############################################################

currently = 'cloud'

if currently == 'cloud':

    folder_path = os.getcwd()
    pathtofolder = os.path.join(folder_path, 'data/reseaux/')
    pathtoconfig = os.path.join(folder_path, 'configs/')
    
    with open( pathtoconfig + "main_lucas.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    config = attributedict(config)
    keptfiles = list(config.dashboard.data.cams.keptfiles)

    
else:
    folder_path = os.getcwd()
    with open("../configs/main_alberto.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    config = attributedict(config)
    pathtofolder = config.dashboard.data.cams.folder
    keptfiles = list(config.dashboard.data.cams.keptfiles)



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


bt_aerien_coord = extract_rescoordinates(geojson_bt_aerien)
hta_aerien_coord = extract_rescoordinates(geojson_hta_aerien)
htb_aerien_coord = extract_rescoordinates(geojson_htb_aerien)
pylones_coord = extract_rescoordinates(geojson_pylones)




#############################################################
## Streamlit app
#############################################################


# Language translations
translations = {
    'en': {
        # 'tab1name': "Environmental risks on the overhead electricity network",
        'title1': "Environmental risks on the overhead electricity network",
        'tab1options': "Options",


    },
    'fr': {
        # 'tab1name': "Risques environementaux sur le réseau electrique aérien",
        'title1': "Risques environementaux sur le réseau electrique aérien",
        'tab1options': "Options",

    }
}

# Language selection
language = st.sidebar.selectbox('Select language:', ['Français', 'English'])
if language == 'Français':
    lang_code = 'fr'
    tab1 = st.tabs(["Risques sur le réseau electrique aérien"])
else:
    lang_code = 'en'
    tab1  = st.tabs(["Risk on overhead electricity network (poles)"])

# # Tabs
# if 'active_tab' not in st.session_state:
#     st.session_state['active_tab'] = translations[lang_code]['tab1name']
    

#############################################################
## Tab1 
#############################################################


with tab1:
    st.session_state['active_tab'] = translations[lang_code]['tab1name']
    st.title(translations[lang_code]['title1'])

    st.sidebar.header(translations[lang_code]['tab1options'])

    #insert the function we will need to read the API

    ######
    ######
    ######

    #############################################################
    ## Function to generate static map
    #############################################################

    def generate_map_tab1(bt_aerien_coord, hta_aerien_coord, htb_aerien_coord,pylones_coord):

    	"""
		Generate corsica map with aerial network displayed


		"""
		# Step 1: Combine your data into one DataFrame
		data = []
		
		for point in bt_aerien_coord:
			data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 'Category': 'BT aérien', 'Statut': point['statut']})
		for point in hta_aerien_coord:
			data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 'Category': 'HTA aérien', 'Statut': point['statut']})
		for point in htb_aerien_coord:
			 data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 'Category': 'HTB aérien', 'Statut': point['statut']})
		for point in pylones_coord:
			 data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 'Category': 'Pylones', 'Statut': point['statut']})


			# Create a DataFrame
		df = pd.DataFrame(data)

		# Define your custom color map
		custom_colors = {
		    'BT aérien': 'blue',   
		    'HTA aérien': 'red',    
		    'HTB aérien': 'orange',  
		    'Pylones': 'black'  
		}

		# plot
		fig = px.scatter_mapbox(
		    df,
		    lat='Latitude',
		    lon='Longitude',
		    color='Category',  # Differentiate points by 'Category'
		    hover_name='Statut',  # Display 'Statut' on hover
		    mapbox_style='open-street-map',
		    zoom=7,
		    center={"lat": 42.16, "lon": 9.13},
		    title="Aerial Points Map",
		    height=800,
		    width=800,
		    color_discrete_map=custom_colors  # Apply custom color map
		)

		# Customize the colorbar
		# fig.update_layout(
		#     mapbox_style="open-street-map",
		#     mapbox=dict(
		#         zoom=7,
		#         center={"lat": 42.16, "lon": 9.13}  # Center map on the data
		#     ),
		#     height=800,
		#     width=800
		#     )

		# Also an option for pylones
		# go.Scattermapbox(
		#     lat=[point['lat'] for point in pylones_coord],
		#     lon=[point['lon'] for point in pylones_coord],
		#     mode='markers',
		#     marker=go.scattermapbox.Marker(
		#         size=10,
		#         color='black'  # Set a different color for the second set of points
		#     ),
		#     text=[point['statut'] for point in pylones_coord],
		#     name='Pylones'
		# )

		return fig        


	#############################################################
	## Generate and Display the Map
	#############################################################


	fig = generate_map_tab1(
		bt_aerien_coord, 
		hta_aerien_coord, 
		htb_aerien_coord,
		pylones_coord
		)



	#############################################################
	## Layout with Two Columns: Map and Legend
	#############################################################

	if fig:
	# Create two columns with a 3:1 ratio (map:legend)
	col1, col2 = st.columns([3, 1])

	with col1:
	    st.plotly_chart(fig, use_container_width=True)

	with col2:
		# Do nothing for now 

         



