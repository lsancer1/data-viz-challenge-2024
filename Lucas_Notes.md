# Logbook

## 11th of September

- create main notes with data links and goals :heavy_check_mark:
- check structre of electric network json :heavy_check_mark:
- check   plotly  dash  Graphana  :heavy_check_mark:
- check example of code using METEO FRANCE API :heavy_multiplication_x:
- define maybe work laod to split and writte shared notes 
- no time to start python script as it is already 22:30

## Structres of Networks Json

Pretty basic. The GeoJson files don't have extra information.

- Postes Electriques:

![ScreenShot](/docs/lscreenshots/struct-lignes-et-postes-electriques.png)

- Pylones and Postes have the same type:

![ScreenShot](/docs/lscreenshots/struct-pylones-htb.png)

- Lignes, not check comprehensively but I feel like they have same structures except the geometry string values

![ScreenShot](/docs/lscreenshots/struct-lignes-haute-tension-htb-aerien.png)

### TDL Next Time

- [Dash 20min tutorial](https://dash.plotly.com/tutorial) and or  Graphana basic tuto such as [fundamentals docs](https://grafana.com/docs/grafana/latest/fundamentals/) or [Getting started with Grafana dashboard design](https://grafana.com/go/webinar/getting-started-with-grafana-dashboard-design/?pg=videos&plcmt=ondemand) from the webinar section [here](https://grafana.com/videos/) -> WE START WITH DASH 
- Start to retrieve basic info from METEO FRANCE
- Import jsons data and plot all points in a Cosrica map - check what the coordinates correspond to :heavy_check_mark:
- Whenever we will have different "maps" layout we will need to deal with coordinates system that can vary SEE IN FUTURE 
- Should start to have "clear" idea of who do what :heavy_check_mark:

## 18th September 

- not able to do much in 1h30 , need to start at the latest at 18h30 on Wednesdays.... :'(

- Play with Alberto code and set my repo in a proper way, conda env, configs, utils.

- Defining guideline and propositon to split work on shared notes 

- Shared notes

  One should care about the reseaux data fully and the implementation in dashboard, then we split the environmental risks between us 2. We should define tasks from now. 

  Peut etre faire un tableau avec, Données Réseaux Affichées, API pour données Environmentale, Données Environmentale, Seuil d'alerte, Niveau de Guidelines. 

## 25th September

- for the retrieval informal part we will focus on the 30 rule:

| Données Réseaux Affichées | API pour données Environnementales | Données Environnementales   | Seuil d'alerte                             | Autres       |
| ------------------------- | ---------------------------------- | --------------------------- | ------------------------------------------ | ------------ |
| Hta et Htb aérien         | Météo France                       | Température, Humidité, Vent | T > 30°C + Humidité < 30% + Vent > 30 km/h | ------------ |

and Alberto will tackle other natural hazards and their impacts. I focujs on this hazard and on making the dashboard look pretty. 

- Program: 
  - start on checking METEO FRANCE API , writte first code
  - approaching to the end continue with making dashbpard pretty
  - notes and leave
  - leave at 10h30PM (first 9h40, 10h10, 10h30)
- alias ll="ls -l -G"
- [How to use the API - generate token](https://portail-api.meteofrance.fr/web/en/faq)
- List of APIs I susbscribed to [portal](https://portail-api.meteofrance.fr/web/fr)  then my account then My API
- Work on `forecast_requests.py` need to make it work for next time -> wee directly focus on real time
- All the important ressources are in the beginning of the code

#### Meteo France API

Name: **lucas.sancere**

mdp: shortversion

#### TDL Next Day

- Continue to work on  `forecast_requests.py`
- Work on making the dashboard nicer (starting with blackbackground)

## September 29th

- Never checkout from dev-lucas branch as going back to this take a long time. Edit the main branch directly in the browser
- Able to make a request to API working, now we can focus on extracted the data we want
- Corsica coordinates:
  - "area": [43.25, 8.15, 41.15, 10.15]
  - max latitude; min longitude; min latitude: max longitude

#### TDL Next Day

- We focus on creating a streamlit tab that we can discuss next thursday with Alberto. So first create the tabe with the Corsica map, second insert the poles data there, third try to export the observation/forecast. Forecast makes more sense but check if it is hard or not to work with the forecast and if we can have the tings usufull for the rule of 30.

# Schedule

- **11th, 18h30**
- **18th, 21h00**
- **25th, 18h30**
- **29th, 12h30** 
- 02nd, 18h30
- 09th, 18h30
- _After the session of the 09, define extension work_
- 11th 18h30
- _Optional Extensions from 12 to 16_
- 16th, 18h30
