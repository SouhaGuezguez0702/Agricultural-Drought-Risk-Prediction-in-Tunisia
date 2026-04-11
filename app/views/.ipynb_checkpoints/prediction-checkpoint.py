import streamlit as st
import numpy as np
import pandas as pd
import joblib
from export_pdf import bouton_telecharger_pdf
RISK_LABELS = {0:"Aucun risque", 1:"Secheresse moderee",
               2:"Secheresse severe", 3:"Secheresse extreme"}
RISK_ICONS  = {0:"🟢", 1:"🟡", 2:"🟠", 3:"🔴"}
RISK_COLORS = {0:"#d8f3dc", 1:"#fff3cd", 2:"#ffe5cc", 3:"#fde8e8"}
RISK_TEXT   = {0:"#1b4332", 1:"#856404", 2:"#b54708", 3:"#c0392b"}

GOUVERNORATS = [
    "Tunis","Ariana","Ben Arous","Manouba","Nabeul","Zaghouan",
    "Bizerte","Beja","Jendouba","Kef","Siliana","Sousse",
    "Monastir","Mahdia","Sfax","Kairouan","Kasserine","Sidi Bouzid",
    "Gabes","Medenine","Tataouine","Gafsa","Tozeur","Kebili"
]
REGIONS = {
    "Nord":   ["Tunis","Ariana","Ben Arous","Manouba","Nabeul","Zaghouan",
               "Bizerte","Beja","Jendouba","Kef","Siliana"],
    "Centre": ["Sousse","Monastir","Mahdia","Sfax","Kairouan","Kasserine","Sidi Bouzid"],
    "Sud":    ["Gabes","Medenine","Tataouine","Gafsa","Tozeur","Kebili"]
}

def get_region(gouv):
    for r, gs in REGIONS.items():
        if gouv in gs: return r
    return "Nord"

@st.cache_resource
def load_model():
    try:
        model    = joblib.load('../models/best_model.pkl')
        scaler   = joblib.load('../models/scaler.pkl')
        le_reg   = joblib.load('../models/le_region.pkl')
        le_gouv  = joblib.load('../models/le_gouvernorat.pkl')
        features = joblib.load('../models/features.pkl')
        return model, scaler, le_reg, le_gouv, features
    except:
        return None, None, None, None, None

def predict(model, scaler, le_reg, le_gouv, features,
            gouvernorat, region, precip, precip_7j, precip_30j,
            temp_moy, temp_max, temp_min, humidite, vent, mois):

    def get_saison(m):
        if m in [12,1,2]: return 1
        elif m in [3,4,5]: return 2
        elif m in [6,7,8]: return 3
        else: return 4

    try: region_enc = le_reg.transform([region])[0]
    except: region_enc = 0
    try: gouv_enc = le_gouv.transform([gouvernorat])[0]
    except: gouv_enc = 0

    input_data = {
        'precipitations_mm':   precip,
        'temperature_moy':     temp_moy,
        'temperature_max':     temp_max,
        'temperature_min':     temp_min,
        'humidite_pct':        humidite,
        'vent_ms':             vent,
        'precip_rolling_7j':   precip_7j,
        'precip_rolling_30j':  precip_30j,
        'amplitude_thermique': temp_max - temp_min,
        'jour_sec':            1 if precip == 0 else 0,
        'saison':              get_saison(mois),
        'mois':                mois,
        'region_enc':          region_enc,
        'gouvernorat_enc':     gouv_enc,
    }

    X    = pd.DataFrame([input_data])[features]
    X_sc = scaler.transform(X)
    pred  = int(model.predict(X_sc)[0])
    proba = model.predict_proba(X_sc)[0].tolist()
    return pred, proba


