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
        'tab1header': "Options",
        'network_text1': "Visualisation du réseau électrique aérien en Corse. \n\n" \
         " Le réseau électrique est vulnérable aux risques climatiques tels que le vent." \
         " Egalement lorsque l'humidité est de plus de 30%, le vent de plus de 30km/h et la température de plus de 30°C" \
         " les feux de forêt son probables (règle des trois 30) et peuvent donc endommager le réseau."  \
         " Vous pouvez explorer les prévisions de risques climatiques sur l'onglet  `Environmental Risks Forecast`. \n\n" \
         "- Les points BT indiquent la localisation des lignes électrique basse tension \n\n" \
         "- Les points HTA indiquent la localisation des lignes électrique haute tension \n\n" \
  		 "- Les points Pylones HTB indiquent la localisation des pylones de lignes électrique très haute tension",

  		 'cat_bt':"Aerial BT",
  		 'cat_hta':"Aerial HTA",
  		 'cat_htb':"HTB Poles",

    },

    'fr': {
        'tab1name': "Réseau electrique aérien",
        'title1': "Localisation des lignes du réseau électrique aérien",
        'tab1options': "Options",
        'tab1header': "Options",
        'network_text1': "Visualisation du réseau électrique aérien en Corse. \n\n" \
         " Le réseau électrique est vulnérable aux risques climatiques tels que le vent." \
         " Egalement lorsque l'humidité est de plus de 30%, le vent de plus de 30km/h et la température de plus de 30°C" \
         " les feux de forêt son probables (règle des trois 30) et peuvent donc endommager le réseau."  \
         " Vous pouvez explorer les prévisions de risques climatiques sur l'onglet  `Environmental Risks Forecast`. \n\n" \
         "- Les points BT indiquent la localisation des lignes électrique basse tension \n\n" \
         "- Les points HTA indiquent la localisation des lignes électrique haute tension \n\n" \
  		 "- Les points Pylones HTB indiquent la localisation des pylones de lignes électrique très haute tension",

  		 'cat_bt':"BT aérien",
  		 'cat_hta':"HTA aérien",
  		 'cat_htb':"Pylones HTB",
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
#     geojson_pylones = json.load(f)translations[lang_code]['tab1name']


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
## Tab1 
#############################################################


with tab1:
	st.session_state['active_tab'] = translations[lang_code]['tab1name']
	st.title(translations[lang_code]['title1'])

	# Explanations about electricity network
	st.write(translations[lang_code]['network_text1'])
	

	def generate_map_tab1(bt_aerien_coord, hta_aerien_coord, htb_aerien_coord,pylones_coord):
   	 # Step 1: Combine your data into one DataFrame

		data = []
		for point in bt_aerien_coord:
		 	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		 	'Category': translations[lang_code]['cat_bt'], 'Statut': point['statut']})
		for point in hta_aerien_coord:
		 	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		 	'Category': translations[lang_code]['cat_hta'], 'Statut': point['statut']})
		for point in pylones_coord:
		 	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		 	'Category': translations[lang_code]['cat_htb'], 'Statut': point['statut']})
		# for point in htb_aerien_coord:
		#  	data.append({'Latitude': point['lat'], 'Longitude': point['lon'], 
		# 'Category': 'HTB aérien', 'Statut': point['statut']})
		## -> USEless if Pylones

		# Create a DataFrame
		df = pd.DataFrame(data)

		# Define your custom color map
		custom_colors = {
			translations[lang_code]['cat_bt']: 'blue',   
			translations[lang_code]['cat_hta']: 'red',    
			translations[lang_code]['cat_htb']: 'orange'  
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
			 title="",
			 height=800,
			 width=800,
			 color_discrete_map=custom_colors  # Apply custom color map
		 )

		return fig



	fig = generate_map_tab1(bt_aerien_coord, hta_aerien_coord, htb_aerien_coord, pylones_coord)

	

	if fig:



		st.plotly_chart(fig, use_container_width=True)



         



