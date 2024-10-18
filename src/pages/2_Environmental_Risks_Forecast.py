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
        'tab1name': "Temperature Forecast",
        'title1': "Temperature Forecast",
        'tab1options': "Options",

        'tab2name': "Wind Forecast",
        'title2': "Wind Forecast",

        'tab3name': "Snow Forecast",
        'title3': "Snow precipitation Forecast",

        'tab4name': "Rain Forecast",
        'title4': "Rain precipitation Forecast",

        'tab5name': "Humidity Forecast",
        'title5': "Humidity level Forecast",


    },
    'fr': {
        'tab1name': "Prévision température",
        'title1': "Prévision de température",
        'tab1options': "Options",

        'tab2name': "Prévision vent",
        'title2': "Prévision de la force du vent",

        'tab3name': "Prévision neige",
        'title3': "Prévision précipitation de neige",

        'tab4name': "Prévision pluie",
        'title4': "Prévision précipitation de pluie",

        'tab5name': "Prévision d'humidité",
        'title5': "Prévision du taux d'humidité",
    }
}

# Language selection
language = st.sidebar.selectbox('Select language:', ['Français', 'English'])
if language == 'Français':
    lang_code = 'fr'   
else:
    lang_code = 'en'

# Tab names
tab1, tab2, tab3, tab4, tab5 = st.tabs([translations[lang_code]['tab1name'], 
				    		 translations[lang_code]['tab2name'],
				    		 translations[lang_code]['tab3name'],
				    		 translations[lang_code]['tab4name'],
				    		 translations[lang_code]['tab5name']])



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



###### UTILS 


def find_stretch_dim(image):
	"""
	"""
	# Define the new size for the output image
	output_width = image.width
	output_height = image.height

	# Define how much you want to stretch the center section horizontally
	stretch_factor = 1.25  # Increase this value to stretch more

	# Calculate crop dimensions (assuming you want to crop from the center)
	crop_width = int(output_width / stretch_factor)  # Crop width is reduced by the stretch factor
	crop_height = output_height  # Keep the full height

	# Get the center crop box
	left = (output_width - crop_width) / 2
	top = 0
	right = (output_width + crop_width) / 2
	bottom = output_height

	# Crop the center of the image
	cropped_img = image.crop((left, top, right, bottom))

	# Stretch the cropped image to the new width
	stretched_center = cropped_img.resize((output_width, crop_height))

	return stretched_center, output_width, output_height




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



#############################################################
## Generate and Display Forecast
#############################################################


miny_corsica="41.3" 
minx_corsica="7.93" 
maxy_corsica="43.1"
maxx_corsica="10" 

corsica_bbox_arome = miny_corsica+","+minx_corsica+","+maxy_corsica+","+maxx_corsica 

forecastlayers = {
"temperature": "TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
"windspeed": "WIND_SPEED__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
"snow":  "TOTAL_SNOW_PRECIPITATION__GROUND_OR_WATER_SURFACE",
"rain": "TOTAL_WATER_PRECIPITATION__GROUND_OR_WATER_SURFACE",
"humidity": "RELATIVE_HUMIDITY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
"geom": "GEOMETRIC_HEIGHT__GROUND_OR_WATER_SURFACE",
}

cosrica_mapheight=570
cosrica_mapwidth=757

# load client 
client = Client()


# Used to size and transform the map to fit Corsica map
help_layermap = client.get_wms_map(		
    layers = forecastlayers["geom"],
	bbox = corsica_bbox_arome,
	height = str(cosrica_mapheight),
	width = str(cosrica_mapwidth)
	)



