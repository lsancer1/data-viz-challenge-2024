import pytest

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

import json
import requests
import time



# It's necessary to 
# - update APPLICATION_ID
# - update request_url at the end of the script

#############################################################
## Ressources
#############################################################

# https://github.com/hacf-fr/meteofrance-api/blob/master/tests/test_integrations.py
# https://github.com/anquetos/meteoviz-streamlit-app/blob/main/meteo_france.py
# https://portail-api.meteofrance.fr/web/en/faq 


#############################################################
## Token related
#############################################################

# unique application id : you can find this in the curl's command to generate jwt token 
ID_Sancere_2024_09_25 = 'aFpJT0dKNGg5TEozY2JaZWZmSTlPSWhZMjRnYTpMVFF5NFBDRWFrSkozOWFNb3IzYkVNZHl0elFh'

APPLICATION_ID = ID_Sancere_2024_09_25

# url to obtain acces token
TOKEN_URL = "https://portail-api.meteofrance.fr/token"

#Temporary token for test
# No need normally and dead after one hour
TOKEN = (
    'eyJ4NXQiOiJOelU0WTJJME9XRXhZVGt6WkdJM1kySTFaakZqWVRJeE4yUTNNalEyTkRRM09HRmtZalkzTURkbE9UZ3paakUxTURRNF' +
'ltSTVPR1kyTURjMVkyWTBNdyIsImtpZCI6Ik56VTRZMkkwT1dFeFlUa3paR0kzWTJJMVpqRmpZVEl4TjJRM01qUTJOR' +
'FEzT0dGa1lqWTNNRGRsT1RnelpqRTFNRFE0WW1JNU9HWTJNRGMxWTJZME13X1JTMjU2IiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJjNDdiOGI3MC00Y' +
'mIxLTQ4M2MtODg3Ni05ODEzYjAzMGI3NWQiLCJhdXQiOiJBUFBMSUNBVElPTiIsImF1ZCI6ImhaSU9HSjRoOUxKM2N' +
'iWmVmZkk5T0loWTI0Z2EiLCJuYmYiOjE3MjcyOTIzMjMsImF6cCI6ImhaSU9HSjRoOUxKM2NiWmVmZkk5T0loWTI0Z2' +
'EiLCJzY29wZSI6ImRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnJcL29hd' +
'XRoMlwvdG9rZW4iLCJleHAiOjE3MjcyOTU5MjMsImlhdCI6MTcyNzI5MjMyMywianRpIjoiOTYyODczMmYtZmNmZC00Z' +
'Dc2LTg3MzktNGZlMjE0NTk2ZjNkIiwiY2xpZW50X2lkIjoiaFpJT0dKNGg5TEozY2JaZWZmSTlPSWhZMjRnYSJ9.gN8kD' +
'j1gHMggiT7BTk4xelavHN8xEaqyW9AkxeUKB_oaBRuh1m7GPp8YFcdfzMOa4Do8Zn966_bzkeSWk1lsH6Lmd7jEUKrHP4' +
'qUwCipQ06aJEtLSOYyWrnxWvRaTrMwqEICki9Cn_XwaIyOphtfcjHnI66Mhydag0LAvc4ah8YcnLhoJ-QZ2FECEkIgjOS' +
'19t6-tFHKXREqmxU5jbH_O3pAHXsDd_km1YF-iSO3tFV5FA5qzoz5vJWoDie2FgHLFEa5X4NV2L_CN1FOtXe3OwkKg29Y' +
'XeDQEdGC9Ebq_E7LQbe5sXZuuPmnRJrFPLNOU8ceBzqwZxmqxrI82FR3eQ'
)



#############################################################
## Hard coded configs parameter
#############################################################

# for now we hard code to have the parameters :'p '

