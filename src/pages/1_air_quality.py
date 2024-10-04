#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 15:46:31 2024

@author: alonso-pinar_a
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
from datetime import datetime
import cdsapi

#############################################################
## Load configs parameter
#############################################################

currently = 'cloud'

if currently == 'cloud':

    folder_path = os.getcwd()
    pathtofolder = os.path.join(folder_path, 'data/cams/')
    pathtoconfig = os.path.join(folder_path, 'configs/')
    
    with open( pathtoconfig + "main_alberto.yml", "r") as f:
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
    
ext = '.nc'

dust = pathtofolder + keptfiles[0] + ext
pm10 = pathtofolder + keptfiles[1] + ext
pm25 = pathtofolder + keptfiles[2] + ext
pmwildfires = pathtofolder + keptfiles[3] + ext

config = attributedict(config)
pathtofolder = config.dashboard.data.cams.folder
keptfiles = list(config.dashboard.data.cams.keptfiles)

#############################################################
## Load data
#############################################################


@st.cache_data
def load_data():
    dust_data = xr.open_dataset(dust)
    pm10_data = xr.open_dataset(pm10)
    pm25_data = xr.open_dataset(pm25)
    pmwildfires_data = xr.open_dataset(pmwildfires)
    return dust_data, pm10_data, pm25_data, pmwildfires_data

dust_data, pm10_data, pm25_data, pmwildfires_data = load_data()

available_data = ['Dust', 'PM10 particles', 'PM2.5 particles', 'PM wildfires']
datasets = {
    'Dust': dust_data,
    'PM10 particles': pm10_data,
    'PM2.5 particles': pm25_data,
    'PM wildfires': pmwildfires_data
}

def map_aqi_25(aerosol_value):
    if aerosol_value <= 25:
        return "Good"
    elif aerosol_value <= 50:
        return "Moderate"
    elif aerosol_value <= 100:
        return "Unhealthy for sensitive groups"
    elif aerosol_value <= 300:
        return "Unhealthy"
    else:
        return "Hazardous"
def map_aqi_10(aerosol_value):
    if aerosol_value <= 40:
        return "Good"
    elif aerosol_value <= 80:
        return "Moderate"
    elif aerosol_value <= 120:
        return "Unhealthy for sensitive groups"
    elif aerosol_value <= 300:
        return "Unhealthy"
    else:
        return "Hazardous"

# Define AQI levels with corresponding aerosol ranges and colors
aqi_levels_25 = [
    {"Level": "Good", "Range": "0-25", "Color": "#00E400", "Color_name":'Green'},           # Green
    {"Level": "Moderate", "Range": "26-50", "Color": "#FFFF00" , "Color_name":'Yellow'},      # Yellow
    {"Level": "Unhealthy for sensitive groups", "Range": "51-100", "Color": "#FF7E00" , "Color_name":'Orange'}, # Orange
    {"Level": "Unhealthy", "Range": "101-300", "Color": "#FF0000" , "Color_name":'Red'}, # Red
    {"Level": "Hazardous", "Range": "301+", "Color": "#8F3F97", "Color_name":'Purple'},    # Purple
]
aqi_levels_10 = [
    {"Level": "Good", "Range": "0-40", "Color": "#00E400", "Color_name":'Green'},           # Green
    {"Level": "Moderate", "Range": "41-80", "Color": "#FFFF00" , "Color_name":'Yellow'},      # Yellow
    {"Level": "Unhealthy for sensitive groups", "Range": "81-120", "Color": "#FF7E00" , "Color_name":'Orange'}, # Orange
    {"Level": "Unhealthy", "Range": "121-300", "Color": "#FF0000" , "Color_name":'Red'}, # Red
    {"Level": "Hazardous", "Range": "301+", "Color": "#8F3F97", "Color_name":'Purple'},    # Purple
]

# Create a DataFrame for the AQI legend
aqi_legend_25 = pd.DataFrame(aqi_levels_25)
aqi_legend_10 = pd.DataFrame(aqi_levels_10)


#############################################################
## Streamlit app
#############################################################

tab1, tab2 = st.tabs(['Historic air pollution levels', 'Forecast air pollution levels'])

if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 'Historic air pollution levels'
    

