

<center> <h1>Data Viz Challenge</h1> </center>

# General

[CHALLENGE](https://chaire-territoires.universita.corsica/article.php?id_site=73&id_art=7022&lang=fr)

[Ideas Document](https://docs.google.com/document/d/1goIOnfw7DgGOCrfaB56elmai3LYjU27jQNenf__UQvA/edit)

## Data

Supplementary info on what is inside /data/  folder:

### EDF - Mix Energetique 

- [eCorsicaWatt](https://opendata-corse.edf.fr/explore/dataset/ecorsicawatt/information/) 
- [Production d’électricité par filière et coûts de production au pas horaire ](https://opendata-corse.edf.fr/explore/dataset/production-d-electricite-par-filiere-et-couts-de-production-au-pas-horaire/)
- [Production annuelle d'électricité par filière](https://opendata-corse.edf.fr/explore/dataset/production-annuelle-delectricite-par-filiere/)
- [Consommation annuelle par commune](https://opendata-corse.edf.fr/explore/dataset/consommation-annuelle-par-commune0/)
- [Emissions annuelles de CO2](https://opendata-corse.edf.fr/explore/dataset/emissions-annuelles-de-c02/)
- [Capacités d'accueil du réseau](https://opendata-corse.edf.fr/explore/dataset/capacites-reseau/)
- Actions d'Efficacité Énergétique -> no url and even the one in F12 doesn't make sense, if we want it we must look for it 


### EDF - Reseaux

- [Lignes basse tension (BT souterrain)](https://opendata-corse.edf.fr/explore/dataset/lignes-basse-tension-bt-souterrain/)
- [Lignes basse tension (BT aérien)](https://opendata-corse.edf.fr/explore/dataset/lignes-basse-tension-bt-aerien/) 
- [Lignes haute tension (HTA souterrain)](https://opendata-corse.edf.fr/explore/dataset/lignes-haute-tension-hta-souterrain/)
- [Lignes haute tension (HTA aérien)](https://opendata-corse.edf.fr/explore/dataset/lignes-haute-tension-hta-aerien/)
- [Lignes haute tension (HTB souterrain)](https://opendata-corse.edf.fr/explore/dataset/lignes-haute-tension-htb-souterrain/)
- [Lignes haute tension (HTB aérien)](https://opendata-corse.edf.fr/explore/dataset/lignes-haute-tension-htb-aerien/)
- [Pylônes HTB](https://opendata-corse.edf.fr/explore/dataset/pylones-htb/) 
- [Postes sources](https://opendata-corse.edf.fr/explore/dataset/postes-sources/)
- [Lignes et postes électriques](https://opendata-corse.edf.fr/explore/dataset/lignes-et-postes-electriques/)

### METEO FRANCE 

- [API](https://portail-api.meteofrance.fr/web/en/) (need to create a free account)
-  [Niveaux de Vigilance](http://storage.gra.cloud.ovh.net/v1/AUTH_555bdc85997f4552914346d4550c421e/gra-vigi6-archive_public/) -> But Corsica is just split into 2 regions and then maybe not enough precise predictions
- Some python ressources:
  - [Pyhton Client Package](https://github.com/hacf-fr/meteofrance-api?tab=readme-ov-file)
  - [meteoviz-streamlit-app ](https://github.com/anquetos/meteoviz-streamlit-app)
  - [smOl query example](https://github.com/bflo/MeteoFranceAPIQuery/blob/main/MeteoFranceAPIQuery.ipynb)
- [Different datasets main page](https://donneespubliques.meteofrance.fr/?fond=rubrique&id_rubrique=30)

### Copernicus

- [API calls](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-europe-air-quality-forecasts?tab=form
)

# Goals

It is based on what we discussed today 11th of September, we can update / change it if you want.

- **(1)** Create an offline (no update with data stream) dashboard representing Corsica with its electricity network (from json data) and ONE natural hazard. Show whenever the electricity network is endangered. User could choose to display/hide the different types of networks nodes (Basse Tension / Haute Tension / Aerien / Souterrain - that shouldn't be a risk if we keep wind as natural hazards) and the natural hazards through buttons and so on.
- **(2)** Same, offline, but with Electricity Network + SEVERAL Natural Hazards
- **(3 - optional)** Retrieve data in real time using either Meteo France API or Copernicus API.  
- In parallel we can explore other possibilities of projects and do data exploration. 