city = ["Bastia", "Ajaccio"]




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
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False, allow_redirects=False, headers=headers)
        token = access_token_response.json()['access_token']
        # Update session with fresh token
        self.session.headers.update({'Authorization': 'Bearer %s' % token})


    #### HERE
    # should start by a function more directly in the meteo france reco to see if the request works
    #### HERE


    # Place

    def search_places(
        self,
        search_query: str,
        latitude: str = None,
        longitude: str = None,
    ) -> Place:
        """Search the places (cities) linked to a query by name.

        You can add GPS coordinates in parameter to search places arround a given
        location.

        Args:
            search_query: A complete name, only a part of a name or a postal code (for
                France only) corresponding to a city in the world.
            latitude: Optional; Latitude in degree of a reference point to order
                results. The nearest places first.
            longitude: Optional; Longitude in degree of a reference point to order
                results. The nearest places first.

        Returns:
            A list of places (Place instance) corresponding to the query.
        """
        self.session.headers.update({'Accept': 'application/json'})
        # Construct the list of the GET parameters
        params = {"q": search_query}
        if latitude is not None:
            params["lat"] = latitude
        if longitude is not None:
            params["lon"] = longitude

        # Send the API resuest
        resp = self.request("GET", "https://api.meteofrance.fr/places", params=params)
        return [Place(place_data) for place_data in resp.json()]

    #
    # Observation
    #
    def get_observation(
        self,
        latitude: float,
        longitude: float,
        language: str = "fr",
    ) -> Observation:
        """Retrieve the weather observation for a given GPS location.

        Results can be fetched in french or english according to the language parameter.

        Args:
            latitude: Latitude in degree of the GPS point corresponding to the weather
                forecast.
            longitude: Longitude in degree of the GPS point corresponding to the weather
                forecast.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            An Observation instance.
        """
        resp = self.session.request(
            "get",
            "v2/observation",
            params={"lat": latitude, "lon": longitude, "lang": language},
        )
        return Observation(resp.json())

    def get_observation_for_place(
        self,
        place: Place,
        language: str = "fr",
    ) -> Observation:
        """Retrieve the weather observation for a given Place instance.

        Results can be fetched in french or english according to the language parameter.

        Args:
            place: Place class instance corresponding to a location.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            An Observation intance.
        """
        return self.get_observation(place.latitude, place.longitude, language)

    #
    # Forecast
    #
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        language: str = "fr",
    ) -> Forecast:
        """Retrieve the weather forecast for a given GPS location.

        Results can be fetched in french or english according to the language parameter.

        Args:
            latitude: Latitude in degree of the GPS point corresponding to the weather
                forecast.
            longitude: Longitude in degree of the GPS point corresponding to the weather
                forecast.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            A Forecast intance representing the hourly and daily weather forecast.
        """
        # TODO: add possibility to request forecast from id

        # Send the API request
        resp = self.session.request(
            "get",
            "forecast",
            params={"lat": latitude, "lon": longitude, "lang": language},
        )
        return Forecast(resp.json())

    def get_forecast_for_place(
        self,
        place: Place,
        language: str = "fr",
    ) -> Forecast:
        """Retrieve the weather forecast for a given Place instance.

        Results can be fetched in french or english according to the language parameter.

        Args:
            place: Place class instance corresponding to a location.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            A Forecast intance representing the hourly and daily weather forecast.
        """
        return self.get_forecast(place.latitude, place.longitude, language)

    #
    # Rain
    #
    def get_rain(self, latitude: float, longitude: float, language: str = "fr") -> Rain:
        """Retrieve the next 1 hour rain forecast for a given GPS the location.

        Results can be fetched in french or english according to the language parameter.

        Args:
            latitude: Latitude in degree of the GPS point corresponding to the rain
                forecast.
            longitude: Longitude in degree of the GPS point corresponding to the rain
                forecast.
            language: Optional; If language is equal "fr" (default value) results will
                be in French. All other value will give results in English.

        Returns:
            A Rain instance representing the next hour rain forecast.
        """
        # TODO: add protection if no rain forecast for this position

        # Send the API request
        resp = self.session.request(
            "get", "rain", params={"lat": latitude, "lon": longitude, "lang": language}
        )
        return Rain(resp.json())

    #
    # Warning
    #
    # def get_warning_current_phenomenoms(
    #     self, domain: str, depth: int = 0, with_coastal_bulletin: bool = False
    # ) -> CurrentPhenomenons:
    #     """Return the current weather phenomenoms (or alerts) for a given domain.

    #     Args:
    #         domain: could be `france` or any metropolitan France department numbers on
    #             two digits. For some departments you can access an additional bulletin
    #             for coastal phenomenoms. To access it add `10` after the domain id
    #             (example: `1310`).
    #         depth: Optional; To be used with domain = 'france'. With depth = 0 the
    #             results will show only natinal sum up of the weather alerts. If
    #             depth = 1, you will have in addition, the bulletin for all metropolitan
    #             France department and Andorre
    #         with_coastal_bulletin: Optional; If set to True (default is False), you can
    #             get the basic bulletin and coastal bulletin merged.

    #     Returns:
    #         A warning.CurrentPhenomenons instance representing the weather alert
    #         bulletin.
    #     """
    #     # Send the API request
    #     resp = self.session.request(
    #         "get",
    #         "v3/warning/currentphenomenons",
    #         params={"domain": domain, "depth": depth},
    #     )

    #     # Create object with API response
    #     phenomenoms = CurrentPhenomenons(resp.json())
    #     # if user ask to have the coastal bulletin merged
    #     if with_coastal_bulletin:
    #         if domain in COASTAL_DEPARTMENT_LIST:
    #             resp = self.session.request(
    #                 "get",
    #                 "v3/warning/currentphenomenons",
    #                 params={"domain": domain + "10"},
    #             )
    #             phenomenoms.merge_with_coastal_phenomenons(
    #                 CurrentPhenomenons(resp.json())
    #             )

    #     return phenomenoms

    # def get_warning_full(
    #     self, domain: str, with_coastal_bulletin: bool = False
    # ) -> Full:
    #     """Retrieve a complete bulletin of the weather phenomenons for a given domain.

    #     For a given domain we can access the maximum alert, a timelaps of the alert
    #     evolution for the next 24 hours, a list of alerts and other metadatas.

    #     Args:
    #         domain: could be `france` or any metropolitan France department numbers on
    #             two digits. For some departments you can access an additional bulletin
    #             for coastal phenomenoms. To access it add `10` after the domain id
    #             (example: `1310`).
    #         with_coastal_bulletin: Optional; If set to True (default is False), you can
    #             get the basic bulletin and coastal bulletin merged.

    #     Returns:
    #         A warning.Full instance representing the complete weather alert bulletin.
    #     """
    #     # TODO: add formatDate parameter

    #     # Send the API request
    #     resp = self.session.request(
    #         "get", "/v3/warning/full", params={"domain": domain}
    #     )

    #     # Create object with API response
    #     full_phenomenoms = Full(resp.json())

    #     # if user ask to have the coastal bulletin merged
    #     if with_coastal_bulletin:
    #         if domain in COASTAL_DEPARTMENT_LIST:
    #             resp = self.session.request(
    #                 "get",
    #                 "v3/warning/full",
    #                 params={"domain": domain + "10"},
    #             )
    #             full_phenomenoms.merge_with_coastal_phenomenons(Full(resp.json()))

    #     return full_phenomenoms

    # def get_warning_thumbnail(self, domain: str = "france") -> str:
    #     """Retrieve the thumbnail URL of the weather phenomenoms or alerts map.

    #     Args:
    #         domain: could be `france` or any metropolitan France department numbers on
    #             two digits.

    #     Returns:
    #         The URL of the thumbnail representing the weather alert status.
    #     """
    #     # Return directly the URL of the gif image
    #     return (
    #         f"{METEOFRANCE_API_URL}/v3/warning/thumbnail?&token={METEOFRANCE_API_TOKEN}"
    #         f"&domain={domain}"
    #     )

    # def get_warning_dictionary(self, language: str = "fr") -> WarningDictionary:
    #     """Retrieves the meteorological dictionary from the Météo-France API.

    #     This dictionary includes information about various meteorological
    #     phenomena and color codes used for weather warnings.

    #     Args:
    #         language (str): The language in which to retrieve the
    #             dictionary data. Default is 'fr' for French. Other language codes
    #             can be used if supported by the API.

    #     Returns:
    #         WarningDictionary: An object containing structured data about
    #             meteorological phenomena and warning color codes. It has two main
    #             attributes: 'phenomenons' (list of PhenomenonDictionaryEntry) and
    #             'colors' (list of ColorDictionaryEntry).
    #     """
    #     resp = self.session.request(
    #         "get", "v3/warning/dictionary", params={"lang": language}
    #     )
    #     dictionary = WarningDictionary(resp.json())
    #     return dictionary

    # #
    # # Picture of the day
    # #
    # def get_picture_of_the_day(self, domain: str = "france") -> PictureOfTheDay:
    #     """Retrieve the picture of the day image URL & description.

    #     Args:
    #         domain: could be `france`

    #     Returns:
    #         PictureOfTheDay instance with the URL and the description of the picture of
    #         the day.
    #     """
    #     # Send the API request
    #     # TODO: check if other value of domain are usable

    #     resp = self.session.request(
    #         "get",
    #         "v2/report",
    #         params={
    #             "domain": domain,
    #             "report_type": "observation",
    #             "report_subtype": "image du jour",
    #             "format": "txt",
    #         },
    #     )

    #     image_url = (
    #         f"{METEOFRANCE_API_URL}/v2/report"
    #         f"?domain={domain}"
    #         f"&report_type=observation&report_subtype=image%20du%20jour&format=jpg"
    #         f"&token={METEOFRANCE_API_TOKEN}"
    #     )

    #     return PictureOfTheDay({"image_url": image_url, "description": resp.text})






