# Logbook

## October 18th

- https://stackoverflow.com/questions/22786068/how-to-avoid-http-error-429-too-many-requests-python
- Fill placeholder correctly now

### LAST guidelines from when I stop and when Alberto take over!

- fnezkfnz*
- fze

## October 16th

- **Proposed a planning for the final RUSH! See at the end of the file!**

- Log for the display of forecast map st.write(layermap)

  - request5000
  - change bbox paramters to have it directly as a string without bracket
  - request400
  - change bbox and height and width to correspond to provided examples
  - request200!!! works
  - to get image try request.content 
  - it is a bit more than that but got it

  

- Package problem:

```bash
INFO: pip is looking at multiple versions of meteofrance-api to determine which version is compatible with other requirements. This could take a while.

ERROR: Cannot install -r /mount/src/data-viz-challenge-2024/src/requirements.txt (line 42), -r /mount/src/data-viz-challenge-2024/src/requirements.txt (line 72) and urllib3==2.2.3 because these package versions have conflicting dependencies.

The conflict is caused by:

    The user requested urllib3==2.2.3

    requests 2.32.3 depends on urllib3<3 and >=1.21.1

    meteofrance-api 1.3.0 depends on urllib3<2.0.0 and >=1.26.18

To fix this you could try to:

1. loosen the range of package versions you've specified

2. remove package versions to allow pip attempt to solve the dependency conflict

ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts

[notice] A new release of pip is available: 24.0 -> 24.2

[notice] To update, run: pip install --upgrade pip

Checking if Streamlit is installed
```
- RESOLVED

- Test news settings in SUBLIME text to avoid having the indentation f****ing problem:

```yaml
	// Calculates indentation automatically when pressing enter
	"auto_indent": true,
	// true default 

	// Makes auto indent a little smarter, e.g., by indenting the next line
	// after an if statement in C. Requires auto_indent to be enabled.
	"smart_indent": false,
	// true default 
```

### TDL Next Day

- First, reorganize the display of Air Quality tab. After testing on 3 screens, the display per row is way better than per columns so change this. Keep a version of the code easy to access (no on github versionning but directly on a script) if Alberto wants to edit back. :heavy_check_mark:
- Second, finish the plan B maps with the Meteo France API
- **After this 2 points**, we restart working on plan A, meaning doing interactive maps. By ctrl + F the metadata with key "coverageID", I get it will be possible to extract value for temp, wind and so on from WCS.

## October 11th

- https://discuss.streamlit.io/t/manage-app-button-has-disappeared/43915/11 
- https://discuss.streamlit.io/t/manage-app-button-has-disappeared/43915/11 
- s**sh-add ~/.ssh/id_ed25519** NEED TO ADD THE SSH KEY !!‚

## October 9th

- Use prints and manage app to debug!!

- Need to create 2 ssh configs to push now from the laptop..

  ```bash
  # Configuration for the first account (lucas-sancere)
  Host github-lucas-sancere
    AddKeysToAgent yes
    UseKeychain yes
    HostName github.com
    User git
    IdentityFile ~/.ssh/key-bozekmac-1
  
  # Configuration for the second account (lsancer1)
  Host github-lsancer1
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
  ```

- maybe the solution of all my problems: https://stackoverflow.com/questions/47770917/sublime-text-3-misinterpreting-indentation-when-code-is-pasted 

- https://forum.sublimetext.com/t/inconsistent-indentation-in-python/64637/2

#### Env additions

- pip install streamlit
- pip install cdsapi 

#### List of bugs in the Air Quality tab for now

- Raw data view text on the right column is not changing when selecting AQI data 
- Names of menu options are only in English (January, Dust and so on)
- Forecast not working because token needs to be added  :heavy_check_mark:
- Get data not displaying anything

#### TDL Next Day

- Define the planning of the week left...
- Focus on the new tab and make the thing coherent in french 
- Don't focus on forecast data from copernic before having all the rest done. It can eitherr be fixed by Alberto or removed fully. 

## October 4th

- [Streamlit Secrets management](https://docs.streamlit.io/develop/concepts/connections/secrets-management)
- [Create a multipage app](https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app)

- id_ed25519

## September 29th

- Never checkout from dev-lucas branch as going back to this take a long time. Edit the main branch directly in the browser
- Able to make a request to API working, now we can focus on extracted the data we want
- Corsica coordinates:
  - "area": [43.25, 8.15, 41.15, 10.15]
  - max latitude; min longitude; min latitude: max longitude

#### TDL Next Day

- We focus on creating a streamlit tab that we can discuss next thursday with Alberto. So first create the tabe with the Corsica map, second insert the poles data there, third try to export the observation/forecast. Forecast makes more sense but check if it is hard or not to work with the forecast and if we can have the tings usufull for the rule of 30.

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

## 18th September 

- not able to do much in 1h30 , need to start at the latest at 18h30 on Wednesdays.... :'(

- Play with Alberto code and set my repo in a proper way, conda env, configs, utils.

- Defining guideline and propositon to split work on shared notes 

- Shared notes

  One should care about the reseaux data fully and the implementation in dashboard, then we split the environmental risks between us 2. We should define tasks from now. 

  Peut etre faire un tableau avec, Données Réseaux Affichées, API pour données Environmentale, Données Environmentale, Seuil d'alerte, Niveau de Guidelines. 

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

# Schedule for final rush

- The night of the 17/18 before going to sleep, check the constraints and all what need to do another time to sned the application 
- The 18th Before 10h GER / 18h AUS, work on the app
- AT 10h GER / 18h AUS STOP working on the app, create a copy of the repo and archive it in private, delete all the commits of the repo, create a README with explanations for the app, do the small video they are asking for
- AT 11h GER / 19h AUS send everything qnd follow requirements

# Schedule 

- **11th, 18h30**
- **18th, 21h00**
- **25th, 18h30**
- **29th, 12h30** 
- **04th, 21h00**
- **09th, 18h30**
- **11th very short**
- **16th, 15h30**
- **17th 18h**
- **18h MONRING**
