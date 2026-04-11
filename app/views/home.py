import streamlit as st

def render():
    # Hero
    st.markdown("""
    <div class="card-green">
        <div style='font-size:0.8rem; opacity:0.6; letter-spacing:0.15em; margin-bottom:10px;'>
            PROJET MACHINE LEARNING — 2025/2026
        </div>
        <div style='font-family: Playfair Display, serif; font-size:2.2rem;
                    color:white; line-height:1.2; margin-bottom:12px;'>
            Prédiction de la Sécheresse<br>Agricole en Tunisie
        </div>
        <p style='opacity:0.75; font-size:1rem; max-width:580px; line-height:1.7; margin:0;'>
            Un système de détection précoce basé sur le Machine Learning
            utilisant les données météorologiques de
            <strong style='color:white;'>24 gouvernorats tunisiens</strong>
            (2010–2023) via NASA POWER API.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("122 712", "Observations", "📋"),
        ("24",      "Gouvernorats", "🗺️"),
        ("14",      "Variables",    "📊"),
        ("87.4%",   "Accuracy RF",  "🎯"),
    ]
    for col, (val, lbl, icon) in zip([c1,c2,c3,c4], kpis):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:20px 12px;">
                <div style='font-size:1.6rem; margin-bottom:6px;'>{icon}</div>
                <div class="metric-val">{val}</div>
                <div class="metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="card">
            <h3 style='margin-top:0; color:#1b4332;'>🎯 Problématique</h3>
            <p style='color:#555; line-height:1.8; font-size:0.93rem;'>
                La Tunisie fait face à une pression hydrique croissante.
                Ce projet prédit le <strong>niveau de risque de sécheresse</strong>
                (Aucun / Modéré / Sévère / Extrême) par région à partir de données
                météo historiques officielles.
            </p>
            <div style='display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;'>
                <span style='background:#d8f3dc; color:#1b4332; border-radius:20px;
                             padding:4px 12px; font-size:0.8rem; font-weight:600;'>
                    Classification
                </span>
                <span style='background:#e8f4fd; color:#1565c0; border-radius:20px;
                             padding:4px 12px; font-size:0.8rem; font-weight:600;'>
                    NASA POWER API
                </span>
                <span style='background:#fff3cd; color:#856404; border-radius:20px;
                             padding:4px 12px; font-size:0.8rem; font-weight:600;'>
                    Indice SPI
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="card">
            <h3 style='margin-top:0; color:#1b4332;'>📦 Sources de données</h3>
            <table style='width:100%; font-size:0.88rem; border-collapse:collapse;'>
                <tr style='border-bottom:1px solid #f0f0f0;'>
                    <td style='padding:6px 4px;'>🌐</td>
                    <td style='padding:6px 4px;'><strong>NASA POWER API</strong></td>
                    <td style='padding:6px 4px; color:#888;'>Météo journalière</td>
                </tr>
                <tr style='border-bottom:1px solid #f0f0f0;'>
                    <td style='padding:6px 4px;'>🇹🇳</td>
                    <td style='padding:6px 4px;'><strong>data.gov.tn</strong></td>
                    <td style='padding:6px 4px; color:#888;'>Stations officielles</td>
                </tr>
                <tr>
                    <td style='padding:6px 4px;'>📐</td>
                    <td style='padding:6px 4px;'><strong>Indice SPI</strong></td>
                    <td style='padding:6px 4px; color:#888;'>Variable cible calculée</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # Pipeline
    st.markdown("""
    <div class="card">
        <h3 style='margin-top:0; color:#1b4332;'>🔄 Pipeline du projet</h3>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("1", "Collecte",     "NASA POWER API\n24 gouvernorats",    "#1b4332"),
        ("2", "EDA",          "Analyse exploratoire\nvisualisations","#2d6a4f"),
        ("3", "Preprocessing","Nettoyage, encodage\nnormalisation",  "#40916c"),
        ("4", "Modélisation", "LR, DT, RF\nXGBoost",                "#52b788"),
        ("5", "Évaluation",   "F1-Score, Accuracy\nmatrice confusion","#74c69d"),
        ("6", "Application",  "Interface Streamlit\ncarte interactive","#95d5b2"),
    ]
    cols = st.columns(6)
    for col, (num, title, desc, color) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style='text-align:center; padding:12px 4px;'>
                <div style='width:38px; height:38px; border-radius:50%;
                            background:{color}; color:white; font-weight:700;
                            font-size:1rem; display:flex; align-items:center;
                            justify-content:center; margin:0 auto 8px;'>{num}</div>
                <div style='font-weight:600; color:#1b4332; font-size:0.85rem;
                            margin-bottom:4px;'>{title}</div>
                <div style='font-size:0.72rem; color:#888; line-height:1.4;
                            white-space:pre-line;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Classes de risque
    st.markdown("""
    <div class="card">
        <h3 style='margin-top:0; color:#1b4332;'>🎨 Classes de risque (Indice SPI)</h3>
        <div style='display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:12px;'>
            <div style='text-align:center; padding:16px; background:#d8f3dc;
                        border-radius:12px;'>
                <div style='font-size:1.5rem;'>🟢</div>
                <div style='font-weight:700; color:#1b4332; margin:4px 0;'>Classe 0</div>
                <div style='font-size:0.82rem; color:#2d6a4f;'>Aucun risque</div>
                <div style='font-size:0.75rem; color:#888; margin-top:4px;'>SPI > -0.5</div>
            </div>
            <div style='text-align:center; padding:16px; background:#fff3cd;
                        border-radius:12px;'>
                <div style='font-size:1.5rem;'>🟡</div>
                <div style='font-weight:700; color:#856404; margin:4px 0;'>Classe 1</div>
                <div style='font-size:0.82rem; color:#856404;'>Modéré</div>
                <div style='font-size:0.75rem; color:#888; margin-top:4px;'>SPI > -1.0</div>
            </div>
            <div style='text-align:center; padding:16px; background:#ffe5cc;
                        border-radius:12px;'>
                <div style='font-size:1.5rem;'>🟠</div>
                <div style='font-weight:700; color:#b54708; margin:4px 0;'>Classe 2</div>
                <div style='font-size:0.82rem; color:#b54708;'>Sévère</div>
                <div style='font-size:0.75rem; color:#888; margin-top:4px;'>SPI > -1.5</div>
            </div>
            <div style='text-align:center; padding:16px; background:#fde8e8;
                        border-radius:12px;'>
                <div style='font-size:1.5rem;'>🔴</div>
                <div style='font-weight:700; color:#c0392b; margin:4px 0;'>Classe 3</div>
                <div style='font-size:0.82rem; color:#c0392b;'>Extrême</div>
                <div style='font-size:0.75rem; color:#888; margin-top:4px;'>SPI ≤ -1.5</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
