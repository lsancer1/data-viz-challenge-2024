# Lucas

## 11th of September

Pas de vocal pour l'instant :p

- J'ai surtout récupérer les données jsons edf en local et écrit les notes pour avoir une idée de notre objectif principal et des différentes étapes, et check un peu les codes qui utilisent l'API météo france.

- J'ai crée une branche pour moi mais pas encore utilisé, je vais mettre mes notes en main pour l'instant si c'est ok. J'ai fais un compte Graphana et Météo France API.

- On pourrait commencer à travailler sur des choses séparamment si on fait ce qu'il y a écrit dans **goals**.
   Je peux commencer à faire une map aveec les jsons du réseaux, voir comment récupérer des infos via météo france API (pour l'instant sans temps réel). Tu peux regarder comment récupérer des infos via Copernicus (j'ai pas du tout regardé ça). 
  On peux tout les deux regarder plotly dash et Graphana et choisir lequel des 2 on utilise (en gardant l'autre en plan B). 
  Il faudrait définir qui fait quoi. On peut chacun se concentrer sur un phénomène naturel que l'on choisit au début. Un de nous deux peut aussi même déjà penser à la visualization pourquoi pas même si c'est un peu prématuré 

## 17th of September
# Alberto
Jour 7. Toujours pas de vocal. Je crois que Lucas n'est plus. Il vivra toujours dans notre mémoire.

- J'ai une branche 'alberto' que j'ai alimenté avec un src/test.py qui permet de lancer un dashboard dash. Il suffit d'executer le fichier puis d'aller sur http://127.0.0.1:8050/ . Pour l'instant, j'ai récupèré les données des lignes aériennes des geojason, parsé, puis fait un scatter mapbox des données. J'ai mis deux tabs pour organiser un peu.
- J'ai un compte météo france qui marche. Pas essayé l'api encore.
- Ok je viens de lire. Je regarderai pour Copernicus alors.
- Pour la météo et EDF sur l'API il y a le vent moyent et les rafales. En plus on pourrait penser à utiliser :
a) pluie! ça peut inonder les sous stations et les lignes souterraines!
b) température! T élevées -> plus de conso electrique, surcharge des systèmes? A coupler avec les données de prod et conso peut être?
c) orages et foudre
d) feux, règle des 30 : T > 30 + Humidité < 30% + Vent > 30km/h -> risque important de feu. Les lignes aériennes peuvent générer des étincelles.
