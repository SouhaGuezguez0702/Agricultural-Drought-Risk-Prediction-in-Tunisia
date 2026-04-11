import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

RESULTS = {
    "Logistic Regression": {"accuracy":0.609,"f1":0.648,"precision":0.651,"recall":0.609,"color":"#3498db","icon":"📐","desc":"Modèle linéaire de référence"},
    "Decision Tree":       {"accuracy":0.705,"f1":0.735,"precision":0.741,"recall":0.705,"color":"#e67e22","icon":"🌳","desc":"Arbre de décision simple"},
    "Random Forest":       {"accuracy":0.830,"f1":0.836,"precision":0.840,"recall":0.830,"color":"#2ecc71","icon":"🌲","desc":"Ensemble de 100 arbres"},
    "XGBoost":             {"accuracy":0.800,"f1":0.777,"precision":0.780,"recall":0.800,"color":"#9b59b6","icon":"⚡","desc":"Gradient Boosting"},
    "RF Optimisé":         {"accuracy":0.874,"f1":0.873,"precision":0.876,"recall":0.874,"color":"#1b4332","icon":"🏆","desc":"RF + RandomizedSearchCV"},
}

def render():
    st.markdown("""
    <div class="card-green" style="padding:24px 28px; margin-bottom:20px;">
        <h1 style="color:white; margin:0 0 6px; font-size:1.8rem;">
            🏆 Comparaison des Modèles
        </h1>
        <p style="opacity:0.65; margin:0; font-size:0.9rem;">
            Évaluation de 5 algorithmes de classification
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Bannière meilleur modèle
    st.markdown("""
    <div class="card" style="background:#f0faf4; border:1px solid #2d6a4f;
                             text-align:center; padding:18px;">
        <span style="font-size:1.4rem;">🏆</span>
        <strong style="font-size:1.05rem; color:#1b4332;">
            Meilleur modèle : Random Forest Optimisé
        </strong>
        <span style="color:#888; font-size:0.9rem; margin-left:12px;">
            Accuracy = 87.4% | F1 = 87.3%
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cartes modèles
    cols = st.columns(5)
    for col, (name, m) in zip(cols, RESULTS.items()):
        is_best = name == "RF Optimisé"
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:18px 12px;
                 border-top:3px solid {m['color']};">
                <div style="font-size:1.6rem; margin-bottom:8px;">{m['icon']}</div>
                <div style="font-weight:700; font-size:0.82rem; color:#1b4332;
                            margin-bottom:6px;">{"🏆 " if is_best else ""}{name}</div>
                <div style="font-size:0.75rem; color:#888; margin-bottom:10px;">
                    {m['desc']}
                </div>
                <div style="font-size:1.5rem; font-weight:700; color:{m['color']};">
                    {m['accuracy']*100:.1f}%
                </div>
                <div style="font-size:0.72rem; color:#aaa;">Accuracy</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_t, col_r = st.columns([3, 2])

    with col_t:
        st.markdown("### 📋 Tableau des métriques")
        df_m = pd.DataFrame([{
            "Modèle":    f"{m['icon']} {n}",
            "Accuracy":  f"{m['accuracy']*100:.1f}%",
            "F1-Score":  f"{m['f1']:.3f}",
            "Précision": f"{m['precision']:.3f}",
            "Recall":    f"{m['recall']:.3f}",
        } for n, m in RESULTS.items()])
        st.dataframe(df_m, hide_index=True, use_container_width=True)

    with col_r:
        # Radar
        cats = ["Accuracy","F1-Score","Précision","Recall"]
        fig = go.Figure()
        for name, m in list(RESULTS.items())[-3:]:  # Top 3
            vals = [m["accuracy"], m["f1"], m["precision"], m["recall"]]
            fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=cats+[cats[0]],
                fill="toself", name=name,
                line_color=m["color"], opacity=0.65
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0.5,1.0])),
            showlegend=True, paper_bgcolor="white",
            font_family="Source Sans 3", height=300,
            margin=dict(t=20,b=20,l=30,r=30),
            title="Radar Top 3 modèles", title_font_size=12,
            legend=dict(font_size=9)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Graphique barres
    st.markdown("### 📈 Comparaison visuelle")
    metric = st.selectbox("Métrique", ["Accuracy","F1-Score","Précision","Recall"])
    key_map = {"Accuracy":"accuracy","F1-Score":"f1","Précision":"precision","Recall":"recall"}
    k = key_map[metric]

    df_bar = pd.DataFrame([
        {"Modèle": n, metric: m[k], "Couleur": m["color"]}
        for n, m in RESULTS.items()
    ]).sort_values(metric)

    fig = go.Figure(go.Bar(
        x=df_bar[metric], y=df_bar["Modèle"], orientation="h",
        marker_color=df_bar["Couleur"],
        text=[f"{v:.3f}" for v in df_bar[metric]], textposition="outside"
    ))
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                      font_family="Source Sans 3", height=280,
                      xaxis=dict(range=[0.4,1.05], title=metric),
                      margin=dict(t=10,b=10,l=10,r=60))
    st.plotly_chart(fig, use_container_width=True)

    # Analyse des erreurs
    st.markdown("### 🔍 Analyse des erreurs & Interprétation")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="card">
            <h4 style="color:#1b4332; margin-top:0;">Pourquoi RF > XGBoost ici ?</h4>
            <ul style="font-size:0.88rem; color:#555; line-height:1.9;">
                <li>Les données ont une <strong>forte structure spatiale</strong>
                    (région) que RF gère mieux par défaut</li>
                <li>XGBoost nécessite plus d'optimisation d'hyperparamètres
                    pour ce type de données temporelles</li>
                <li>Le déséquilibre des classes favorise RF avec
                    <code>class_weight='balanced'</code></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="card">
            <h4 style="color:#1b4332; margin-top:0;">Top 3 features importantes</h4>
            <div style="font-size:0.88rem;">
        """, unsafe_allow_html=True)
        features = [
            ("precip_rolling_30j",  "78%", "Moy. précip. 30 jours"),
            ("temperature_moy",     "61%", "Température moyenne"),
            ("precip_rolling_7j",   "55%", "Moy. précip. 7 jours"),
        ]
        for feat, imp, desc in features:
            st.markdown(f"""
            <div style='margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between;
                            font-size:0.85rem; margin-bottom:4px;'>
                    <span><code>{feat}</code></span>
                    <span style='font-weight:600; color:#1b4332;'>{imp}</span>
                </div>
                <div style='background:#f0f0f0; border-radius:4px; height:6px;'>
                    <div style='width:{imp}; background:#1b4332; border-radius:4px;
                                height:6px;'></div>
                </div>
                <div style='font-size:0.75rem; color:#888; margin-top:2px;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Conclusion
    st.markdown("""
    <div class="card" style="background:#f0faf4; border-left:4px solid #1b4332;">
        <strong>💡 Conclusion</strong><br>
        <span style="font-size:0.9rem; color:#444; line-height:1.8;">
        Le <strong>Random Forest optimisé</strong> (Accuracy=87.4%, F1=87.3%) est le meilleur
        modèle pour ce problème. Les features les plus prédictives sont les <strong>moyennes
        mobiles des précipitations</strong> sur 7 et 30 jours, ce qui confirme que la
        sécheresse est un phénomène cumulatif plutôt qu'instantané.
        </span>
    </div>
    """, unsafe_allow_html=True)
