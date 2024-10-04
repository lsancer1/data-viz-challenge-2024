import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import xarray as xr
import pandas as pd
import calendar
import numpy as np
import yaml
from attrdictionary import AttrDict as attributedict

#############################################################
## Load configs parameter
#############################################################

with open("./../configs/main_lucas.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

config = attributedict(config)
pathtofolder = config.dashboard.data.cams.folder
keptfiles = list(config.dashboard.data.cams.keptfiles)

#############################################################
## Load files
#############################################################

ext = '.nc'

dust = pathtofolder + keptfiles[0] + ext
pm10 = pathtofolder + keptfiles[1] + ext
pm25 = pathtofolder + keptfiles[2] + ext
pmwildfires = pathtofolder + keptfiles[3] + ext

# Load datasets directly without 'with open()'
dust_data = xr.open_dataset(dust)
pm10_data = xr.open_dataset(pm10)
pm25_data = xr.open_dataset(pm25)
pmwildfires_data = xr.open_dataset(pmwildfires)

#############################################################
## Dash app
#############################################################

available_data = ['Dust', 'PM10 particles', 'PM2.5 particles', 'PM wildfires']
datasets = {
    'Dust': dust_data,
    'PM10 particles': pm10_data,
    'PM2.5 particles': pm25_data,
    'PM wildfires': pmwildfires_data
}

data_options = [{'label': element, 'value': element} for element in available_data]

# Initialize the Dash app
app = dash.Dash(__name__)

# Modify the layout to include a slider for day selection and an animate button
app.layout = html.Div([
    html.H1("Air pollution levels over time"),
    html.Div([
        html.Label('Select Data:'),
        dcc.Dropdown(
            id='data-dropdown',
            options=data_options,
            value=available_data[0]
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Select Month:'),
        dcc.Dropdown(
            id='month-dropdown',
            options=[],
            value=None
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Select Day:'),
        dcc.Slider(
            id='day-slider',
            min=1,
            max=31,
            value=1,
            marks={},  # We'll update this dynamically
            step=None  # Set step to None to select only marked days
        ),
    ], style={'width': '90%', 'padding': '0px 20px 20px 20px'}),
    html.Button('Animate', id='animate-button', n_clicks=0),
    dcc.Graph(id='map'),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Interval in milliseconds (adjust as needed)
        n_intervals=0,
        disabled=True  # Initially disabled
    )
])

# Callback to update the month options based on the selected dataset
@app.callback(
    Output('month-dropdown', 'options'),
    Output('month-dropdown', 'value'),
    Input('data-dropdown', 'value')
)
def update_month_options(selected_data):
    data = datasets[selected_data]
    times = pd.to_datetime(data.time.values)
    available_months = np.unique(times.month)
    available_months.sort()
    month_options = [{'label': calendar.month_name[month], 'value': month} for month in available_months]
    default_month = available_months[0] if len(available_months) > 0 else None
    return month_options, default_month

# Callback to update the day slider based on the selected dataset and month
@app.callback(
    Output('day-slider', 'min'),
    Output('day-slider', 'max'),
    Output('day-slider', 'marks'),
    Output('day-slider', 'value'),
    Input('data-dropdown', 'value'),
    Input('month-dropdown', 'value'),
)
def update_day_slider(selected_data, selected_month):
    if selected_month is None:
        return 1, 31, {}, 1  # Default values
    data = datasets[selected_data]
    times = pd.to_datetime(data.time.values)
    month_times = times[times.month == selected_month]
    available_days = np.unique(month_times.day)
    available_days.sort()
    if len(available_days) == 0:
        return 1, 31, {}, 1  # No available days
    min_day = int(available_days[0])
    max_day = int(available_days[-1])
    marks = {int(day): str(int(day)) for day in available_days}
    default_day = int(available_days[0])
    return min_day, max_day, marks, default_day

# Callback to control the interval component based on the animate button
@app.callback(
    Output('interval-component', 'disabled'),
    Output('interval-component', 'n_intervals'),
    Input('animate-button', 'n_clicks')
)
def control_animation(n_clicks):
    if n_clicks % 2 == 1:
        # If the button has been clicked an odd number of times, enable the animation
        return False, 0  # Enable interval, reset n_intervals
    else:
        # Otherwise, disable the animation
        return True, dash.no_update  # Disable interval, keep n_intervals unchanged

# Callback to update the animate button text
@app.callback(
    Output('animate-button', 'children'),
    Input('animate-button', 'n_clicks')
)
def update_button_text(n_clicks):
    if n_clicks % 2 == 1:
        return 'Pause'
    else:
        return 'Animate'

# Callback to update the map based on the selected dataset, month, and day
@app.callback(
    Output('map', 'figure'),
    Input('data-dropdown', 'value'),
    Input('month-dropdown', 'value'),
    Input('day-slider', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('animate-button', 'n_clicks')
)
def update_map(selected_data, selected_month, selected_day, n_intervals, n_clicks):
    dataset = datasets[selected_data]
    times = pd.to_datetime(dataset.time.values)
    ctx = dash.callback_context

    # Determine which input triggered the callback
    if not ctx.triggered:
        trigger_id = 'No clicks yet'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle animation
    if trigger_id == 'interval-component' and n_clicks % 2 == 1:
        # Get available days
        month_times = times[times.month == selected_month]
        available_days = np.unique(month_times.day)
        available_days.sort()
        # Update selected_day based on n_intervals
        selected_day = available_days[n_intervals % len(available_days)]
    elif selected_day is None or selected_month is None:
        # If no day or month is selected, return an empty figure
        fig = px.scatter_mapbox()
        fig.update_layout(
            title="No date selected.",
            mapbox_style='open-street-map'
        )
        return fig

    # Filter the dataset to the selected date
    selected_date = pd.Timestamp(year=2023, month=selected_month, day=int(selected_day))
    selected_times = times[(times.month == selected_month) & (times.day == selected_day)]

    variable_name = list(dataset.keys())[0]

    if selected_times.empty:
        # Handle case where there is no data for the selected date
        fig = px.scatter_mapbox()
        fig.update_layout(
            title="No data available for the selected date.",
            mapbox_style='open-street-map'
        )
        return fig

    units = dataset[variable_name].attrs.get('units', '')
    data = dataset.sel(time=selected_times).mean(dim='time')

    # Prepare data for plotting
    aerosol = data[variable_name]
    latitudes = data.lat.values
    longitudes = data.lon.values

    # Calculate the number of points for the new grid
    num_new_lon = longitudes.size * 10
    num_new_lat = latitudes.size * 10

    # Create new longitude and latitude arrays
    new_lon = np.linspace(longitudes.min().item(), longitudes.max().item(), num=num_new_lon)
    new_lat = np.linspace(latitudes.min().item(), latitudes.max().item(), num=num_new_lat)

    lon, lat = np.meshgrid(new_lon, new_lat)

    aerosol_interp = aerosol.interp(lon=new_lon, lat=new_lat, method='cubic')

    df_interp = pd.DataFrame({
        'Latitude': lat.ravel(),
        'Longitude': lon.ravel(),
        'Aerosol': aerosol_interp.values.flatten()
    })

    # Create the figure using Plotly Express
    fig = px.scatter_mapbox(
        df_interp,
        lat='Latitude',
        lon='Longitude',
        color='Aerosol',
        color_continuous_scale='Viridis',
        mapbox_style='open-street-map',
        zoom=7,
        center={"lat": 42.16, "lon": 9.13},  # Center map on the data
        title=f"{variable_name.capitalize()} Levels on {selected_date.strftime('%Y-%m-%d')}",
        opacity=0.1,
        height=800,
        width=800
    )

    # Adjust marker size and opacity for better visualization
    colorbar_title = f"{variable_name.capitalize()} ({units})"
    fig.layout.coloraxis.colorbar.title = colorbar_title
    fig.update_traces(marker={'size': 8})

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)