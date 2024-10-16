#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 08:34:55 2024

@authors: alonso-pinar_a, lucas-sancere
"""

import streamlit as st


import json
from utils.json_manager import extract_rescoordinates
from io import StringIO
from meteofrance_api import MeteoFranceClient
from meteofrance_api.helpers import readeable_phenomenoms_dict
from meteofrance_api import client
import constants
import csv 
import requests
import time




#############################################################
## Token related
#############################################################


APPLICATION_ID = st.secrets['ID_Sancere_2024_09_25']
TOKEN_URL = st.secrets['MF_TOKEN_URL']



####################################
# Create Client 
####################################


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




####################################
# Main 
####################################


client = Client()

wcs_exploration = client.get_wcs_metadata()















