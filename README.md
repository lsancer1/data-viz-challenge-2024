

<center> <h1>Data Viz Challenge</h1> </center>


# Open App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://data-viz-challenge-2024.streamlit.app/)

# Projet 

**Nom de l'équipe :** "Les risques corsés" 

Ce tableau de bord permet de visualiser à la fois des données météorologiques et des données d'un réseau électrique. L'utilisateur peut ainsi naviguer sur des cartes et être en mésure d'analyser les risques potentiels sur la Corse.

## Démonstration

Une vidéo de démonstration est disponible ci dessous :

[![Lien YouTube](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](A FAIRE)

## Utilisation

### En ligne

L'application est disponible sur le site de [StreamLit](https://data-viz-challenge-2024.streamlit.app/).

### Hors ligne

Il est aussi possible de cloner le dépôt et d'utiliser un serveur local.
Une fois le dépôt cloné sur la machine locale il faudra modifier les fichiers (Home.py et les fichiers dans le dossier Pages) en remplaçant la variable _currently_ par _local_ au lieu de _cloud_.

### Fonctionnement
![Home]

Page d'accueil.
L'utilisateur chosit sur le menu à gauche la visualisation à observer : "Air Quality", "Environmental Risk Forecast" ou "Electric Network".

![Air Quality]

L'utilisateur peut observer les données 2023 ou alors la prévision de qualité d'air dans la Corse.
Le mode _rax data_ affiche les données brutes et le mode _AQI data_ (pour Air Quality Index) affiche des données avec une estimation du risque pour la population.

![Environmental Risk Forecast]
L'utilisateur peut observer la prévision météorologique pour les prochaines heures en Corse et particulièrement : le vent, la pluie, l'humidité, la tempétature et la neige.
Une explication des risques potentiels est aussi affichée.

## Données utilisées

- Données météo Arome
- Données _dust_ Copernicus
- Lignes hautes tension et postes sources d'[EDF Corse](https://opendata-corse.edf.fr)

## Technologies utilisées

- **Visualisation et application** : [Streamlit](https://streamlit.io/)

- **Python**

## Membres de l'équipe

- **Lucas Sancéré** : Ingénieur et doctorant en bioinformatique

- **Alberto Alonso Pinar** : Ingénieur et doctorant en physique

