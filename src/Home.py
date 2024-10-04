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
    'français': {
        'title': "# Bien le bonjour! 👋",
        'sidebar_message': "Veuillez choisir une donnée:",
        'description': """
            Ce tableau de bord permet de visualiser quelques aspects liés aux risques
            en Corse. On a identifié deux risques majeurs :
            - Pollution de l'air
            - Risques du réseau électrique

            👈 Dans la **barre latérale** on peut explorer un peu plus ces aspects!
        """,
    },
    'english': {
        'title': "# Hello, welcome! 👋",
        'sidebar_message': "Please choose a dataset:",
        'description': """
            This dashboard allows you to explore several aspects related to risks
            in Corsica. We have identified two major risks:
            - Air pollution
            - Electrical grid risks

            👈 In the **sidebar**, you can explore these aspects further!
        """,
    }
}

# Language selector in the sidebar
language = st.sidebar.selectbox("Select Language", ['français', 'english'])

# Get the appropriate translations based on the selected language
current_lang = translations[language]

# Display content based on selected language
st.write(current_lang['title'])
st.sidebar.success(current_lang['sidebar_message'])

st.markdown(current_lang['description'])