with tab1:
    st.session_state['active_tab'] = 'Historic air pollution levels'
    st.title("Air pollution levels over time")

    st.sidebar.header("HISTORIC - Filter Options")

    # Mode Selection: Raw Data or AQI Data
    mode = st.sidebar.radio("Select view mode:", ("Raw data", "AQI data"), key='firstTab')

    selected_data = st.sidebar.selectbox('Select data:', available_data)
    
    # Function to get available months
    def get_available_months(selected_data):
        data = datasets[selected_data]
        times = pd.to_datetime(data.time.values)
        available_months = np.unique(times.month)
        available_months.sort()
        month_options = [calendar.month_name[month] for month in available_months]
        return available_months, month_options
    
    available_months, month_options = get_available_months(selected_data)
    
    selected_month_name = st.sidebar.selectbox('Select month:', month_options)
    selected_month_index = month_options.index(selected_month_name)
    selected_month = available_months[selected_month_index]
    
    # Function to get available days
    def get_available_days(selected_data, selected_month):
        data = datasets[selected_data]
        times = pd.to_datetime(data.time.values)
        month_times = times[times.month == selected_month]
        available_days = np.unique(month_times.day)
        available_days.sort()
        return available_days
    
    available_days = get_available_days(selected_data, selected_month)
    day_options = [int(day) for day in available_days]
    selected_day = st.sidebar.select_slider('Select day:', options=day_options, value=int(day_options[0]))
    
    # Animate checkbox
    animate = st.sidebar.checkbox('Animate over days')
    
    #############################################################
    ## Function to generate static map
    #############################################################
    
    def generate_map(selected_data, selected_month, selected_day, mode):
        
        dataset = datasets[selected_data]
        times = pd.to_datetime(dataset.time.values)
        selected_date = pd.Timestamp(year=2023, month=selected_month, day=int(selected_day))
        selected_times = times[(times.month == selected_month) & (times.day == selected_day)]
        variable_name = list(dataset.keys())[0]
    
        if len(selected_times) == 0:
            st.warning("No data available for the selected date.")
            return None
    
        units = dataset[variable_name].attrs.get('units', '')
        data = dataset.sel(time=selected_times).mean(dim='time')
        aerosol = data[variable_name]
        latitudes = data.lat.values
        longitudes = data.lon.values

        # Interpolate data
        num_new_lon = int(longitudes.size * 10)
        num_new_lat = int(latitudes.size * 10)
        new_lon = np.linspace(longitudes.min().item(), longitudes.max().item(), num=num_new_lon)
        new_lat = np.linspace(latitudes.min().item(), latitudes.max().item(), num=num_new_lat)
        lon, lat = np.meshgrid(new_lon, new_lat)
        aerosol_interp = aerosol.interp(lon=new_lon, lat=new_lat, method='linear')
    
        df_interp = pd.DataFrame({
            'Latitude': lat.ravel(),
            'Longitude': lon.ravel(),
            'Aerosol': aerosol_interp.values.flatten()
        })
    
        if mode == "Raw data":
            # Raw Data Mode: Use continuous color scale
            fig = px.scatter_mapbox(
                df_interp,
                lat='Latitude',
                lon='Longitude',
                color='Aerosol',
                color_continuous_scale='Viridis',
                range_color=(df_interp['Aerosol'].min(), df_interp['Aerosol'].max()),
                mapbox_style='open-street-map',
                zoom=7,
                center={"lat": 42.16, "lon": 9.13},
                title=f"{variable_name.capitalize()} Levels on {selected_date.strftime('%Y-%m-%d')}",
                opacity=0.2,
                height=800,
                width=800,
                color_continuous_midpoint=0  # Adjust if needed
            )
            # Customize the colorbar
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=f"{variable_name.capitalize()} ({units})",
                    lenmode='fraction',
                    len=0.75,
                    yanchor='middle',
                    y=0.5
                )
            )
        else:
            # AQI Data Mode: Use discrete color scale
            # Map aerosol values to AQI levels
            if variable_name == 'dust' or variable_name == 'pm10' or variable_name == 'pmwildfire':
                df_interp['AQI_Level'] = df_interp['Aerosol'].apply(map_aqi_10)
        
                # color_discrete_map = {
                #     level['Level']: level['Color'] for level in aqi_levels_10
                # }
        
                # Create the custom discrete colorscale for colorbar
                aqi_thresholds = [0, 50, 100, 150, 200, 300]  # Extend max to 300 for colorbar
                aqi_colors = [level['Color'] for level in aqi_levels_10]
        
                # Normalize thresholds for Plotly colorscale (0 to 1)
                norm_thresholds = [thresh / 300 for thresh in aqi_thresholds]
                
        
                # Create colorscale with steps
                colorscale = []
                for i in range(len(aqi_thresholds)-1):
                    colorscale.append([norm_thresholds[i], aqi_colors[i]])
                    # Duplicate the threshold to create a sharp transition
                    if i < len(aqi_thresholds) - 1:
                        colorscale.append([norm_thresholds[i + 1], aqi_colors[i]])
            else:
                df_interp['AQI_Level'] = df_interp['Aerosol'].apply(map_aqi_25)
        
                # color_discrete_map = {
                #     level['Level']: level['Color'] for level in aqi_levels_25
                # }
        
                # Create the custom discrete colorscale for colorbar
                aqi_thresholds = [0, 50, 100, 150, 200, 300]  # Extend max to 300 for colorbar
                aqi_colors = [level['Color'] for level in aqi_levels_25]
        
                # Normalize thresholds for Plotly colorscale (0 to 1)
                norm_thresholds = [thresh / 300 for thresh in aqi_thresholds]
                
        
                # Create colorscale with steps
                colorscale = []
                for i in range(len(aqi_thresholds)-1):
                    colorscale.append([norm_thresholds[i], aqi_colors[i]])
                    # Duplicate the threshold to create a sharp transition
                    if i < len(aqi_thresholds) - 1:
                        colorscale.append([norm_thresholds[i + 1], aqi_colors[i]])
    
            # Create the figure with custom colorscale
            fig = px.scatter_mapbox(
                df_interp,
                lat='Latitude',
                lon='Longitude',
                color='Aerosol',
                color_continuous_scale=colorscale,
                range_color=(0, 300),  # Set the color axis range to match AQI thresholds
                mapbox_style='open-street-map',
                zoom=7,
                center={"lat": 42.16, "lon": 9.13},
                title=f"{variable_name.capitalize()} AQI Levels on {selected_date.strftime('%Y-%m-%d')}",
                opacity=0.2,
                height=800,
                width=800,
                color_continuous_midpoint=0  # Start color scale at 0
            )
    
            # Customize the colorbar to reflect AQI levels
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=f"{variable_name.capitalize()} AQI Levels",
                    tickmode='array',
                    tickvals=aqi_thresholds,
                    lenmode='fraction',
                    len=0.75,
                    yanchor='middle',
                    y=0.5
                )
            )
    
        return fig
    
    #############################################################
    ## Function to generate animated map
    #############################################################
    
    def generate_animated_map(selected_data, selected_month, mode):
        dataset = datasets[selected_data]
        times = pd.to_datetime(dataset.time.values)
        selected_times = times[times.month == selected_month]
        available_days = np.unique(selected_times.day)
    
        if len(available_days) == 0:
            st.warning("No data available for the selected month.")
            return None
    
        variable_name = list(dataset.keys())[0]
        units = dataset[variable_name].attrs.get('units', '')
        df_list = []
    
        for day in available_days:
            day_times = selected_times[selected_times.day == day]
            data = dataset.sel(time=day_times).mean(dim='time')
            aerosol = data[variable_name]
            latitudes = data.lat.values
            longitudes = data.lon.values
    
            # Interpolate data
            num_new_lon = int(longitudes.size * 10)
            num_new_lat = int(latitudes.size * 10)
            new_lon = np.linspace(longitudes.min().item(), longitudes.max().item(), num=num_new_lon)
            new_lat = np.linspace(latitudes.min().item(), latitudes.max().item(), num=num_new_lat)
            lon, lat = np.meshgrid(new_lon, new_lat)
            aerosol_interp = aerosol.interp(lon=new_lon, lat=new_lat, method='linear')
    
            df_interp = pd.DataFrame({
                'Latitude': lat.ravel(),
                'Longitude': lon.ravel(),
                'Aerosol': aerosol_interp.values.flatten(),
                'Day': int(day)
            })
    
            df_list.append(df_interp)
    
        df_all = pd.concat(df_list, ignore_index=True)
    
        if mode == "Raw data":
            # Raw Data Mode: Use continuous color scale
            fig = px.scatter_mapbox(
                df_all,
                lat='Latitude',
                lon='Longitude',
                color='Aerosol',
                color_continuous_scale='Viridis',
                range_color=(df_all['Aerosol'].min(), df_all['Aerosol'].max()),
                mapbox_style='open-street-map',
                zoom=7,
                center={"lat": 42.16, "lon": 9.13},
                title=f"{variable_name.capitalize()} Levels in {calendar.month_name[selected_month]}",
                opacity=0.2,
                height=800,
                width=800,
                animation_frame='Day',
                color_continuous_midpoint=0  # Adjust if needed
            )
            # Customize the colorbar
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=f"{variable_name.capitalize()} ({units})",
                    lenmode='fraction',
                    len=0.75,
                    yanchor='middle',
                    y=0.5
                )
            )
        else:
            # AQI Data Mode: Use discrete color scale
            # Map aerosol values to AQI levels
            
            if variable_name == 'dust' or variable_name == 'pm10' or variable_name == 'pmwildfire':
                df_all['AQI_Level'] = df_all['Aerosol'].apply(map_aqi_10)
    
                # color_discrete_map = {
                #     level['Level']: level['Color'] for level in aqi_levels_10
                # }
    
                # Create the custom discrete colorscale for colorbar
                aqi_thresholds = [0, 40, 80, 120, 300]  # Extend max to 300 for colorbar
                aqi_colors = [level['Color'] for level in aqi_levels_10]
    
                # Normalize thresholds for Plotly colorscale (0 to 1)
                norm_thresholds = [thresh / 300 for thresh in aqi_thresholds]
                
    
                # Create colorscale with steps
                colorscale = []
                for i in range(len(aqi_thresholds)):
                    colorscale.append([norm_thresholds[i], aqi_colors[i]])
                    # Duplicate the threshold to create a sharp transition
                    if i < len(aqi_thresholds) - 1:
                        colorscale.append([norm_thresholds[i + 1], aqi_colors[i]])
            else:
                df_all['AQI_Level'] = df_all['Aerosol'].apply(map_aqi_25)
    
                # color_discrete_map = {
                #     level['Level']: level['Color'] for level in aqi_levels_25
                # }
    
                # Create the custom discrete colorscale for colorbar
                aqi_thresholds = [0, 25, 50, 100, 300]  # Extend max to 300 for colorbar
                aqi_colors = [level['Color'] for level in aqi_levels_25]
    
                # Normalize thresholds for Plotly colorscale (0 to 1)
                norm_thresholds = [thresh / 300 for thresh in aqi_thresholds]
                
    
                # Create colorscale with steps
                colorscale = []
                for i in range(len(aqi_thresholds)):
                    colorscale.append([norm_thresholds[i], aqi_colors[i]])
                    # Duplicate the threshold to create a sharp transition
                    if i < len(aqi_thresholds) - 1:
                        colorscale.append([norm_thresholds[i + 1], aqi_colors[i]])
                
    
            # Create the animated figure with custom colorscale
            fig = px.scatter_mapbox(
                df_all,
                lat='Latitude',
                lon='Longitude',
                color='Aerosol',
                color_continuous_scale=colorscale,
                range_color=(0, 300),  # Set the color axis range to match AQI thresholds
                mapbox_style='open-street-map',
                zoom=7,
                center={"lat": 42.16, "lon": 9.13},
                title=f"{variable_name.capitalize()} AQI Levels in {calendar.month_name[selected_month]}",
                opacity=0.2,
                height=800,
                width=800,
                animation_frame='Day',
                color_continuous_midpoint=0  # Start color scale at 0
            )
    
            # Customize the colorbar to reflect AQI levels
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=f"{variable_name.capitalize()} AQI Levels",
                    tickmode='array',
                    tickvals=aqi_thresholds,
                    lenmode='fraction',
                    len=0.75,
                    yanchor='middle',
                    y=0.5
                )
            )
    
        return fig
    
    #############################################################
    ## Generate and Display the Map
    #############################################################
    
    if animate:
        fig = generate_animated_map(selected_data, selected_month, mode)
    else:
        fig = generate_map(selected_data, selected_month, selected_day, mode)
    
    #############################################################
    ## Layout with Two Columns: Map and AQI Legend
    #############################################################
    
    if fig:
        # Create two columns with a 3:1 ratio (map:legend)
        col1, col2 = st.columns([3, 1])
    
        with col1:
            st.plotly_chart(fig, use_container_width=True)
    
        with col2:
            dataset = datasets[selected_data]
            variable_name = list(dataset.keys())[0]

            if variable_name =='dust' or variable_name == 'pm10' or variable_name == 'pmwildfire':
                if mode == "AQI Data":
                    st.header("AQI Levels")
                    # Generate AQI legend using HTML with colored boxes and inline styles
                    aqi_legend_md = ""
                    for level in aqi_levels_10:
                        aqi_legend_md += f"**{level['Level']}**: \n\n"
                        aqi_legend_md += f"{level['Color_name']} ( {level['Range']} ) \n\n"
                    
                    st.markdown(aqi_legend_md)
                else:
                    # Optionally, display information or leave blank in Raw Data mode
                    st.header("Raw data view")
                    st.markdown("""
                        This view displays the raw aerosol concentration data without categorization into AQI levels.
                    """)
            else:
                if mode == "AQI Data":
                    st.header("AQI Levels")
                    # Generate AQI legend using HTML with colored boxes and inline styles
                    aqi_legend_md = ""
                    for level in aqi_levels_25:
                        aqi_legend_md += f"**{level['Level']}**: \n\n"
                        aqi_legend_md += f"{level['Color_name']} ( {level['Range']} ) \n\n"
                    
                    st.markdown(aqi_legend_md)
                else:
                    # Optionally, display information or leave blank in Raw Data mode
                    st.header("Raw data view")
                    st.markdown("""
                        This view displays the raw aerosol concentration data without categorization into AQI levels.
                    """)
            
