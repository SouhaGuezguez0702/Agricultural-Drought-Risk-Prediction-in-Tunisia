import streamlit as st
import pandas as pd
from datetime import datetime

def render(name, username, user_info):
    avatar = user_info.get("avatar", "👤")
    role   = user_info.get("role", "user")
    email  = user_info.get("email", "")

    st.markdown("""
    <div class="card-green fade-in" style="padding:28px 32px; margin-bottom:24px;">
        <h1 style="color:white; margin:0 0 6px; font-size:1.8rem;">
            👤 Mon Profil
        </h1>
        <p style="opacity:0.6; margin:0; font-size:0.9rem;">
            Informations du compte connecte
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown(f"""
        <div class="card fade-in" style="text-align:center; padding:36px 20px;">
            <div style="font-size:5rem; margin-bottom:16px;">{avatar}</div>
            <div style="font-family:'Playfair Display',serif; font-size:1.4rem;
                        color:#1b4332; font-weight:700; margin-bottom:4px;">{name}</div>
            <div style="color:#888; font-size:0.85rem; margin-bottom:16px;">@{username}</div>
            <div style="display:inline-block;
                        background:{'#d8f3dc' if role=='admin' else '#e8f4fd'};
                        color:{'#1b4332' if role=='admin' else '#1565c0'};
                        border-radius:20px; padding:5px 16px; font-size:0.82rem;
                        font-weight:600;">
                {'⚙️ Administrateur' if role=='admin' else '🎓 Etudiant'}
            </div>
            <hr style="margin:20px 0;">
            <div style="font-size:0.82rem; color:#888;">{email}</div>
            <div style="font-size:0.78rem; color:#bbb; margin-top:8px;">
                Connecte depuis {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card fade-in">
            <h3 style="color:#1b4332; margin-top:0; margin-bottom:20px;">
                📋 Informations du projet
            </h3>
        </div>
        """, unsafe_allow_html=True)

        infos = [
            ("🎓 Filiere",       "4eme cycle Data Science & Intelligence Artificielle"),
            ("📅 Annee scolaire","2025 / 2026"),
            ("📊 Dataset",       "NASA POWER API — 24 gouvernorats (2010-2023)"),
            ("🤖 Meilleur modele","Random Forest Optimise (Accuracy = 87.4%)"),
            ("🌾 Problematique", "Prediction de la secheresse agricole en Tunisie"),
            ("📁 Livrables",     "Notebooks EDA + Modeling, Interface Streamlit, GitHub"),
        ]

        for label, val in infos:
            st.markdown(f"""
            <div style="display:flex; gap:16px; padding:12px 0;
                        border-bottom:1px solid #f5f5f5; font-size:0.88rem;">
                <span style="min-width:160px; font-weight:600;
                             color:#1b4332;">{label}</span>
                <span style="color:#555;">{val}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Stats du projet
        st.markdown("""
        <h3 style="color:#1b4332; margin-bottom:16px;">📈 Stats du projet</h3>
        """, unsafe_allow_html=True)

        stats = [
            ("122 712", "Observations totales",    "#1b4332"),
            ("24",      "Gouvernorats couverts",    "#2d6a4f"),
            ("14",      "Variables utilisees",      "#40916c"),
            ("87.4%",   "Accuracy meilleur modele", "#52b788"),
        ]
        cols = st.columns(4)
        for col, (val, lbl, color) in zip(cols, stats):
            with col:
                st.markdown(f"""
                <div style="text-align:center; padding:16px 8px; background:#f8fdf9;
                            border-radius:12px; border-top:3px solid {color};">
                    <div style="font-family:'Playfair Display',serif; font-size:1.6rem;
                                font-weight:700; color:{color};">{val}</div>
                    <div style="font-size:0.72rem; color:#888; margin-top:4px;">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)

    # Activite recente
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card fade-in">
        <h3 style="color:#1b4332; margin-top:0;">🕒 Activite de la session</h3>
    </div>
    """, unsafe_allow_html=True)

    pred_count = st.session_state.get("pred_count", 0)
    activites = [
        ("✅", "Connexion reussie",                  datetime.now().strftime('%H:%M'), "success"),
        ("🔬", f"Predictions effectuees : {pred_count}", datetime.now().strftime('%H:%M'), "info"),
        ("📊", "Dashboard EDA consulte",             datetime.now().strftime('%H:%M'), "info"),
    ]

    bg_map = {"success": "#d8f3dc", "info": "#e8f4fd", "warn": "#fff3cd"}
    for icon, desc, time, kind in activites:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; padding:10px 14px;
                    background:{bg_map[kind]}; border-radius:10px; margin-bottom:8px;
                    font-size:0.88rem;">
            <span style="font-size:1.1rem;">{icon}</span>
            <span style="flex:1; color:#444;">{desc}</span>
            <span style="color:#aaa; font-size:0.78rem;">{time}</span>
        </div>
        """, unsafe_allow_html=True)