#############################################################
## Main
############################################################


def main():

    client = Client()
    # Issue a series of API requests an example.  For use this test, you must first subscribe to the arome api with your application
    client.session.headers.update({'Accept': 'application/json'})

    # Search a location from name.
    list_places = client.search_places(city)
    my_place = list_places[0]

    # Fetch weather forecast for the location
    my_place_weather_forecast = client.get_forecast_for_place(my_place)

    # Get the daily forecast
    my_place_daily_forecast = my_place_weather_forecast.daily_forecast

    # If rain in the hour forecast is available, get it.
    if my_place_weather_forecast.position["rain_product_available"] == 1:
        my_place_rain_forecast = client.get_rain(my_place.latitude, my_place.longitude)
        next_rain_dt = my_place_rain_forecast.next_rain_date_locale()
        if not next_rain_dt:
            rain_status = "No rain expected in the following hour."
        else:
            rain_status = next_rain_dt.strftime("%H:%M")
    else:
        rain_status = "No rain forecast available."

    # Fetch weather alerts.
    if my_place.admin2:
        my_place_weather_alerts = client.get_warning_current_phenomenoms(
            my_place.admin2
        )
        readable_warnings = readeable_phenomenoms_dict(
            my_place_weather_alerts.phenomenons_max_colors
            )


    # for i in range(100):
    #     response = client.request(
    #         'GET', 
    #         'https://public-api.meteofrance.fr/public/' + 
    #         'arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities?service=WMS&version=1.3.0', 
    #         verify=False)
    #     print(response.status_code)
    #     time.sleep(120)



    # assert isinstance(my_place_daily_forecast, list)
    # assert rain_status
    # assert isinstance(readable_warnings, dict)




if __name__ == '__main__':
    main()