with tab2:
    st.title("Forecasted air pollution levels")
    st.write("Choose your dataset and visualize the forecast.")
    
    st.session_state['active_tab'] = 'Forecast air pollution levels'
    
    variable_options = [
        "Dust",
        "10PM Particles",
        "2.5PM Particles",
        "PM from wildfires"
    ]
    
    st.sidebar.header("FORECAST - Filter Options")
    
    selected_variable = st.sidebar.selectbox(
        "Select variable: ",
        options=variable_options,
    )
    
    variable_options_dico = {
        "Dust": "dust",
        "10PM Particles": "particulate_matter_10um",
        "2.5PM Particles": "pm2.5_total_organic_matter",
        "PM from wildfires": "pm10_wildfires"
    }
    
    subvariable_options_dico = {
        "pm2.5_total_organic_matter":"pm2p5_total_om_conc",
        "dust":"dust",
        "particulate_matter_10um":"pm10_conc",
        "pm10_wildfires":"pmwf_conc"
        }

    # Define variable_name before the button
    variable_name = variable_options_dico[selected_variable]
    variable_in_dataset = subvariable_options_dico[variable_name]

    date = datetime.today().strftime('%Y-%m-%d') + "/" + datetime.today().strftime('%Y-%m-%d')

    # Move the sidebar header here
    st.sidebar.header("Filter Options")
    
    def generate_map(selected_data, selected_hour, mode):
        
        dataset = selected_data
        times = dataset.time.values
        selected_hours = pd.to_timedelta( selected_hour, 'h' )
        selected_time = times[times == selected_hours]
        variable_name = list(dataset.keys())[0]

        units = dataset[variable_in_dataset].attrs.get('units', '')
        data = dataset.sel(time=selected_time)
        aerosol = data[variable_in_dataset]
        latitudes = data.latitude.values
        longitudes = data.longitude.values

        # Interpolate data
        num_new_lon = int(longitudes.size * 10)
        num_new_lat = int(latitudes.size * 10)
        new_lon = np.linspace(longitudes.min().item(), longitudes.max().item(), num=num_new_lon)
        new_lat = np.linspace(latitudes.min().item(), latitudes.max().item(), num=num_new_lat)
        lon, lat = np.meshgrid(new_lon, new_lat)
        aerosol_interp = aerosol.interp(longitude=new_lon, latitude=new_lat, method='linear')
    
        df_interp = pd.DataFrame({
            'Latitude': lat.ravel(),
            'Longitude': lon.ravel(),
            'Aerosol': aerosol_interp.values.flatten()
        })
    
        if mode == "Raw data":
            # Raw Data Mode: Use continuous color scale
            fig = px.scatter_mapbox(
                df_interp,
                lat='Latitude',
                lon='Longitude',
                color='Aerosol',
                color_continuous_scale='Viridis',
                range_color=(df_interp['Aerosol'].min(), df_interp['Aerosol'].max()),
                mapbox_style='open-street-map',
                zoom=7,
                center={"lat": 42.16, "lon": 9.13},
                title=f"{variable_name.capitalize()} forecast in the next {selected_hour} hours",
                opacity=0.2,
                height=800,
                width=800,
                color_continuous_midpoint=0  # Adjust if needed
            )
            # Customize the colorbar
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=f"{variable_name.capitalize()} ({units})",
                    lenmode='fraction',
                    len=0.75,
                    yanchor='middle',
                    y=0.5
                )
            )
        else:
            # AQI Data Mode: Use discrete color scale
            # Map aerosol values to AQI levels
            if variable_name == 'dust' or variable_name == 'pm10' or variable_name == 'pmwildfire':
                df_interp['AQI_Level'] = df_interp['Aerosol'].apply(map_aqi_10)
        
                # color_discrete_map = {
                #     level['Level']: level['Color'] for level in aqi_levels_10
                # }
        
                # Create the custom discrete colorscale for colorbar
                aqi_thresholds = [0, 50, 100, 150, 200, 300]  # Extend max to 300 for colorbar
                aqi_colors = [level['Color'] for level in aqi_levels_10]
        
                # Normalize thresholds for Plotly colorscale (0 to 1)
                norm_thresholds = [thresh / 300 for thresh in aqi_thresholds]
                
        
                # Create colorscale with steps
                colorscale = []
                for i in range(len(aqi_thresholds)-1):
                    colorscale.append([norm_thresholds[i], aqi_colors[i]])
                    # Duplicate the threshold to create a sharp transition
                    if i < len(aqi_thresholds) - 1:
                        colorscale.append([norm_thresholds[i + 1], aqi_colors[i]])
            else:
                df_interp['AQI_Level'] = df_interp['Aerosol'].apply(map_aqi_25)
        
                # color_discrete_map = {
                #     level['Level']: level['Color'] for level in aqi_levels_25
                # }
        
                # Create the custom discrete colorscale for colorbar
                aqi_thresholds = [0, 50, 100, 150, 200, 300]  # Extend max to 300 for colorbar
                aqi_colors = [level['Color'] for level in aqi_levels_25]
        
                # Normalize thresholds for Plotly colorscale (0 to 1)
                norm_thresholds = [thresh / 300 for thresh in aqi_thresholds]
                
        
                # Create colorscale with steps
                colorscale = []
                for i in range(len(aqi_thresholds)-1):
                    colorscale.append([norm_thresholds[i], aqi_colors[i]])
                    # Duplicate the threshold to create a sharp transition
                    if i < len(aqi_thresholds) - 1:
                        colorscale.append([norm_thresholds[i + 1], aqi_colors[i]])
    
            # Create the figure with custom colorscale
            fig = px.scatter_mapbox(
                df_interp,
                lat='Latitude',
                lon='Longitude',
                color='Aerosol',
                color_continuous_scale=colorscale,
                range_color=(0, 300),  # Set the color axis range to match AQI thresholds
                mapbox_style='open-street-map',
                zoom=7,
                center={"lat": 42.16, "lon": 9.13},
                title=f"{variable_name.capitalize()} AQI forecast in the next {selected_hour} hours",
                opacity=0.2,
                height=800,
                width=800,
                color_continuous_midpoint=0  # Start color scale at 0
            )
    
            # Customize the colorbar to reflect AQI levels
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title=f"{variable_name.capitalize()} AQI Levels",
                    tickmode='array',
                    tickvals=aqi_thresholds,
                    lenmode='fraction',
                    len=0.75,
                    yanchor='middle',
                    y=0.5
                )
            )
    
        return fig

    if st.sidebar.button("Get Data"):
        with st.spinner('Downloading data...'):
            
            c = cdsapi.Client()
            cams_dataset_name = "cams-europe-air-quality-forecasts"
            request = {
                "variable": [variable_name],
                "model": ["ensemble"],
                "level": ["0"],
                "date": [date],
                "type": ["forecast"],
                "time": ["00:00"],
                "leadtime_hour": [
                    "6",
                    "12",
                    "18",
                    "24",
                    "30",
                    "36",
                    "42"
                ],
                "data_format": "netcdf_zip",
                "area": [43.25, 8.15, 41.15, 10.15]
            }
            response = c.retrieve(cams_dataset_name, request).download()

            with st.spinner('Extracting data...'):
                zip_file = zipfile.ZipFile(folder_path + '/' + response)
                netcdf_files = [name for name in zip_file.namelist() if name.endswith('.nc')]
                #netcdf_files = [name for name in os.listdir( folder_path ) if name.endswith('.nc')]
                netcdf_filename = netcdf_files[0]
                zip_file.extractall( folder_path )
                ds = xr.open_dataset(netcdf_filename)
                selected_data = ds

                # Store variables in session state
                st.session_state['selected_data'] = selected_data
                st.session_state['variable_name'] = variable_name
                st.session_state['selected_variable'] = selected_variable

    # Check if data is available in session state
    
    if 'selected_data' in st.session_state and st.session_state['active_tab'] == 'Forecast air pollution levels':
        selected_data = st.session_state['selected_data']
        variable_name = st.session_state['variable_name']
        selected_variable = st.session_state['selected_variable']

        # Mode Selection: Raw Data or AQI Data
        mode = st.sidebar.radio("Select view mode:", ("Raw data", "AQI data"), key='secondTab')

        # Function to get available hours
        def get_available_hours(selected_data):
            times = selected_data.time.values
            times_in_hours = [int(pd.to_timedelta(elt).total_seconds()/(60*60)) for elt in times]
            hours_options = np.unique(times_in_hours)
            hours_options.sort()
            return times_in_hours, hours_options

        available_hours, hours_options = get_available_hours(selected_data)
        selected_hour = st.sidebar.selectbox('Select hour:', hours_options, index=0)

        # Generate and display the map
        if variable_in_dataset in list(selected_data.keys()):
            fig = generate_map(selected_data, selected_hour, mode)
    
            # Layout with two columns: map and AQI legend
            if fig:
                
                col1, col2 = st.columns([3, 1])
                l1 = st.columns(1)
    
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
    
                with col2:
                    if variable_name in ['dust', 'pm10', 'pmwildfire']:
                        if mode == "AQI data":
                            st.header("AQI Levels")
                            aqi_legend_md = ""
                            for level in aqi_levels_10:
                                aqi_legend_md += f"**{level['Level']}**:\n\n"
                                aqi_legend_md += f"{level['Color_name']} ({level['Range']})\n\n"
                            st.markdown(aqi_legend_md)
                        else:
                            st.header("Raw data view")
                            st.markdown("""
                                This view displays the raw aerosol concentration data without categorization into AQI levels.
                            """)
                    else:
                        if mode == "AQI data":
                            st.header("AQI Levels")
                            aqi_legend_md = ""
                            for level in aqi_levels_25:
                                aqi_legend_md += f"**{level['Level']}**:\n\n"
                                aqi_legend_md += f"{level['Color_name']} ({level['Range']})\n\n"
                            st.markdown(aqi_legend_md)
                        else:
                            st.header("Raw data view")
                            st.markdown("""
                                This view displays the raw aerosol concentration data without categorization into AQI levels.
                            """)
                with l1[0]:
                    forecast_max = []
                    forecast_interpretation = []
                    times = []
                    if variable_name in ['dust', 'pm10', 'pmwildfire']:
                        for elt_time in selected_data.time:
                            converted_time = int(pd.to_timedelta(elt_time.values).total_seconds()/(60*60))
                            times.append( converted_time )
                            fmax = float(selected_data[variable_in_dataset].sel(time=elt_time).max().values)
                            forecast_max.append( fmax )
                            forecast_interpretation = map_aqi_10(fmax)
                            st.markdown(f"La qualité de l'air en Corse est prévue : **{forecast_interpretation}** dans {converted_time} heures. \n\n")
    
                    else:
                        for elt_time in selected_data.time:
                            converted_time = int(pd.to_timedelta(elt_time.values).total_seconds()/(60*60))
                            times.append( converted_time )
                            fmax = float(selected_data[variable_in_dataset].sel(time=elt_time).max().values)
                            forecast_max.append( fmax )
                            forecast_interpretation = map_aqi_25(fmax)
                            st.markdown(f"La qualité de l'air en Corse est prévue : **{forecast_interpretation}** dans {converted_time} heures. \n\n")
        else:
            st.write("Please click on 'Get Data' to load data.")
    else:
        st.write("Please click on 'Get Data' to load data.")


