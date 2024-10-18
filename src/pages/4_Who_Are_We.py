#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 08:34:55 2024

@authors: alonso-pinar_a, lucas-sancere
"""

import streamlit as st


# Language translations dictionary
translations = {
    'Français': {
        'title': "# Qui sommes nous?",
        'description': """
        Nous sommes deux amis de longue date et doctorants!

        Lucas aime apprendre le nom de toutes les subdivisions des pays d'Amérique,

        Alberto aime le vélo et les figues,

        Nous contacter:
        - lsancer1@smail.uni-koeln.de
        """,
    },
    'English': {
        'title': "# Who are we?",
        'description': """
        We are two long-time friends and doctoral students!

        Lucas loves learning the names of all the subdivisions of American countries,
        
        Alberto enjoys cycling and figs.
        
        Contact us:
        - lsancer1@smail.uni-koeln.de
        """,
    }
}

# Language selector in the sidebar
language = st.sidebar.selectbox("Select Language", ['Français', 'English'])

# Get the appropriate translations based on the selected language
current_lang = translations[language]

# Display content based on selected language
st.write(current_lang['title'])

st.markdown(current_lang['description'])


st.image("https://i.imgur.com/jCQC1cT.png", caption="Nous...", width=400)
