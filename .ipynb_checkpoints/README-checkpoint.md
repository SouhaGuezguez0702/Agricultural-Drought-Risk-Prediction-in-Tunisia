# 🌾 Prédiction de la Sécheresse Agricole en Tunisie

> **Projet Machine Learning End-to-End** — 4ème cycle Data Science & IA — 2025/2026

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4-orange?style=flat-square&logo=scikit-learn)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?style=flat-square&logo=streamlit)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-green?style=flat-square)
![NASA POWER](https://img.shields.io/badge/NASA-POWER%20API-darkblue?style=flat-square)

---

## 📋 Table des matières

- [Contexte et problématique](#-contexte-et-problématique)
- [Dataset](#-dataset)
- [Pipeline ML](#-pipeline-ml)
- [Résultats des modèles](#-résultats-des-modèles)
- [Structure du dépôt](#-structure-du-dépôt)
- [Installation et lancement](#-installation-et-lancement)
- [Application Streamlit](#-application-streamlit)
- [Auteure](#-auteure)

---

## 🌍 Contexte et problématique

La Tunisie fait face à une **pression hydrique croissante** : les précipitations ont diminué de 20 à 30% en 40 ans selon l'INM, menaçant directement les cultures agricoles (blé, olivier, agrumes) qui constituent une part importante de l'économie rurale tunisienne.

### Question centrale

> *"À partir des données météorologiques historiques des 24 gouvernorats tunisiens, peut-on prédire avec précision le niveau de risque de sécheresse ?"*

### Objectifs

- ✅ Analyser les tendances climatiques historiques par région (Nord / Centre / Sud)
- ✅ Calculer l'indice **SPI** (Standardized Precipitation Index) comme variable cible
- ✅ Comparer 4 algorithmes de classification ML
- ✅ Déployer une interface web interactive avec carte de la Tunisie

---

## 📦 Dataset

| Propriété | Détail |
|-----------|--------|
| **Source principale** | [NASA POWER API](https://power.larc.nasa.gov) |
| **Source secondaire** | [data.gov.tn](https://catalog.data.gov.tn) |
| **Période** | 2010 — 2023 |
| **Gouvernorats** | 24 (couverture nationale complète) |
| **Observations** | 122 712 lignes |
| **Variables** | 14 features + 1 variable cible |
| **Variable cible** | `risque_secheresse` (0 à 3) |

### Variables principales

| Variable | Description | Type |
|----------|-------------|------|
| `precipitations_mm` | Précipitations journalières (mm) | Numérique |
| `temperature_moy` | Température moyenne à 2m (°C) | Numérique |
| `temperature_max` | Température maximale (°C) | Numérique |
| `temperature_min` | Température minimale (°C) | Numérique |
| `humidite_pct` | Humidité relative (%) | Numérique |
| `vent_ms` | Vitesse du vent (m/s) | Numérique |
| `precip_rolling_7j` | Moyenne mobile 7 jours | Numérique |
| `precip_rolling_30j` | Moyenne mobile 30 jours | Numérique |
| `saison` | Saison (1=Hiver, 2=Printemps, 3=Été, 4=Automne) | Catégorielle |
| `region_enc` | Région encodée (Nord/Centre/Sud) | Catégorielle |
| **`risque_secheresse`** | **Variable cible (0-3)** | **Binaire** |

### Construction de la variable cible (Indice SPI)

| Classe | Label | Condition SPI |
|--------|-------|--------------|
| 0 | 🟢 Aucun risque | SPI > -0.5 |
| 1 | 🟡 Sécheresse modérée | -1.0 < SPI ≤ -0.5 |
| 2 | 🟠 Sécheresse sévère | -1.5 < SPI ≤ -1.0 |
| 3 | 🔴 Sécheresse extrême | SPI ≤ -1.5 |

---

## ⚙️ Pipeline ML

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌────────────┐
│  Collecte   │───▶│     EDA      │───▶│  Preprocessing  │───▶│ Modélisation │───▶│ Évaluation │
│ NASA POWER  │    │ Visualisations│    │ Nettoyage       │    │ LR / DT      │    │ F1, Accuracy│
│ data.gov.tn │    │ Corrélations │    │ Encodage        │    │ RF / XGBoost │    │ Matrice     │
│             │    │ Outliers     │    │ Normalisation   │    │ GridSearch   │    │ Confusion   │
└─────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘    └────────────┘
```

### Étapes de preprocessing

- **Gestion des NaN** : Suppression des 3 premiers mois (nécessaires au calcul SPI)
- **Encodage** : LabelEncoder sur `region` et `gouvernorat`
- **Normalisation** : StandardScaler sur toutes les variables numériques
- **Déséquilibre** : `class_weight='balanced'` sur tous les modèles
- **Split** : 80% train / 20% test avec `random_state=42` et stratification

### Feature Engineering

- `precip_rolling_7j` : moyenne mobile des précipitations sur 7 jours
- `precip_rolling_30j` : moyenne mobile des précipitations sur 30 jours
- `amplitude_thermique` : température_max - température_min
- `jour_sec` : indicateur binaire (1 si précipitations = 0mm)
- `saison` : saison calculée à partir du mois

---

## 🏆 Résultats des modèles

| Modèle | Accuracy | F1-Score | Précision | Recall |
|--------|----------|----------|-----------|--------|
| Logistic Regression | 60.9% | 0.648 | 0.651 | 0.609 |
| Decision Tree | 70.5% | 0.735 | 0.741 | 0.705 |
| XGBoost | 80.0% | 0.777 | 0.780 | 0.800 |
| Random Forest | 83.0% | 0.836 | 0.840 | 0.830 |
| **RF Optimisé ✅** | **87.4%** | **0.873** | **0.876** | **0.874** |

### Meilleur modèle — Random Forest Optimisé

```python
RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced'
)
```

**Top 3 features les plus importantes :**
1. `precip_rolling_30j` — Moyenne précipitations 30 jours
2. `temperature_moy` — Température moyenne
3. `precip_rolling_7j` — Moyenne précipitations 7 jours

---

## 📁 Structure du dépôt

```
secheresse-agricole-tunisie/
│
├── 📁 notebooks/
│   ├── 📁 drafts/
│   │   ├── draft_01_exploration.ipynb
│   │   ├── draft_02_preprocessing.ipynb
│   │   └── draft_03_modelisation.ipynb
│   ├── 01_EDA.ipynb
│   ├── 02_Modeling.ipynb
│   └── notebook_final.ipynb
│
├── 📁 data/
│   └── dataset_secheresse_tunisie.csv
│
├── 📁 models/
│   ├── best_model.pkl
│   ├── scaler.pkl
│   ├── features.pkl
│   ├── le_region.pkl
│   └── le_gouvernorat.pkl
│
├── 📁 app/
│   ├── app.py
│   └── views/
│       ├── home.py
│       ├── carte.py
│       ├── prediction.py
│       ├── eda.py
│       ├── models.py
│       └── profile.py
│
├── 📁 src/
│   └── Data.py
│
├── 📄 README.md
├── 📄 Presentation.pdf
├── 📄 requirements.txt
└── 📄 .gitignore
```

---

## 🚀 Installation et lancement

### 1. Cloner le dépôt

```bash
git clone https://github.com/souha-guezguez/secheresse-agricole-tunisie.git
cd secheresse-agricole-tunisie
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Collecter les données

```bash
python src/Data.py
```

> ⏳ Le script télécharge les données de 24 gouvernorats via NASA POWER API (~5-10 min)

### 4. Lancer les notebooks

```bash
jupyter notebook notebooks/01_EDA.ipynb
jupyter notebook notebooks/02_Modeling.ipynb
```

### 5. Lancer l'application Streamlit

```bash
cd app
streamlit run app.py
```

> 🌐 L'application sera accessible sur `http://localhost:8501`

---

## 🌐 Application Streamlit

L'application web interactive comprend **6 pages** :

| Page | Description |
|------|-------------|
| 🏠 **Accueil** | Présentation du projet, KPIs, pipeline |
| 🗺️ **Carte interactive** | Carte Folium de la Tunisie avec niveau de risque par gouvernorat |
| 🔬 **Prédiction** | Formulaire de prédiction en temps réel |
| 📊 **Dashboard EDA** | Visualisations interactives avec filtres |
| 🏆 **Comparaison Modèles** | Tableau comparatif, radar chart, feature importance |
| 👤 **Mon Profil** | Informations utilisateur connecté |

**Identifiants de démonstration :**
```
admin   / admin123
souha   / souha2026
```

---

## 🛠️ Technologies utilisées

| Catégorie | Technologies |
|-----------|-------------|
| **Langage** | Python 3.9+ |
| **ML** | Scikit-learn, XGBoost |
| **Data** | Pandas, NumPy, SciPy |
| **Visualisation** | Matplotlib, Seaborn, Plotly |
| **Interface** | Streamlit, Folium, streamlit-folium |
| **Auth** | streamlit-authenticator, bcrypt |
| **API** | NASA POWER API, requests |

---

## 👩‍🎓 Auteure

**Souha Guezguez**
- 🎓 4ème cycle — Data Science & Intelligence Artificielle
- 📅 Année scolaire : 2025 / 2026
- 📧 souha.guezguez@etudiant.tn

---

## 📄 Licence

Ce projet est réalisé dans le cadre académique du cours de Machine Learning.

---

<div align="center">
  <sub>🌾 Fait avec ❤️ pour l'agriculture tunisienne</sub>
</div>
