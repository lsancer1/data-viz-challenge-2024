#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 08:34:55 2024

@author: alonso-pinar_a
edit: lucas-sancere
"""

import streamlit as st

# Language translations dictionary
translations = {
    'Français': {
        'title': "# Bien le bonjour! 👋",
        'sidebar_message': "Veuillez choisir un onglet",
        'description': """
            Ce tableau de bord permet de visualiser quelques aspects liés aux risques
            en Corse. On a identifié deux risques majeurs :
            - Pollution de l'air (voir Air Quality)
            - Prévions météorologiques et risques (voir Environmental Risks Forecast)
            - Localisation des lignes du réseau électrique (voir Electric Network)

            👈 Dans la **barre latérale** on peut explorer un peu plus ces aspects!
        """,
    },
    'English': {
        'title': "# Welcome! 👋",
        'sidebar_message': "Please choose a dataset tab",
        'description': """
            This dashboard allows you to explore several aspects related to risks
            in Corsica. We have identified two major risks:
            - Air Quality
            - Environmental Risks Forecast 
            - Location of overhead power lines

            👈 In the **sidebar**, you can explore these aspects further!
        """,
    }
}

# Language selector in the sidebar
language = st.sidebar.selectbox("Select Language", ['Français', 'English'])

# Get the appropriate translations based on the selected language
current_lang = translations[language]

# Display content based on selected language
st.write(current_lang['title'])
st.sidebar.success(current_lang['sidebar_message'])

st.markdown(current_lang['description'])