def render():
    st.markdown("""
    <div class="card-green" style="padding:24px 28px; margin-bottom:20px;">
        <h1 style="color:white; margin:0 0 6px; font-size:1.8rem;">
            🔬 Prediction en temps reel
        </h1>
        <p style="opacity:0.65; margin:0; font-size:0.9rem;">
            Entrez les donnees meteo d'une region pour obtenir le niveau de risque
        </p>
    </div>
    """, unsafe_allow_html=True)

    model, scaler, le_reg, le_gouv, features = load_model()
    if model is None:
        st.warning("Modele introuvable. Lance d'abord le notebook 02_Modeling.ipynb")
        return

    # Initialiser le compteur de predictions
    if "pred_count" not in st.session_state:
        st.session_state["pred_count"] = 0

    col_form, col_result = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("#### 📍 Localisation")
        c1, c2 = st.columns(2)
        with c1:
            gouvernorat = st.selectbox("Gouvernorat", GOUVERNORATS)
        with c2:
            region = get_region(gouvernorat)
            st.markdown(f"""
            <div style='margin-top:28px; padding:8px 14px; background:#d8f3dc;
                        border-radius:8px; font-size:0.88rem; color:#1b4332;
                        font-weight:600;'>
                🗺️ Region : {region}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 🌧️ Precipitations")
        c3, c4, c5 = st.columns(3)
        with c3:
            precip     = st.number_input("Precip. jour (mm)", 0.0, 150.0, 0.0, 0.5)
        with c4:
            precip_7j  = st.number_input("Moy. 7 jours (mm)", 0.0, 100.0, 0.0, 0.5)
        with c5:
            precip_30j = st.number_input("Moy. 30 jours (mm)", 0.0, 80.0, 0.2, 0.5)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 🌡️ Temperature & Atmosphere")
        c6, c7 = st.columns(2)
        with c6:
            temp_moy = st.slider("Temperature moy. (C)", -5.0, 45.0, 28.0, 0.5)
            temp_max = st.slider("Temperature max. (C)",  0.0, 55.0, 35.0, 0.5)
        with c7:
            temp_min = st.slider("Temperature min. (C)", -5.0, 35.0, 21.0, 0.5)
            humidite = st.slider("Humidite (%)", 5, 100, 22)

        c8, c9 = st.columns(2)
        with c8:
            vent = st.number_input("Vent (m/s)", 0.0, 20.0, 6.0, 0.5)
        with c9:
            mois_noms = {
                1:"Janvier",2:"Fevrier",3:"Mars",4:"Avril",
                5:"Mai",6:"Juin",7:"Juillet",8:"Aout",
                9:"Septembre",10:"Octobre",11:"Novembre",12:"Decembre"
            }
            mois = st.selectbox("Mois", list(mois_noms.keys()),
                                format_func=lambda x: mois_noms[x], index=2)

        st.markdown('</div>', unsafe_allow_html=True)

        # Bouton avec key unique
        predict_btn = st.button(
            "🌾  Lancer la prediction",
            use_container_width=True,
            type="primary",
            key="btn_predict"
        )

    with col_result:

        # Etat vide avant le premier clic
        if st.session_state["pred_count"] == 0 and not predict_btn:
            st.markdown("""
            <div class="card" style="text-align:center; padding:48px 20px; color:#aaa;">
                <div style="font-size:3rem; margin-bottom:14px;">🌾</div>
                <div style="font-size:1rem; line-height:1.6;">
                    Remplissez le formulaire<br>et cliquez sur<br>
                    <strong style="color:#1b4332;">Lancer la prediction</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Calculer si bouton clique
        if predict_btn:
            pred, proba = predict(
                model, scaler, le_reg, le_gouv, features,
                gouvernorat, region, precip, precip_7j, precip_30j,
                temp_moy, temp_max, temp_min, humidite, vent, mois
            )
            st.session_state["pred_count"] += 1
            st.session_state["result"] = {
                "pred": pred, "proba": proba,
                "gouvernorat": gouvernorat, "region": region,
                "precip": precip, "temp_moy": temp_moy,
                "humidite": humidite, "vent": vent,
                "precip_30j": precip_30j,
                "mois_nom": mois_noms[mois]
            }

        # Afficher le résultat depuis session_state
        if "result" in st.session_state:
            r     = st.session_state["result"]
            pred  = r["pred"]
            proba = r["proba"]

            # Badge prediction numero
            st.markdown(f"""
            <div style='text-align:right; font-size:0.75rem; color:#aaa;
                        margin-bottom:8px;'>
                Prediction #{st.session_state["pred_count"]}
            </div>
            """, unsafe_allow_html=True)

            # Resultat principal
            st.markdown(f"""
            <div style='background:{RISK_COLORS[pred]}; border-radius:14px;
                        padding:28px; text-align:center; margin-bottom:16px;'>
                <div style='font-size:3rem; margin-bottom:10px;'>{RISK_ICONS[pred]}</div>
                <div style='font-family:serif; font-size:1.7rem; font-weight:700;
                            color:{RISK_TEXT[pred]};'>{RISK_LABELS[pred]}</div>
                <div style='font-size:0.85rem; color:{RISK_TEXT[pred]};
                            opacity:0.75; margin-top:6px;'>
                    {r["gouvernorat"]} — {r["region"]} — {r["mois_nom"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

                        # Probabilités
            st.markdown("**Probabilites par classe :**")
            labels_list = list(RISK_LABELS.values())
            for i, p in enumerate(proba):
                pct = p * 100
                st.markdown(f"""
                <div style='display:flex; align-items:center; gap:10px;
                            margin-bottom:8px; font-size:0.85rem;'>
                    <span style='width:20px;'>{RISK_ICONS[i]}</span>
                    <span style='width:85px; color:#555; font-size:0.78rem;'>
                        {labels_list[i][:12]}
                    </span>
                    <div style='flex:1; background:#f0f0f0; border-radius:6px; height:10px;'>
                        <div style='width:{pct:.1f}%; background:{RISK_COLORS[i]};
                                    border-radius:6px; height:10px;
                                    border:1px solid rgba(0,0,0,0.08);
                                    min-width:2px;'></div>
                    </div>
                    <span style='width:45px; text-align:right; font-weight:700;
                                 color:{RISK_TEXT[i]};'>{pct:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)

            # ✅ ICI (IMPORTANT : même indentation que st.markdown)
            st.markdown("<hr>", unsafe_allow_html=True)
            bouton_telecharger_pdf(st.session_state["result"])

            # Tableau données
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("**📋 Donnees saisies :**")
            summary = pd.DataFrame({
                "Variable": ["Precipitations","Temperature","Humidite",
                             "Vent","Moy. 30j","Mois"],
                "Valeur":   [f"{r['precip']} mm", f"{r['temp_moy']}°C",
                             f"{r['humidite']}%", f"{r['vent']} m/s",
                             f"{r['precip_30j']} mm", r['mois_nom']]
            })
            st.dataframe(summary, hide_index=True, use_container_width=True)

            # Alerte si risque eleve
            if pred >= 2:
                st.markdown("""
                <div style='background:#fde8e8; border:1px solid #e74c3c;
                            border-radius:10px; padding:12px 14px;
                            font-size:0.82rem; color:#c0392b; margin-top:10px;'>
                    ⚠️ <strong>Alerte :</strong> Risque eleve detecte.
                    Irrigation recommandee.
                </div>
                """, unsafe_allow_html=True)