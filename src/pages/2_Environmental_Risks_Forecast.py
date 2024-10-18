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
        'tab1name': "Wind Forecast",
        'title1': "Wind Forecast",
        'taboptions': "Options",
        'hour_selection': "Select number of hours from now to display forecast",
        'im_caption1' : "Wind Forecast",

        'wind_pres_text': "The forecast time window is shown just above. Risks are explained below the picture. \n\n" \
          "Wind forecasts are crucial for determining potential risks to infrastructure (such as ports and electrical lines) as well as people's safety.\n\n" \
          "The forecast presents contours of wind velocity: the wind is constant along a line, and the value of the wind in meters per second is displayed over the line.",
        'wind_risks_header': "Risks linked to high wind force",
        'wind_risks_text': 
        "Severe winds (above 22 m/s): Can result in dangerous flying debris and increase the risk of accidents for pedestrians, vehicles, and cyclists. \n\n" \
        "Strong winds (above 14 m/s): Increased risk of property damage (fallen trees or damaged roofs) and power outages due to downed power lines. \n\n" \
       "Fire conditions (wind above 11 m/s): Increased risk of forest fires spreading rapidly, especially in dry conditions (low humidity). \n\n" \
       "Coastal areas (wind above 21 m/s): Risk of storm surges and flooding in coastal regions, especially during storms or hurricanes. \n\n",

        'tab2name': "Rain Forecast",
        'title2': "Rain precipitation Forecast",
        'im_caption2' : "Rain precipitation Forecast",

        'rain_pres_text': "The forecast time window is shown just above. Risks are explained below the picture. \n\n "\
         "Rain forecast is of great importance to determine potential risks for infrastructures (ports for example) but also people's safety \n\n" \
         "The forecast presents contours of rain quantity: the rain is constant along a line and the value of the rain is shown over the line. \n\n",
        'rain_risks_header': "Risks linked to rain intensity",
        'rain_risks_text': "Heavy rain (>50): increases the risk of flash flooding, particularly in urban areas where drainage systems might be overwhelmed. \n\n" \
        "Continuous rain (more than 20 for several days): can lead to landslides in mountainous regions due to saturated soil. \n\n" \
        "Localized intense rainfall (more than 15 mm in one hour): can overwhelm urban drainage systems and lead to flash floods, causing road and property damage. \n\n",



        'tab3name': "Humidity Forecast",
        'title3': "Humidity level Forecast",
        'im_caption3' : "Humidity level Forecast",

        'humidity_pres_text': "The forecast time window is shown just above. Risks are explained below the picture. \n\n "\
         "Humidity forecast allows to determine water concentration in the atmosphere. \n\n" \
         "The forecast presents contours of humidity : the humidity is constant along a line and the value of the humidity in percentage is shown over the line. \n\n",
        'humidity_risks_header': "Risks linked to humidity",
        'humidity_risks_text': "High humidity (above 85%): increases the risk of heat stress when combined with high temperatures. It also promotes the growth of mold and other allergens, exacerbating respiratory issues. \n\n" \
        "Low humidity (below 30%): can lead to wildfire risk in dry regions by drying out vegetation. Prolonged low humidity can also cause dry skin and irritation of the eyes and throat. \n\n" \
        "Rapid humidity changes (>20% within next hours): can impact materials and infrastructure, causing wood to swell or contract, which could lead to structural issues in buildings. \n\n" ,



        'tab4name': "Temperature Forecast",
        'title4': "Temperature Forecast",
        'im_caption4' : "Temperature Forecast",

        'temp_pres_text': "The forecast time window is shown just above. Risks are explained below the picture. \n\n "\
         "Temperature forecast is of great importance to determine potential risks for landscapes (in case of a fire propagation for example) but also for people's safety \n\n" \
        "The forecast presents contours of temperature : the temperature is constant along a line and the value of the temperature in degrees Celsius is shown over the line. \n\n",
        
        'temp_risks_header': "Risks linked to high temperature",
        'temp_risks_text': "Extreme heat (above 35°C): High temperatures increase the risk of heatstroke, especially for elderly people, children, and those with pre-existing health conditions. This can also strain power systems due to increased air conditioning use. \n\n "\
        "High temperatures (above 30°C): wildfire risk increases in dry, vegetated areas. High temperatures dry out vegetation, making it more flammable.  \n\n "\
        "Freezing temperatures (0°C and below): icy road conditions increase the risk of traffic accidents due to reduced tire grip and slippery surfaces. \n\n "\
        "Very cold temperatures (Below -10°C): extremely low temperatures can cause frostbite and hypothermia, particularly for those without adequate clothing or shelter. \n\n ",




        'tab5name': "Snow Forecast",
        'title5': "Snow precipitation Forecast",
        'im_caption5' : "Snow precipitation Forecast",
        'snow_risks_header': "Risks linked to snow",
        'snow_pres_text': "The forecast time window is shown just above. Risks are explained below the picture. \n\n "\
         "Snow forecast is of great importance to determine potential risks for mountainous areas. \n\n" \
        "The forecast presents contours of snow : the snow is constant along a line and the value of the snow is shown over the line. \n\n",
        'snow_risks_text': "Heavy snowfall (more than 10 cm in 24 hours): Increases the risk of structural damage to buildings, especially those with flat roofs, as well as road accidents due to low visibility and slippery conditions. \n\n "\
        "Snowfall at Higher Altitudes (>1500m): In mountainous areas, even moderate snow can pose risks such as avalanches and isolating communities. \n\n ",

    },

    'fr': {

        'tab1name': "Prévision vent",
        'title1': "Prévision de la force du vent",
        'taboptions': "Options",
        'hour_selection': "Sélectionnez le nombre d heure séparant de la prévison",
        'im_caption1' : "Prévision de la force du vent",

        'wind_pres_text': "La période de prévision est indiquée juste au-dessus. Les risques sont expliqués sous l'image. \n\n" \
          "Les prévisions de vent sont cruciales pour déterminer les risques potentiels pour les infrastructures (comme les ports et les lignes électriques), ainsi que pour la sécurité des personnes.\n\n" \
          "La prévision présente des contours de vitesse du vent : le vent est constant le long d'une ligne, et la valeur du vent en mètres par seconde est affichée sur la ligne.",

        'wind_risks_header': "Risques liés à la force du vent élevé",
        'wind_risks_text': 
        "Vents violents (au-dessus de 22 m/s) : peuvent entraîner des débris volants dangereux et augmenter le risque d'accidents pour les piétons, les véhicules et les cyclistes. \n\n" \
        "Vents forts (au-dessus de 14 m/s) : risque accru de dommages matériels (arbres tombés ou toits endommagés) et de coupures de courant dues à la chute de lignes électriques. \n\n" \
       "Conditions propices aux incendies (vent au-dessus de 11 m/s) : risque accru de propagation rapide des feux de forêt, surtout en cas de conditions sèches (faible humidité). \n\n" \
       "Zones côtières (vent au-dessus de 21 m/s) : risque de vagues de tempête et d'inondations dans les régions côtières, notamment lors des tempêtes ou des ouragans. \n\n",




        'tab2name': "Prévision pluie",
        'title2': "Prévision des précipitations de pluie",
        'im_caption2' : "Prévision des précipitations de pluie",

        'rain_pres_text': "La période de prévision est indiquée juste au-dessus. Les risques sont expliqués sous l'image. \n\n" \
                          "Les prévisions de pluie sont d'une grande importance pour déterminer les risques potentiels pour les infrastructures (comme les ports, par exemple), ainsi que pour la sécurité des personnes. \n\n" \
                          "La prévision présente des contours de quantité de pluie : la pluie est constante le long d'une ligne et la valeur de la pluie est affichée sur la ligne. \n\n",

        'rain_risks_header': "Risques liés à l'intensité des pluies",
        'rain_risks_text': "Pluies abondantes (>50 mm) : augmentent le risque d'inondations soudaines, particulièrement dans les zones urbaines où les systèmes de drainage peuvent être submergés. \n\n" \
                           "Pluie continue (plus de 20 mm pendant plusieurs jours) : peut provoquer des glissements de terrain dans les régions montagneuses en raison de la saturation des sols. \n\n" \
                           "Précipitations localisées intenses (plus de 15 mm en une heure) : peuvent submerger les systèmes de drainage urbains et provoquer des inondations soudaines, causant des dégâts aux routes et aux biens. \n\n",




        'tab3name': "Prévision d'humidité",
        'title3': "Prévision du taux d'humidité",
        'im_caption3' : "Prévision du taux d'humidité",

        'humidity_pres_text': "La période de prévision est indiquée juste au-dessus. Les risques sont expliqués sous l'image. \n\n" \
                              "La prévision de l'humidité permet de déterminer la concentration d'eau dans l'atmosphère. \n\n" \
                              "La prévision présente des contours d'humidité : l'humidité est constante le long d'une ligne et la valeur de l'humidité en pourcentage est affichée sur la ligne. \n\n",

        'humidity_risks_header': "Risques liés à l'humidité",
        'humidity_risks_text': "Humidité élevée (au-dessus de 85 %) : augmente le risque de stress thermique lorsqu'elle est combinée à des températures élevées. Elle favorise également la croissance de moisissures et d'autres allergènes, aggravant les problèmes respiratoires. \n\n" \
                               "Humidité faible (en dessous de 30 %) : peut entraîner un risque de feux de forêt dans les régions sèches en asséchant la végétation. Une humidité faible prolongée peut aussi provoquer une sécheresse de la peau et des irritations des yeux et de la gorge. \n\n" \
                               "Changements rapides d'humidité (>20 % dans les prochaines heures) : peuvent affecter les matériaux et les infrastructures, provoquant un gonflement ou une contraction du bois, ce qui pourrait entraîner des problèmes structurels dans les bâtiments. \n\n",




        'tab4name': "Prévision température",
        'title4': "Prévision de la température",
        'im_caption4' : "Prévision de la température",       
        'temp_pres_text': "La période de prévision est indiquée juste au-dessus. Les risques sont expliqués sous l'image. \n\n" \
                          "Les prévisions de température sont d'une grande importance pour déterminer les risques potentiels pour les paysages (en cas de propagation d'incendie, par exemple), mais aussi pour la sécurité des personnes. \n\n" \
                          "La prévision présente des contours de température : la température est constante le long d'une ligne et la valeur de la température en degrés Celsius est affichée sur la ligne. \n\n",

        'temp_risks_header': "Risques liés aux températures élevées",
        'temp_risks_text': "Chaleur extrême (au-dessus de 35°C) : Les températures élevées augmentent le risque de coup de chaleur, en particulier pour les personnes âgées, les enfants et ceux ayant des problèmes de santé préexistants. Cela peut également mettre à rude épreuve les systèmes électriques en raison de l'utilisation accrue de la climatisation. \n\n" \
                           "Températures élevées (au-dessus de 30°C) : Le risque de feux de forêt augmente dans les zones végétalisées et sèches. Les hautes températures assèchent la végétation, la rendant plus inflammable. \n\n" \
                           "Températures de gel (0°C et en dessous) : Les conditions glacées sur les routes augmentent le risque d'accidents de la circulation en raison de la réduction de l'adhérence des pneus et des surfaces glissantes. \n\n" \
                           "Températures très froides (en dessous de -10°C) : Les températures extrêmement basses peuvent provoquer des engelures et de l'hypothermie, en particulier pour ceux qui n'ont pas de vêtements ou d'abris adéquats. \n\n",




        'tab5name': "Prévision neige",
        'title5': "Prévision des précipitations de neige",
        'im_caption5' : "Prévision des précipitations de neige",       

        'snow_risks_header': "Risques liés à la neige",
        'snow_pres_text': "La période de prévision est indiquée juste au-dessus. Les risques sont expliqués sous l'image. \n\n" \
                          "Les prévisions de neige sont d'une grande importance pour déterminer les risques potentiels dans les zones montagneuses. \n\n" \
                          "La prévision présente des contours de neige : la neige est constante le long d'une ligne et la valeur de l'accumulation de neige est affichée sur la ligne. \n\n",

        'snow_risks_text': "Chutes de neige abondantes (plus de 10 cm en 24 heures) : Augmente le risque de dommages structurels aux bâtiments, en particulier ceux avec des toits plats, ainsi que les accidents de la route dus à une faible visibilité et des conditions glissantes. \n\n" \
                           "Chutes de neige à haute altitude (>1500m) : Dans les zones montagneuses, même une neige modérée peut poser des risques tels que des avalanches et l'isolement des communautés. \n\n",



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
		time: str,
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
	        "time": time,
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
## One Common Menu to all tabs
#############################################################

selected_hour = 24 # in case the option is not chosen already

st.sidebar.header(translations[lang_code]['taboptions'])

deltahours_options = [hour for hour in range(6,48,6)]
selected_hour = st.sidebar.selectbox(translations[lang_code]['hour_selection'], deltahours_options, index=0)

# Get current time in UTC
current_time = datetime.utcnow()
# st.write(datetime.utcnow())

# Set current time to the nearest past hour (removing minutes and seconds)
current_time = current_time.replace(minute=0, second=0, microsecond=0)

# Format the time in 'YYYY-MM-DDTHH:mm:ssZ' format
formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# Calculate future time
future_time = current_time + timedelta(hours=selected_hour)
formatted_future_time = future_time.strftime('%Y-%m-%dT%H:%M:%SZ')




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
	width = str(cosrica_mapwidth),
	time = formatted_future_time
	)



