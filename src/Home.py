#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 08:34:55 2024

@author: alonso-pinar_a
"""

import streamlit as st


st.write("# Bien le bonjour! 👋")
st.sidebar.success("Veuillez choisir une donnée:")

st.markdown(
    """
    Ce tableau de bord permet de visualiser quelques aspects liés aux risques
    en Corse.
    On a identifié deux risques majeurs :
    - Pollution de l'air
    - Risques du réseau électrique 

    👈 Dans la **barre latérale** on peut explorer un peu plus ces aspects!

"""
)
