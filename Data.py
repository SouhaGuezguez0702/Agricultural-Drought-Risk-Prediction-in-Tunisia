"""
Script de collecte de donnees meteorologiques via NASA POWER API
Projet : Prediction de la Secheresse Agricole en Tunisie
Auteur : Souha Guezguez
"""

import requests
import pandas as pd
import time
import os

# ── Coordonnees GPS des 24 gouvernorats tunisiens ─────────────────────────
GOUVERNORATS = {
    "Tunis":         {"lat": 36.82, "lon": 10.17},
    "Ariana":        {"lat": 36.86, "lon": 10.19},
    "Ben Arous":     {"lat": 36.75, "lon": 10.22},
    "Manouba":       {"lat": 36.81, "lon": 10.10},
    "Nabeul":        {"lat": 36.45, "lon": 10.73},
    "Zaghouan":      {"lat": 36.40, "lon": 10.14},
    "Bizerte":       {"lat": 37.27, "lon": 9.87},
    "Beja":          {"lat": 36.73, "lon": 9.18},
    "Jendouba":      {"lat": 36.50, "lon": 8.78},
    "Kef":           {"lat": 36.18, "lon": 8.71},
    "Siliana":       {"lat": 36.09, "lon": 9.37},
    "Sousse":        {"lat": 35.83, "lon": 10.64},
    "Monastir":      {"lat": 35.78, "lon": 10.83},
    "Mahdia":        {"lat": 35.50, "lon": 11.06},
    "Sfax":          {"lat": 34.74, "lon": 10.76},
    "Kairouan":      {"lat": 35.67, "lon": 10.10},
    "Kasserine":     {"lat": 35.17, "lon": 8.83},
    "Sidi Bouzid":   {"lat": 35.03, "lon": 9.48},
    "Gabes":         {"lat": 33.88, "lon": 10.10},
    "Mednine":       {"lat": 33.35, "lon": 10.50},
    "Tataouine":     {"lat": 32.92, "lon": 10.45},
    "Gafsa":         {"lat": 34.43, "lon": 8.78},
    "Tozeur":        {"lat": 33.92, "lon": 8.13},
    "Kebili":        {"lat": 33.70, "lon": 8.97},
}

# ── Parametres NASA POWER ─────────────────────────────────────────────────
PARAMETRES = "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN"
# PRECTOTCORR       : Precipitations journalieres corrigees (mm/jour)
# T2M               : Temperature moyenne a 2m (degC)
# T2M_MAX           : Temperature max a 2m (degC)
# T2M_MIN           : Temperature min a 2m (degC)
# RH2M              : Humidite relative a 2m (%)
# WS2M              : Vitesse du vent a 2m (m/s)
# ALLSKY_SFC_SW_DWN : Rayonnement solaire (MJ/m2/jour)

DATE_DEBUT  = "20100101"   # 1er Janvier 2010
DATE_FIN    = "20231231"   # 31 Decembre 2023

# ── Fonction de telechargement pour un gouvernorat ───────────────────────
def telecharger_gouvernorat(nom, lat, lon, retries=3):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": PARAMETRES,
        "community":  "AG",
        "longitude":  lon,
        "latitude":   lat,
        "start":      DATE_DEBUT,
        "end":        DATE_FIN,
        "format":     "JSON"
    }

    for tentative in range(retries):
        try:
            print(f"  Telechargement : {nom} (lat={lat}, lon={lon})...")
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Extraire les parametres
            params_data = data["properties"]["parameter"]

            # Construire le DataFrame
            df = pd.DataFrame(params_data)
            df.index = pd.to_datetime(df.index, format="%Y%m%d")
            df.index.name = "date"
            df.reset_index(inplace=True)

            # Renommer les colonnes
            df.rename(columns={
                "PRECTOTCORR":        "precipitations_mm",
                "T2M":                "temperature_moy",
                "T2M_MAX":            "temperature_max",
                "T2M_MIN":            "temperature_min",
                "RH2M":               "humidite_pct",
                "WS2M":               "vent_ms",
                "ALLSKY_SFC_SW_DWN":  "rayonnement_solaire"
            }, inplace=True)

            # Ajouter colonnes gouvernorat et region
            df["gouvernorat"] = nom
            df["region"]      = attribuer_region(nom)
            df["latitude"]    = lat
            df["longitude"]   = lon

            # Remplacer valeurs aberrantes NASA (-999)
            df.replace(-999.0, pd.NA, inplace=True)

            print(f"  OK {nom} : {len(df)} lignes")
            return df

        except Exception as e:
            print(f"  Erreur tentative {tentative+1}/{retries} pour {nom} : {e}")
            time.sleep(5)

    print(f"  ECHEC pour {nom} apres {retries} tentatives")
    return None

# ── Attribuer region geographique ─────────────────────────────────────────
def attribuer_region(gouvernorat):
    nord = ["Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul",
            "Zaghouan", "Bizerte", "Beja", "Jendouba", "Kef", "Siliana"]
    centre = ["Sousse", "Monastir", "Mahdia", "Sfax",
              "Kairouan", "Kasserine", "Sidi Bouzid"]
    sud = ["Gabes", "Mednine", "Tataouine", "Gafsa", "Tozeur", "Kebili"]

    if gouvernorat in nord:   return "Nord"
    if gouvernorat in centre: return "Centre"
    if gouvernorat in sud:    return "Sud"
    return "Inconnu"