temp_layermap = client.get_wms_map(		
    layers = forecastlayers["temperature"],
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


snow_layermap = client.get_wms_map(		
    layers = forecastlayers["snow"],
	bbox = corsica_bbox_arome,
	height = str(cosrica_mapheight),
	width = str(cosrica_mapwidth)
	)

rain_layermap = client.get_wms_map(		
    layers = forecastlayers["rain"],
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





# hardcoded parameters for the forecast
# example_bbox = "37.5,-12,55.4,16"
# example_mapheight=300
# example_mapwidth=300


# corsica_bbox_ori =  "43.25,8.15,41.15,10.15"

# globalminy=float(miny_corsica)
# globalminx=float(minx_corsica)
# globalmaxy=float(maxy_corsica)
# globalmaxx=float(maxx_corsica)

# global_bbox_arome = str(globalminy)+","+str(globalminx)+","+str(globalmaxy)+","+str(globalmaxx)
# print("global_bbox_arome",global_bbox_arome)

# corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"
# st.image(corsicamap_st_url, caption="Corsica Map", width=600)

# humi_img = Image.open(BytesIO(humi_layermap.content))
# st.image(humi_img, caption="Humidity Forecast Map", use_column_width=True)


#############################################################
## Tab1 
#############################################################


with tab1:

	####### Tab management 

	st.session_state['active_tab'] = translations[lang_code]['tab1name']
	st.title(translations[lang_code]['title1'])

	st.sidebar.header(translations[lang_code]['tab1options'])

	###### Layout 

	### First header and text
	st.header("Exploration")
	st.markdown("Text to put here")

	### Second plot the combioned image
	corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"

	corsica_map = load_image(corsicamap_st_url)
	# size (1428, 1806)
		
	temp_img = Image.open(BytesIO(temp_layermap.content))	

	output = find_stretch_dim(temp_img)
	stretched_center = output[0]
	output_width = output[1]
	output_height = output[2]

	# Create a new blank image with the same dimensions as the original
	temp_img = Image.new("RGB", (output_width, output_height))

	# Paste the stretched center back into the new image
	temp_img.paste(stretched_center, (0, 0))

	# Resize the help image to match the Corsica map size if needed
	temp_img = temp_img.resize(corsica_map.size)

	# Apply transparency (set alpha) to the help image
	temp_img = temp_img.convert("RGBA")  # Ensure it's in RGBA mode for transparency
	alpha = 0.35  # Adjust transparency level (0 is fully transparent, 1 is fully opaque)
	temp_img.putalpha(int(255 * alpha))

	# Merge the two images
	combined_img = Image.alpha_composite(corsica_map.convert("RGBA"), temp_img)

	# Display the final combined image
	st.image(combined_img, caption="Put caption here")



#############################################################
## Tab2 
#############################################################


with tab2:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab2name']
	st.title(translations[lang_code]['title2'])

	st.sidebar.header(translations[lang_code]['tab1options'])

	###### Layout 

	### First header and text
	st.header("Exploration")
	st.markdown("Text to put here")

	### Second plot the combioned image
	corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"

	corsica_map = load_image(corsicamap_st_url)
	# size (1428, 1806)
		
	wind_img = Image.open(BytesIO(wind_layermap.content))	

	output = find_stretch_dim(wind_img)
	stretched_center = output[0]
	output_width = output[1]
	output_height = output[2]

	# Create a new blank image with the same dimensions as the original
	wind_img = Image.new("RGB", (output_width, output_height))

	# Paste the stretched center back into the new image
	wind_img.paste(stretched_center, (0, 0))

	# Resize the help image to match the Corsica map size if needed
	wind_img = wind_img.resize(corsica_map.size)

	# Apply transparency (set alpha) to the help image
	wind_img = wind_img.convert("RGBA")  # Ensure it's in RGBA mode for transparency
	alpha = 0.35  # Adjust transparency level (0 is fully transparent, 1 is fully opaque)
	wind_img.putalpha(int(255 * alpha))

	# Merge the two images
	combined_img = Image.alpha_composite(corsica_map.convert("RGBA"), wind_img)

	# Display the final combined image
	st.image(combined_img, caption="Put caption here")




#############################################################
## Tab3
#############################################################


with tab3:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab3name']
	st.title(translations[lang_code]['title3'])

	st.sidebar.header(translations[lang_code]['tab1options'])

	###### Layout 

	### First header and text
	st.header("Exploration")
	st.markdown("Text to put here")

	### Second plot the combioned image
	corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"

	corsica_map = load_image(corsicamap_st_url)
	# size (1428, 1806)
		
	snow_img = Image.open(BytesIO(snow_layermap.content))	

	output = find_stretch_dim(snow_img)
	stretched_center = output[0]
	output_width = output[1]
	output_height = output[2]

	# Create a new blank image with the same dimensions as the original
	snow_img = Image.new("RGB", (output_width, output_height))

	# Paste the stretched center back into the new image
	snow_img.paste(stretched_center, (0, 0))

	# Resize the help image to match the Corsica map size if needed
	snow_img = snow_img.resize(corsica_map.size)

	# Apply transparency (set alpha) to the help image
	snow_img = snow_img.convert("RGBA")  # Ensure it's in RGBA mode for transparency
	alpha = 0.35  # Adjust transparency level (0 is fully transparent, 1 is fully opaque)
	snow_img.putalpha(int(255 * alpha))

	# Merge the two images
	combined_img = Image.alpha_composite(corsica_map.convert("RGBA"), snow_img)

	# Display the final combined image
	st.image(combined_img, caption="Put caption here")



#############################################################
## Tab4
#############################################################


with tab4:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab4name']
	st.title(translations[lang_code]['title4'])

	st.sidebar.header(translations[lang_code]['tab1options'])

	###### Layout 

	### First header and text
	st.header("Exploration")
	st.markdown("Text to put here")

	### Second plot the combioned image
	corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"

	corsica_map = load_image(corsicamap_st_url)
	# size (1428, 1806)
		
	rain_img = Image.open(BytesIO(rain_layermap.content))	

	output = find_stretch_dim(rain_img)
	stretched_center = output[0]
	output_width = output[1]
	output_height = output[2]

	# Create a new blank image with the same dimensions as the original
	rain_img = Image.new("RGB", (output_width, output_height))

	# Paste the stretched center back into the new image
	rain_img.paste(stretched_center, (0, 0))

	# Resize the help image to match the Corsica map size if needed
	rain_img = rain_img.resize(corsica_map.size)

	# Apply transparency (set alpha) to the help image
	rain_img = rain_img.convert("RGBA")  # Ensure it's in RGBA mode for transparency
	alpha = 0.35  # Adjust transparency level (0 is fully transparent, 1 is fully opaque)
	rain_img.putalpha(int(255 * alpha))

	# Merge the two images
	combined_img = Image.alpha_composite(corsica_map.convert("RGBA"), rain_img)

	# Display the final combined image
	st.image(combined_img, caption="Put caption here")






#############################################################
## Tab5
#############################################################


with tab5:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab5name']
	st.title(translations[lang_code]['title5'])

	st.sidebar.header(translations[lang_code]['tab1options'])

	###### Layout 

	### First header and text
	st.header("Exploration")
	st.markdown("Text to put here")

	### Second plot the combioned image
	corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"

	corsica_map = load_image(corsicamap_st_url)
	# size (1428, 1806)
		
	humi_img = Image.open(BytesIO(humi_layermap.content))	

	output = find_stretch_dim(humi_img)
	stretched_center = output[0]
	output_width = output[1]
	output_height = output[2]

	# Create a new blank image with the same dimensions as the original
	humi_img = Image.new("RGB", (output_width, output_height))

	# Paste the stretched center back into the new image
	humi_img.paste(stretched_center, (0, 0))

	# Resize the help image to match the Corsica map size if needed
	humi_img = humi_img.resize(corsica_map.size)

	# Apply transparency (set alpha) to the help image
	humi_img = humi_img.convert("RGBA")  # Ensure it's in RGBA mode for transparency
	alpha = 0.35  # Adjust transparency level (0 is fully transparent, 1 is fully opaque)
	humi_img.putalpha(int(255 * alpha))

	# Merge the two images
	combined_img = Image.alpha_composite(corsica_map.convert("RGBA"), humi_img)

	# Display the final combined image
	st.image(combined_img, caption="Put caption here")
         



