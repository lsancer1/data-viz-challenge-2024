

"""Constants needed for the modules and the Streamlit application"""



#############################################################
## Forecast APIs
#############################################################


# AROME 0.01
serverurl = 'https://public-api.meteofrance.fr/public/arome/1.0'

AROME_WMS_CAPABILITIES_URL = serverurl + '/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities'
AROME_WMS_MAP_URL = serverurl + '/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetMap'
AROME_WCS_CAPABILITIES_URL = serverurl + '/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCapabilities'
AROME_WCS_COVDESCRIPTION_URL = serverurl + '/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/DescribeCoverage'
AROME_WCS_COVERAGE_URL = serverurl + '/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage'






#############################################################
## Other APIs
#############################################################

## From https://github.com/anquetos/meteoviz-streamlit-app/blob/main/constants.py 

# Observation and Climatological APIs
STATION_LIST_URL = 'https://public-api.meteofrance.fr/public/DPObs/v1/liste-stations'
HOURLY_OBSERVATION_URL = 'https://public-api.meteofrance.fr/public/DPObs/v1/station/horaire'
ORDER_HOURLY_CLIMATOLOGICAL_URL = 'https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/horaire'
ORDER_DAILY_CLIMATOLOGICAL_URL = 'https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/quotidienne'
ORDER_RECOVERY_URL = 'https://public-api.meteofrance.fr/public/DPClim/v1/commande/fichier'

# Adresse apis
ADRESS_SEARCH_URL = 'https://api-adresse.data.gouv.fr/search/'
REVERSE_ADRESS_URL = 'https://api-adresse.data.gouv.fr/reverse/'

# Files
WEATHER_STATION_LIST_PATH = 'datasets/weather-stations-list.csv'

# Date and time format
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