temp_layermap = client.get_wms_map(		
    layers = forecastlayers["temperature"],
	bbox = corsica_bbox_arome,
	height = str(cosrica_mapheight),
	width = str(cosrica_mapwidth),
	time = formatted_future_time
	)


wind_layermap = client.get_wms_map(		
    layers = forecastlayers["windspeed"],
	bbox = corsica_bbox_arome,
	height = str(cosrica_mapheight),
	width = str(cosrica_mapwidth),
	time = formatted_future_time
	)


snow_layermap = client.get_wms_map(		
    layers = forecastlayers["snow"],
	bbox = corsica_bbox_arome,
	height = str(cosrica_mapheight),
	width = str(cosrica_mapwidth),
	time = formatted_future_time
	)

rain_layermap = client.get_wms_map(		
    layers = forecastlayers["rain"],
	bbox = corsica_bbox_arome,
	height = str(cosrica_mapheight),
	width = str(cosrica_mapwidth),
	time = formatted_future_time
	)

humi_layermap = client.get_wms_map(		
    layers = forecastlayers["humidity"],
	bbox = corsica_bbox_arome,
	height = str(cosrica_mapheight),
	width = str(cosrica_mapwidth),
	time = formatted_future_time
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
  # Function to get available hours



#############################################################
## Tab1
#############################################################


with tab1:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab1name']
	st.title(translations[lang_code]['title1'])

	st.markdown(f"UTC Time chosen for prediction: `{formatted_future_time}` " )


	###### Layout 

	### First header and text
	st.markdown(translations[lang_code]['wind_pres_text'])

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

	### Second header and text
	st.header(translations[lang_code]['wind_risks_header'])
	st.markdown(translations[lang_code]['wind_risks_text'])




#############################################################
## Tab2
#############################################################


with tab2:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab2name']
	st.title(translations[lang_code]['title2'])

	st.markdown(f"UTC Time chosen for prediction: `{formatted_future_time}` " )


	###### Layout 

	### First header and text
	st.markdown(translations[lang_code]['rain_pres_text'])

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

	### Second header and text
	st.header(translations[lang_code]['rain_risks_header'])
	st.markdown(translations[lang_code]['rain_risks_text'])




#############################################################
## Tab3
#############################################################


with tab3:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab3name']
	st.title(translations[lang_code]['title3'])

	st.markdown(f"UTC Time chosen for prediction: `{formatted_future_time}` " )


	###### Layout 

	### First header and text
	st.markdown(translations[lang_code]['humidity_pres_text'])

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

	### Second header and text
	st.header(translations[lang_code]['humidity_risks_header'])
	st.markdown(translations[lang_code]['humidity_risks_text'])



#############################################################
## Tab4
#############################################################


with tab4:

	####### Tab management 

	st.session_state['active_tab'] = translations[lang_code]['tab4name']
	st.title(translations[lang_code]['title4'])

	st.markdown(f"UTC Time chosen for prediction: `{formatted_future_time}` " )


	###### Layout 

	### First header and text
	st.markdown(translations[lang_code]['temp_pres_text'])

	### Second plot the combioned image
	corsicamap_st_url = "https://i.imgur.com/MWch7ZP.png"

	corsica_map = load_image(corsicamap_st_url)
	# size (1428, 1806)

	print(temp_layermap.status_code)
	print(temp_layermap.headers.get('Content-Type'))

		
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
	alpha = 0.55  # Adjust transparency level (0 is fully transparent, 1 is fully opaque)
	temp_img.putalpha(int(255 * alpha))

	# Merge the two images
	combined_img = Image.alpha_composite(corsica_map.convert("RGBA"), temp_img)

	# Display the final combined image
	st.image(combined_img, caption="Put caption here")

	### Second header and text
	st.header(translations[lang_code]['temp_risks_header'])
	st.markdown(translations[lang_code]['temp_risks_text'])




#############################################################
## Tab5
#############################################################


with tab5:

	####### Tab management 
	
	st.session_state['active_tab'] = translations[lang_code]['tab5name']
	st.title(translations[lang_code]['title5'])

	st.markdown(f"UTC Time chosen for prediction: `{formatted_future_time}` " )


	###### Layout 

	### First header and text
	st.markdown(translations[lang_code]['snow_pres_text'])

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

	### Second header and text
	st.header(translations[lang_code]['snow_risks_header'])
	st.markdown(translations[lang_code]['snow_risks_text'])
         



