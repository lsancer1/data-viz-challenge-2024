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


# part 4 imports

from PIL import Image, ImageChops
from io import BytesIO
import plotly.io as pio





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

	# Step 1: Save Plotly figure as an image
	fig.write_image("plotly_fig.png", format='png')  # Save plotly figure to disk


	
	

	#############################################################
	## Generate and Display Forecast
	#############################################################

	# hardcoded parameters for the forecast
	example_bbox = "37.5,-12,55.4,16"
	example_mapheight=300
	example_mapwidth=300


	corsica_bbox_ori =  "43.25,8.15,41.15,10.15"

	miny_corsica="41.3" 
	minx_corsica="7.9" 
	maxy_corsica="42.9"
	maxx_corsica="10.2" 

	corsica_bbox_arome = miny_corsica+","+minx_corsica+","+maxy_corsica+","+maxx_corsica 
	print("corsica_bbox_arome",corsica_bbox_arome)

	globalminy=float(miny_corsica)
	globalminx=float(minx_corsica)
	globalmaxy=float(maxy_corsica)
	globalmaxx=float(maxx_corsica)

	global_bbox_arome = str(globalminy)+","+str(globalminx)+","+str(globalmaxy)+","+str(globalmaxx)
	print("global_bbox_arome",global_bbox_arome)

	forecastlayers = {
	"temperature": "TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
	"windspeed": "WIND_SPEED__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
	"humidity": "RELATIVE_HUMIDITY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
	"geom": "GEOMETRIC_HEIGHT__GROUND_OR_WATER_SURFACE",
	}
	
	cosrica_mapheight=800
	cosrica_mapwidth=600

	# load client 
	client = Client()

	temp_layermap = client.get_wms_map(		
	    layers = forecastlayers["temperature"],
		bbox = corsica_bbox_arome,
		height = str(cosrica_mapheight),
		width = str(cosrica_mapwidth)
		)


	help_layermap = client.get_wms_map(		
	    layers = forecastlayers["geom"],
		bbox = corsica_bbox_arome,
		height = str(cosrica_mapheight),
		width = str(cosrica_mapwidth)
		)


	wind_layermap = client.get_wms_map(		
	    layers = forecastlayers["windspeed"],
		bbox = corsica_bbox_arome,
		height = str(cosrica_mapheight),
		width = str(cosrica_mapwidth)
		)

	humi_layermap = client.get_wms_map(		
	    layers = forecastlayers["humidity"],
		bbox = corsica_bbox_arome,
		height = str(cosrica_mapheight),
		width = str(cosrica_mapwidth)
		)




	tempglobal_layermap = client.get_wms_map(		
	    layers = forecastlayers["temperature"],
		bbox = global_bbox_arome,
		height = str(cosrica_mapheight),
		width = str(cosrica_mapwidth)
		)




	#############################################################
	## Layout with Two Columns: Map and Legend
	#############################################################

	if fig:


		corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"


		# Function to load an image using Pillow
		def load_image(url):
		    try:
		        # Fetch the image from the URL
		        response = requests.get(url, allow_redirects=True,  headers = {'User-agent': 'your bot 0.1'})
		        print('corsica_map_response:',response)
		        
		        # Check if the response is successful
		        if response.status_code == 200:
		            return Image.open(BytesIO(response.content))  # Return the image as a Pillow object
		        else:
		            st.error(f"Failed to load image from {url}. Status code: {response.status_code}")
		            return None
		    except requests.exceptions.RequestException as e:
		        st.error(f"Request failed: {e}")
		        return None

		corsica_map = load_image(corsicamap_st_url)
	
			
		help_img = Image.open(BytesIO(help_layermap.content))


		# Resize the help image to match the Corsica map size if needed
		help_img = help_img.resize(corsica_map.size)

		# Apply transparency (set alpha) to the help image
		help_img = help_img.convert("RGBA")  # Ensure it's in RGBA mode for transparency
		alpha = 0.45  # Adjust transparency level (0 is fully transparent, 1 is fully opaque)
		help_img.putalpha(int(255 * alpha))

		# Merge the two images
		combined_img = Image.alpha_composite(corsica_map.convert("RGBA"), help_img)

		# Display the final combined image
		st.image(combined_img, caption="Overlay of Corsica Map and Elevation Map", use_column_width=True)


		st.image(corsica_map, caption="corsica_map", use_column_width=True)
		st.image(help_img, caption="Elevation Map", use_column_width=True)	





		# plotly_img = Image.open("plotly_fig.png") 
		temp_img = Image.open(BytesIO(temp_layermap.content))		
		st.image(temp_img, caption="Temperature Forecast Map", use_column_width=True)



		# temp_globalimg = Image.open(BytesIO(tempglobal_layermap.content))
		# st.image(temp_globalimg, caption="Temperature Forecast Map", use_column_width=True)






		wind_img = Image.open(BytesIO(wind_layermap.content))
		st.image(wind_img, caption="Wind Forecast Map", use_column_width=True)

		humi_img = Image.open(BytesIO(humi_layermap.content))
		st.image(humi_img, caption="Humidity Forecast Map", use_column_width=True)

		# st.plotly_chart(layermap, use_container_width=True)




		st.header("Exploration")
        # it also work like that:
        # corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"
		# st.image(corsicamap_st_url, caption="Corsica Map", width=600)

         



