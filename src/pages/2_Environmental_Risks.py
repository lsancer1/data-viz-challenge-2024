#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 15:46:31 2024

@author: alonso-pinar_a, lucas-sancere
"""

# part 1 imports

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

# part 2 imports

import json
from utils.json_manager import extract_rescoordinates

# part 3 imports

from io import StringIO

from meteofrance_api import MeteoFranceClient
from meteofrance_api.helpers import readeable_phenomenoms_dict
from meteofrance_api import client

from hacf_model import CurrentPhenomenons
from hacf_model import Forecast
from hacf_model import Full
from hacf_model import Observation
from hacf_model import PictureOfTheDay
from hacf_model import Place
from hacf_model import Rain
from hacf_model import WarningDictionary
import constants
import csv 
import requests
import time



#############################################################
## Load configs parameter
#############################################################

currently = 'cloud'

if currently == 'cloud':

    folder_path = os.getcwd()
    pathtofolder = os.path.join(folder_path, 'data/edf_corse/reseaux/')
    pathtoconfig = os.path.join(folder_path, 'configs/')
    
    with open( pathtoconfig + "main_lucas.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    config = attributedict(config)
    keptfiles = list(config.dashboard.data.reseaux.keptfiles)

    
else:
    folder_path = os.getcwd()
    with open("../configs/main_lucas.yml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    config = attributedict(config)
    pathtofolder = config.dashboard.data.reseaux.folder
    keptfiles = list(config.dashboard.data.reseaux.keptfiles)


#############################################################
## Token related
#############################################################


APPLICATION_ID = st.secrets['ID_Sancere_2024_09_25']
TOKEN_URL = st.secrets['MF_TOKEN_URL']



#############################################################
## Translations
#############################################################

# Language translations
translations = {
    'en': {
        'tab1name': "Risk on overhead electricity network (poles)",
        'title1': "Environmental risks on the overhead electricity network",
        'tab1options': "Options",


    },
    'fr': {
        'tab1name': "Risques sur le réseau electrique aérien",
        'title1': "Risques environementaux sur le réseau electrique aérien",
        'tab1options': "Options",

    }
}

# Language selection
language = st.sidebar.selectbox('Select language:', ['Français', 'English'])
if language == 'Français':
    lang_code = 'fr'
    tab1,  = st.tabs(["Risques sur le réseau electrique aérien"] )
else:
    lang_code = 'en'
    tab1,  = st.tabs(["Risk on overhead electricity network (poles)"])



#############################################################
## Load files
#############################################################

ext = '.geojson'

bt_aerien_path = pathtofolder + keptfiles[0] + ext
hta_aerien_path = pathtofolder + keptfiles[1] + ext 
htb_aerien_path = pathtofolder + keptfiles[2] + ext
pylones_path = pathtofolder + keptfiles[3] + ext


# with open(bt_aerien_path) as f:
#     geojson_bt_aerien = json.load(f)

# with open(hta_aerien_path) as f:
#     geojson_hta_aerien = json.load(f)

# with open(htb_aerien_path) as f:
#     geojson_htb_aerien = json.load(f)

# with open(pylones_path) as f:
#     geojson_pylones = json.load(f)


@st.cache_data
def load_data():

	with open(bt_aerien_path) as f:
		geojson_bt_aerien = json.load(f)
	with open(hta_aerien_path) as f:
		geojson_hta_aerien = json.load(f)
	with open(htb_aerien_path) as f:
		geojson_htb_aerien = json.load(f)
	with open(pylones_path) as f:
		geojson_pylones = json.load(f)

	return geojson_bt_aerien, geojson_hta_aerien, geojson_htb_aerien, geojson_pylones

geojson_bt_aerien, geojson_hta_aerien, geojson_htb_aerien, geojson_pylones = load_data()


bt_aerien_coord = extract_rescoordinates(geojson_bt_aerien)
hta_aerien_coord = extract_rescoordinates(geojson_hta_aerien)
htb_aerien_coord = extract_rescoordinates(geojson_htb_aerien)
pylones_coord = extract_rescoordinates(geojson_pylones)



#############################################################
## Streamlit app
#############################################################

# Tabs
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = translations[lang_code]['tab1name']
    



#############################################################
## Functions and Classes
############################################################


class Client(object):

    def __init__(self):
        self.session = requests.Session()

    def request(self, method, url, **kwargs):
        # First request will always need to obtain a token first
        if 'Authorization' not in self.session.headers:
            self.obtain_token()
        # Optimistically attempt to dispatch reqest
        response = self.session.request(method, url, **kwargs)
        if self.token_has_expired(response):
            # We got an 'Access token expired' response => refresh token
            self.obtain_token()
            # Re-dispatch the request that previously failed
            response = self.session.request(method, url, **kwargs)

        return response


    def token_has_expired(self, response):

        status = response.status_code
        content_type = response.headers['Content-Type']
        if status == 401 and 'application/json' in content_type:
            repJson = response.text
            if 'Invalid JWT token' in repJson['description']:
                return True

        return False



    def obtain_token(self):
        # Obtain new token
        data = {'grant_type': 'client_credentials'}
        headers = {'Authorization': 'Basic ' + APPLICATION_ID}
        access_token_response = requests.post(TOKEN_URL, 
        									  data=data, 
        									  verify=False, 
        									  allow_redirects=False, 
        									  headers=headers)
        token = access_token_response.json()['access_token']
        # Update session with fresh token
        self.session.headers.update({'Authorization': 'Bearer %s' % token})



    def observations_get_stations_list(self) -> requests.Response:
        """Get the list of observation stations from the API.

        Returns:
            requests.Response: Response from the API with the data in csv.
        """
        self.session.headers.update({'Accept': 'application/json'})
        request = self.request(
            method='GET',
            url=constants.STATION_LIST_URL
        )

        return request


    def get_wms_metadata(
    	self,
    	service: str = "WMS",
    	version: str = "1.3.0",
    	language: str = "eng"
    	) -> requests.Response:

	    """
	    Returns the metadata of the WMS service 
	    (proposed layers, associated projections, author, etc.)


	    """
	    self.session.headers.update({'Accept': 'application/json'})
	    request = self.request(
	    	method='GET',
	    	url=constants.AROME_WMS_CAPABILITIES_URL,
	    	params = {
	    	"service": service, 
	    	"version": version, 
	    	"language": language}
	    	)

	    return request.text


    def get_wcs_metadata(
    	self,
    	service: str = "WCS",
    	version: str = "2.0.1",
    	language: str = "eng"
    	) -> requests.Response:

	    """
	    Returns the metadata of the WCS service 
	    (proposed layers, associated projections, author, etc.)


	    """
	    self.session.headers.update({'Accept': 'application/json'})
	    request = self.request(
	    	method='GET',
	    	url=constants.AROME_WCS_CAPABILITIES_URL,
	    	params = {
	    	"service": service, 
	    	"version": version, 
	    	"language": language}
	    	)

	    return request.text


    def get_wms_map(
		self,
		layers: str,
		bbox: str,
		height: str,
		width: str,
		service: str = "WMS",
		version: str = "1.3.0",
		crs: str = "EPSG:4326",
		format: str = "image/png",
		transparent: str = "true"
		) -> requests.Response:
	    """
	    """
	    self.session.headers.update({'Accept': 'application/json'})
	    request = self.request(
	    	method='GET',
	    	url=constants.AROME_WMS_MAP_URL,
	    	params = {
	    	"layers": layers,
	        "bbox": bbox,
	        "height": height,
	        "width": width,
	        "service": service,
	        "version": version,
	        "crs": crs,
	        "format": format,
	        "transparent": transparent,
	    	}
	    	)

	    return request 




#############################################################
## Tab1 
#############################################################


with tab1:
	st.session_state['active_tab'] = translations[lang_code]['tab1name']
	st.title(translations[lang_code]['title1'])

	st.sidebar.header(translations[lang_code]['tab1options'])

	#insert the function we will need to read the API

	######

	#############################################################
	## Function to generate static map
	#############################################################

	def generate_map_tab1(bt_aerien_coord, hta_aerien_coord, htb_aerien_coord,pylones_coord):
   	 # Step 1: Combine your data into one DataFrame

		data = []
		for point in bt_aerien_coord:
		 	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		 	'Category': 'BT aérien', 'Statut': point['statut']})
		for point in hta_aerien_coord:
		 	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		 	'Category': 'HTA aérien', 'Statut': point['statut']})
		# for point in htb_aerien_coord:
		#  	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		# 'Category': 'HTB aérien', 'Statut': point['statut']})
		for point in pylones_coord:
		 	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		 	'Category': 'Pylones', 'Statut': point['statut']})

		# Create a DataFrame
		df = pd.DataFrame(data)

		# Define your custom color map
		custom_colors = {
			'BT aérien': 'blue',   
			'HTA aérien': 'red',    
			'HTB aérien': 'orange',  
			'Pylones': 'orange'  
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

		return fig


	# Customize the colorbar
	# fig.update_layout(
	# 	mapbox_style="open-street-map",
	# 	mapbox=dict(
	#     	zoom=7,
	#     	center={"lat": 42.16, "lon": 9.13}  # Center map on the data
	# 	),
	# 	height=800,
	# 	width=800
	# 	)

	# Also an option for pylones
	# go.Scattermapbox(
	# 	lat=[point['lat'] for point in pylones_coord],
	# 	lon=[point['lon'] for point in pylones_coord],
	# 	mode='markers',
	# 	marker=go.scattermapbox.Marker(
	#     	size=10,
	#     	color='black'  # Set a different color for the second set of points
	# 	),
	# 	text=[point['statut'] for point in pylones_coord],
	# ) return fig

	#############################################################
	## Generate and Display the Map
	#############################################################

	fig = generate_map_tab1(bt_aerien_coord, hta_aerien_coord, htb_aerien_coord, pylones_coord)
	
	

	#############################################################
	## Generate and Display Forecast
	#############################################################

	# hardcoded parameters for the forecast
	corsicabbox =  [43.25, 8.15, 41.15, 10.15]
	forecastlayers = {
		"temperature": "TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
		"windspeed": "WIND_SPEED__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
		"humidity": "RELATIVE_HUMIDITY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND"
	}
	mapheight=800
	mapwidth=800

	# load client 
	client = Client()

	layermap = client.get_wms_map(		
	    layers = forecastlayers["temperature"],
		bbox = str(corsicabbox),
		height = str(mapheight),
		width = str(mapwidth)
		)


	#############################################################
	## Layout with Two Columns: Map and Legend
	#############################################################

	if fig:
		# Create two columns with a 3:1 ratio (map:legend)
		col1, col2 = st.columns([3, 1])

	with col1:
		st.plotly_chart(fig, use_container_width=True)

		# st.plotly_chart(layermap, use_container_width=True)

	with col2:
		st.header("Exploration")
		st.write(layermap)

         



