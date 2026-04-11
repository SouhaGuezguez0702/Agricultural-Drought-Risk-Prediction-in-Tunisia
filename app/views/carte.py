import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# Coordonnées des gouvernorats
GOUVERNORATS_COORDS = {
    "Tunis":       (36.82, 10.17), "Ariana":      (36.86, 10.19),
    "Ben Arous":   (36.75, 10.22), "Manouba":     (36.81, 10.10),
    "Nabeul":      (36.45, 10.73), "Zaghouan":    (36.40, 10.14),
    "Bizerte":     (37.27,  9.87), "Beja":        (36.73,  9.18),
    "Jendouba":    (36.50,  8.78), "Kef":         (36.18,  8.71),
    "Siliana":     (36.09,  9.37), "Sousse":      (35.83, 10.64),
    "Monastir":    (35.78, 10.83), "Mahdia":      (35.50, 11.06),
    "Sfax":        (34.74, 10.76), "Kairouan":    (35.67, 10.10),
    "Kasserine":   (35.17,  8.83), "Sidi Bouzid": (35.03,  9.48),
    "Gabes":       (33.88, 10.10), "Medenine":    (33.35, 10.50),
    "Tataouine":   (32.92, 10.45), "Gafsa":       (34.43,  8.78),
    "Tozeur":      (33.92,  8.13), "Kebili":      (33.70,  8.97),
}

RISK_COLORS  = {0: "#2ecc71", 1: "#f1c40f", 2: "#e67e22", 3: "#e74c3c"}
RISK_LABELS  = {0: "Aucun risque", 1: "Modéré", 2: "Sévère", 3: "Extrême"}
RISK_ICONS   = {0: "🟢", 1: "🟡", 2: "🟠", 3: "🔴"}

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('../data/dataset_secheresse_tunisie.csv', parse_dates=['date'])
        df['risque_secheresse'] = pd.to_numeric(df['risque_secheresse'], errors='coerce')
        df = df.dropna(subset=['risque_secheresse'])
        df['risque_secheresse'] = df['risque_secheresse'].astype(int)
        df['annee'] = df['date'].dt.year
        df['mois']  = df['date'].dt.month
        return df
    except:
        return None

def render():
    st.markdown("""
    <div class="card-green" style="padding:24px 28px; margin-bottom:20px;">
        <h1 style="color:white; margin:0 0 6px; font-size:1.8rem;">
            🗺️ Carte Interactive — Risque de Sécheresse
        </h1>
        <p style="opacity:0.65; margin:0; font-size:0.9rem;">
            Visualisation du niveau de risque par gouvernorat tunisien
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df is None:
        st.error("Fichier dataset_secheresse_tunisie.csv introuvable dans data/")
        return

    # Filtres
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        annees = sorted(df['annee'].unique())
        annee  = st.selectbox("Année", annees, index=len(annees)-1)
    with col_f2:
        mois_noms = {1:"Janvier",2:"Février",3:"Mars",4:"Avril",5:"Mai",6:"Juin",
                     7:"Juillet",8:"Août",9:"Septembre",10:"Octobre",11:"Novembre",12:"Décembre"}
        mois = st.selectbox("Mois", list(mois_noms.keys()),
                            format_func=lambda x: mois_noms[x], index=6)
    with col_f3:
        region_filtre = st.selectbox("Région", ["Toutes", "Nord", "Centre", "Sud"])

    # Filtrer les données
    df_f = df[(df['annee'] == annee) & (df['mois'] == mois)]
    if region_filtre != "Toutes":
        df_f = df_f[df_f['region'] == region_filtre]

    # Risque moyen par gouvernorat
    risque_gouv = (
        df_f.groupby('gouvernorat')['risque_secheresse']
        .mean().round().astype(int)
        .reset_index()
    )

    col_map, col_stats = st.columns([2, 1])

    with col_map:
        # Carte Folium
        m = folium.Map(
            location=[34.0, 9.5],
            zoom_start=6,
            tiles='CartoDB positron'
        )

        for _, row in risque_gouv.iterrows():
            gouv = row['gouvernorat']
            risk = row['risque_secheresse']
            if gouv in GOUVERNORATS_COORDS:
                lat, lon = GOUVERNORATS_COORDS[gouv]
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=18,
                    color=RISK_COLORS[risk],
                    fill=True,
                    fill_color=RISK_COLORS[risk],
                    fill_opacity=0.75,
                    popup=folium.Popup(
                        f"<b>{gouv}</b><br>"
                        f"Risque : {RISK_ICONS[risk]} {RISK_LABELS[risk]}<br>"
                        f"Classe : {risk}",
                        max_width=200
                    ),
                    tooltip=f"{gouv} — {RISK_LABELS[risk]}"
                ).add_to(m)

                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:9px; font-weight:bold; '
                             f'color:white; text-align:center; '
                             f'margin-top:-6px;">{gouv[:4]}</div>',
                        icon_size=(40, 20),
                        icon_anchor=(20, 0)
                    )
                ).add_to(m)

        # Légende
        legend = """
        <div style='position:fixed; bottom:30px; left:30px; z-index:1000;
                    background:white; padding:12px 16px; border-radius:10px;
                    box-shadow:0 2px 10px rgba(0,0,0,0.15); font-size:12px;'>
            <b>Niveau de risque</b><br>
            <span style='color:#2ecc71;'>●</span> Aucun risque<br>
            <span style='color:#f1c40f;'>●</span> Modéré<br>
            <span style='color:#e67e22;'>●</span> Sévère<br>
            <span style='color:#e74c3c;'>●</span> Extrême
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend))

        st_folium(m, width=700, height=500)

    with col_stats:
        st.markdown(f"""
        <div class="card" style="padding:16px;">
            <div style="font-weight:700; color:#1b4332; margin-bottom:12px;">
                📅 {mois_noms[mois]} {annee}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Comptage par classe
        for risk in [0, 1, 2, 3]:
            n = len(risque_gouv[risque_gouv['risque_secheresse'] == risk])
            if n > 0:
                st.markdown(f"""
                <div style='display:flex; align-items:center; gap:10px;
                            padding:10px 14px; margin-bottom:8px;
                            background:{"#d8f3dc" if risk==0 else "#fff3cd" if risk==1 else "#ffe5cc" if risk==2 else "#fde8e8"};
                            border-radius:10px;'>
                    <span style='font-size:1.2rem;'>{RISK_ICONS[risk]}</span>
                    <div>
                        <div style='font-weight:600; font-size:0.85rem;
                                    color:{"#1b4332" if risk==0 else "#856404" if risk==1 else "#b54708" if risk==2 else "#c0392b"}'>
                            {RISK_LABELS[risk]}
                        </div>
                        <div style='font-size:0.75rem; color:#888;'>
                            {n} gouvernorat{"s" if n>1 else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**Gouvernorats les plus à risque :**")
        top = risque_gouv.sort_values('risque_secheresse', ascending=False).head(5)
        for _, row in top.iterrows():
            r = int(row['risque_secheresse'])
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between;
                        padding:6px 0; border-bottom:1px solid #f5f5f5;
                        font-size:0.85rem;'>
                <span>{row['gouvernorat']}</span>
                <span>{RISK_ICONS[r]}</span>
            </div>
            """, unsafe_allow_html=True)
