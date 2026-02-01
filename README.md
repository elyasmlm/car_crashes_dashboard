# Dashboard des accidents de la route en France (2005–2024)

## Auteurs
- **MALOUM Elyas**
- **GUERREIRO Noah**

**Formation :** E3FI — Année universitaire 2025–2026

## Objectif du projet

L’objectif de ce projet est d’éclairer un sujet d’intérêt public : **la sécurité routière en France**.  
À partir de données publiques, nous analysons les accidents de la route sur la période de **2005 à 2024**, afin de mettre en évidence des tendances et de sensibiliser les usagers de la route.

Le projet prend la forme d’un dashboard interactif développé en Python, accessible depuis un navigateur web.

## Guide utilisateur

### Prérequis
- Python **3.11 ou supérieur**
- Un navigateur web standard (Chrome, Firefox, Edge…)

### Installation

```bash
git clone https://github.com/elyasmlm/car_crashes_dashboard.git
cd car_crashes_dashboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Lancement du dashboard

```bash
python main.py
```

Le dashboard est accessible à l’adresse indiquée dans la console (par défaut http://127.0.0.1:8050).

## Fonctionnalités du dashboard
Le dashboard est composé de deux pages :

### Page Carte interactive
Carte géolocalisée des accidents en France

Visualisation des zones à forte concentration d’accidents

Localisation de l’accident le plus proche de l’utilisateur à partir de sa position géographique

### Page Analyses statistiques
#### Histogrammes :

- Nombres d'accidents par rapport à la luminosité

- Nombres d'accidents par rapport aux conditions météorologiques

- Nombres d'accidents par rapport aux différentes heures de la journée

- Âge des accidentés

#### Camemberts :

- Répartition des accidents par saison

- Répartition des accidents par  types de collision

- Répartition des accidents par gravité des conséquences (indemnes, blessés, tués)

- Répartition des accidents par types de véhicules impliqués

#### Courbe d’évolution du nombre d’accidents par année

#### Navigation par carrousels (sliders) pour parcourir les graphiques

#### Les graphiques sont interactifs (zoom, survol, navigation dynamique).

## Données
### Source des données
Les données proviennent de la plateforme officielle data.gouv.fr :

https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023

Bien que la page indique 2005–2023, les données 2024 sont également intégrées au projet.

### Nature des données
Données statiques

Fichiers CSV

Données Open Data librement réutilisables

### Organisation des données
data/raw/ : données brutes téléchargées

data/cleaned/ : données nettoyées et consolidées

Le nettoyage et la fusion des données sont réalisés à l’aide de clean_data.py.

## Guide pour développeur

### Architecture du projet

#### Architecture des fichiers et dossiers principaux

```mermaid
├── main.py
├── requirements.txt
├── README.md
├── pyproject.toml
├── data/
│   ├── raw/
│   └── cleaned/
├── src/
│   ├── components/
│   │   ├── camembert/
│   │   ├── evolution/
│   │   ├── gridmap/
│   │   └── histogramme/
│   ├── pages/
│   │   ├── gridmap.py
│   │   └── home.py
│   └── utils/
│       ├── clean_data.py
│       ├── data_loader.py
│       └── get_data.py
└── video_demo.mp4
```

### Qualité du code
Code structuré en modules et fonctions

Variables explicites, docstrings et typage

Respect des bonnes pratiques Python

Un **linter** est utilisé pour analyser statiquement le code et détecter :
- les erreurs potentielles,
- les imports inutilisés,
- les incohérences de style,
- les mauvaises pratiques courantes.

### Linter utilisé : Ruff

Ruff permet notamment :
- de vérifier la conformité du code aux conventions Python,
- d’unifier la gestion des imports,
- d’améliorer la qualité globale du code.

### Utilisation de Ruff

#### Installation via requirements.txt comme vu au début du README.md.

Analyse du code : 

```bash
ruff check src
```

La plupart de nos petites erreurs ont pu être corrigés via cette commande : 

```bash
ruff check src --fix
```

Pour les autres nous les avons fixés à la main.

#### La configuration de Ruff est définie dans le fichier pyproject.toml à la racine du projet.

## Rapport d’analyse

### Les principales conclusions issues des analyses sont :

- Les jeunes conducteurs sont fortement surreprésentés dans les accidents.

- Les accidents surviennent majoritairement aux heures de pointe.

- Sur le long terme, le nombre d’accidents diminue globalement, malgré une légère remontée récente.

- Les accidents sont fortement concentrés sur les grands axes routiers (autoroutes, périphériques).

- Contrairement aux idées reçues, la majorité des accidents ont lieu en plein jour, avec une météo normale, et les saisons influencent peu (par exemple il n'y a pas plus d'accidents en hiver même avec la nuit plus tôt ou la météo parfois rude).

### Ces résultats soulignent l’importance de la prévention routière, en particulier auprès des jeunes conducteurs et sur les axes rapides.

## Vidéo de démonstration
Une vidéo de démonstration du dashboard est fournie dans le dépôt :

video_demo.mp4