# ── Calcul de l'indice SPI (Standardized Precipitation Index) ─────────────
def calculer_spi(df, echelle_mois=3):
    """
    Calcule le SPI sur une echelle de X mois.
    SPI > -0.5  : Aucun risque (0)
    SPI > -1.0  : Secheresse moderee (1)
    SPI > -1.5  : Secheresse severe (2)
    SPI <= -1.5 : Secheresse extreme (3)
    """
    from scipy import stats

    df = df.copy()

    # Cumul mensuel par gouvernorat
    df["annee_mois"] = df["date"].dt.to_period("M")
    cumul_mensuel = (
        df.groupby(["gouvernorat", "annee_mois"])["precipitations_mm"]
        .sum()
        .reset_index()
    )
    cumul_mensuel.rename(columns={"precipitations_mm": "cumul_mensuel"}, inplace=True)

    # Rolling sum sur echelle_mois
    cumul_mensuel = cumul_mensuel.sort_values(["gouvernorat", "annee_mois"])
    cumul_mensuel["cumul_rolling"] = (
        cumul_mensuel.groupby("gouvernorat")["cumul_mensuel"]
        .transform(lambda x: x.rolling(echelle_mois, min_periods=echelle_mois).sum())
    )

    # Calcul SPI par gouvernorat
    def spi_par_groupe(groupe):
        valeurs = groupe["cumul_rolling"].dropna()
        if len(valeurs) < 10:
            groupe["spi"] = pd.NA
            return groupe
        # Fit distribution gamma
        shape, loc, scale = stats.gamma.fit(valeurs[valeurs > 0], floc=0)
        cdf = stats.gamma.cdf(groupe["cumul_rolling"].clip(lower=0.001),
                              shape, loc=loc, scale=scale)
        cdf = cdf.clip(0.001, 0.999)
        groupe["spi"] = stats.norm.ppf(cdf)
        return groupe

    cumul_mensuel = cumul_mensuel.groupby("gouvernorat", group_keys=False).apply(spi_par_groupe)

    # Classifier le risque
    def classifier_risque(spi):
        if pd.isna(spi): return pd.NA
        if spi > -0.5:   return 0   # Aucun risque
        elif spi > -1.0: return 1   # Modere
        elif spi > -1.5: return 2   # Severe
        else:            return 3   # Extreme

    cumul_mensuel["risque_secheresse"] = cumul_mensuel["spi"].apply(classifier_risque)

    return cumul_mensuel

# ── Script principal ──────────────────────────────────────────────────────
if __name__ == "__main__":

    os.makedirs("data", exist_ok=True)

    print("=" * 60)
    print("  Collecte des donnees NASA POWER — Tunisie")
    print(f"  Periode : {DATE_DEBUT} → {DATE_FIN}")
    print(f"  Gouvernorats : {len(GOUVERNORATS)}")
    print("=" * 60)

    tous_les_df = []

    for nom, coords in GOUVERNORATS.items():
        df_gouv = telecharger_gouvernorat(nom, coords["lat"], coords["lon"])
        if df_gouv is not None:
            tous_les_df.append(df_gouv)
        time.sleep(2)  # Pause pour ne pas surcharger l'API

    if not tous_les_df:
        print("\nAucune donnee recuperee. Verifie ta connexion internet.")
    else:
        # Fusionner tous les gouvernorats
        print("\nFusion de tous les gouvernorats...")
        df_final = pd.concat(tous_les_df, ignore_index=True)

        # Sauvegarder les donnees brutes
        df_final.to_csv("data/meteo_tunisie_brut.csv", index=False, encoding="utf-8")
        print(f"Donnees brutes sauvegardees : data/meteo_tunisie_brut.csv")
        print(f"  → {len(df_final)} lignes | {df_final['gouvernorat'].nunique()} gouvernorats")

        # Calculer le SPI et la variable cible
        print("\nCalcul de l'indice SPI (echelle 3 mois)...")
        df_spi = calculer_spi(df_final, echelle_mois=3)

        # Fusionner SPI avec donnees journalieres
        df_final["annee_mois"] = df_final["date"].dt.to_period("M")
        df_complet = df_final.merge(
            df_spi[["gouvernorat", "annee_mois", "cumul_mensuel",
                    "cumul_rolling", "spi", "risque_secheresse"]],
            on=["gouvernorat", "annee_mois"],
            how="left"
        )
        df_complet.drop(columns=["annee_mois"], inplace=True)

        # Sauvegarder le dataset final
        df_complet.to_csv("data/dataset_secheresse_tunisie.csv", index=False, encoding="utf-8")
        print(f"Dataset final sauvegarde : data/dataset_secheresse_tunisie.csv")
        print(f"  → {len(df_complet)} lignes | {df_complet.columns.tolist()}")

        # Apercu
        print("\n── Apercu des 5 premieres lignes ──")
        print(df_complet[["date", "gouvernorat", "region",
                           "precipitations_mm", "temperature_moy",
                           "spi", "risque_secheresse"]].head())

        # Statistiques de la variable cible
        print("\n── Repartition des classes de risque ──")
        print(df_complet["risque_secheresse"].value_counts().sort_index())

        print("\nCollecte terminee avec succes !")
        print("Tu peux maintenant ouvrir le notebook 01_EDA.ipynb")