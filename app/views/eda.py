import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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

RISK_COLORS = {0:"#2ecc71", 1:"#f1c40f", 2:"#e67e22", 3:"#e74c3c"}
RISK_LABELS = {0:"Aucun", 1:"Modéré", 2:"Sévère", 3:"Extrême"}

def render():
    st.markdown("""
    <div class="card-green" style="padding:24px 28px; margin-bottom:20px;">
        <h1 style="color:white; margin:0 0 6px; font-size:1.8rem;">
            📊 Dashboard EDA
        </h1>
        <p style="opacity:0.65; margin:0; font-size:0.9rem;">
            Analyse Exploratoire — 24 gouvernorats tunisiens (2010–2023)
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df is None:
        st.error("Fichier dataset introuvable dans data/")
        return

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    for col, (val, lbl) in zip([c1,c2,c3,c4], [
        (f"{len(df):,}", "Observations"),
        (f"{df['gouvernorat'].nunique()}", "Gouvernorats"),
        (f"{df['annee'].min()}–{df['annee'].max()}", "Période"),
        (f"{df['precipitations_mm'].mean():.2f} mm", "Précip. moy.")
    ]):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:16px 10px;">
                <div class="metric-val" style="font-size:1.5rem;">{val}</div>
                <div class="metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    # Filtres
    with st.expander("🎛️ Filtres", expanded=False):
        fc1, fc2 = st.columns(2)
        with fc1:
            annees = sorted(df['annee'].unique())
            annee_range = st.slider("Période", int(annees[0]), int(annees[-1]),
                                    (int(annees[0]), int(annees[-1])))
        with fc2:
            regions = st.multiselect("Régions", ["Nord","Centre","Sud"],
                                     default=["Nord","Centre","Sud"])

    df_f = df[
        (df['annee'].between(*annee_range)) &
        (df['region'].isin(regions))
    ]
    st.caption(f"📌 {len(df_f):,} observations après filtres")

    # Row 1
    col1, col2 = st.columns(2)

    with col1:
        counts = df_f['risque_secheresse'].value_counts().sort_index()
        fig = px.pie(
            values=counts.values,
            names=[RISK_LABELS[i] for i in counts.index],
            color_discrete_sequence=[RISK_COLORS[i] for i in counts.index],
            hole=0.5,
            title="Répartition des classes de risque"
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(paper_bgcolor="white", font_family="Source Sans 3",
                          title_font_size=13, margin=dict(t=40,b=10),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            df_f, x="precipitations_mm", nbins=60,
            color="region",
            color_discrete_map={"Nord":"#3498db","Centre":"#e67e22","Sud":"#e74c3c"},
            barmode="overlay", opacity=0.7,
            title="Distribution des précipitations par région"
        )
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font_family="Source Sans 3", title_font_size=13,
                          margin=dict(t=40,b=10),
                          xaxis_title="Précipitations (mm)", yaxis_title="Fréquence")
        st.plotly_chart(fig, use_container_width=True)

    # Row 2
    col3, col4 = st.columns(2)

    with col3:
        fig = px.box(
            df_f, x="region", y="precipitations_mm",
            color="region",
            color_discrete_map={"Nord":"#3498db","Centre":"#e67e22","Sud":"#e74c3c"},
            category_orders={"region":["Nord","Centre","Sud"]},
            title="Précipitations par région"
        )
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font_family="Source Sans 3", title_font_size=13,
                          margin=dict(t=40,b=10), showlegend=False,
                          xaxis_title="Région", yaxis_title="Précipitations (mm)")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        mois_noms = ["Jan","Fév","Mar","Avr","Mai","Jun",
                     "Jul","Aoû","Sep","Oct","Nov","Déc"]
        saison_data = df_f.groupby(['mois','region'])['precipitations_mm'].mean().reset_index()
        fig = px.line(
            saison_data, x="mois", y="precipitations_mm", color="region",
            color_discrete_map={"Nord":"#3498db","Centre":"#e67e22","Sud":"#e74c3c"},
            markers=True, title="Saisonnalité des précipitations"
        )
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font_family="Source Sans 3", title_font_size=13,
                          margin=dict(t=40,b=10),
                          xaxis=dict(tickvals=list(range(1,13)), ticktext=mois_noms),
                          xaxis_title="Mois", yaxis_title="Précip. moy. (mm)")
        st.plotly_chart(fig, use_container_width=True)

    # Row 3 — Évolution temporelle
    cumul = df_f.groupby(df_f['date'].dt.to_period('M').dt.to_timestamp())['precipitations_mm'].sum().reset_index()
    cumul.columns = ['date','cumul']
    cumul['rolling'] = cumul['cumul'].rolling(12).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cumul['date'], y=cumul['cumul'],
                             name="Cumul mensuel", line=dict(color="#95d5b2", width=1),
                             opacity=0.6))
    fig.add_trace(go.Scatter(x=cumul['date'], y=cumul['rolling'],
                             name="Moy. mobile 12 mois",
                             line=dict(color="#1b4332", width=2.5)))
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                      font_family="Source Sans 3", title="Évolution temporelle des précipitations",
                      title_font_size=13, margin=dict(t=40,b=10),
                      xaxis_title="Date", yaxis_title="Précipitations (mm)",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    # Row 4 — Corrélation + risque annuel
    col5, col6 = st.columns(2)

    with col5:
        vars_corr = ['precipitations_mm','temperature_moy','humidite_pct',
                     'vent_ms','spi','risque_secheresse']
        corr = df_f[vars_corr].astype(float).corr().round(2)
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1, title="Matrice de corrélation")
        fig.update_layout(paper_bgcolor="white", font_family="Source Sans 3",
                          title_font_size=13, margin=dict(t=40,b=10),
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        risque_an = df_f.groupby(['annee','risque_secheresse']).size().unstack(fill_value=0)
        risque_pct = risque_an.div(risque_an.sum(axis=1), axis=0) * 100
        fig = go.Figure()
        for i, (label, color) in enumerate(zip(RISK_LABELS.values(), RISK_COLORS.values())):
            if i in risque_pct.columns:
                fig.add_trace(go.Bar(name=label, x=risque_pct.index,
                                     y=risque_pct[i], marker_color=color))
        fig.update_layout(barmode='stack', paper_bgcolor="white", plot_bgcolor="white",
                          font_family="Source Sans 3",
                          title="Risque par année (%)", title_font_size=13,
                          margin=dict(t=40,b=10), xaxis_title="Année",
                          yaxis_title="%", legend_title="Risque")
        st.plotly_chart(fig, use_container_width=True)

    # Export
    with st.expander("🗃️ Données brutes"):
        st.dataframe(df_f[['date','gouvernorat','region','precipitations_mm',
                           'temperature_moy','humidite_pct','spi','risque_secheresse']].head(200),
                     use_container_width=True, height=300)
        st.download_button("⬇️ Télécharger CSV",
                           df_f.to_csv(index=False).encode("utf-8"),
                           file_name="secheresse_tunisie_filtre.csv", mime="text/csv")
