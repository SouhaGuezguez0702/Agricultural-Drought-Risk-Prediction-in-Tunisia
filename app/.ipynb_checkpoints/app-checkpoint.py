import streamlit as st
import streamlit_authenticator as stauth
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'views'))

st.set_page_config(
    page_title="Secheresse Agricole — Tunisie",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Global ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d2818 0%, #1b4332 50%, #2d6a4f 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #d8f3dc !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    padding: 11px 18px; border-radius: 10px; margin: 2px 0;
    transition: all 0.25s ease; font-size: 0.92rem !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.09) !important;
}

.stApp { background: #f4f6f0; }

.card {
    background: white; border-radius: 18px; padding: 26px 30px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04); margin-bottom: 20px;
}
.card-green {
    background: linear-gradient(135deg, #0d2818 0%, #1b4332 50%, #2d6a4f 100%);
    border-radius: 18px; padding: 30px 34px; color: white; margin-bottom: 20px;
}
.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 2rem; font-weight: 700; color: #1b4332;
}
.metric-lbl { font-size: 0.78rem; color: #999; margin-top: 2px; }

/* Login */
[data-testid="stForm"] {
    background: white !important;
    border-radius: 20px !important;
    padding: 32px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.10) !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
}

/* Inputs */
.stTextInput input {
    border-radius: 10px !important;
    border: 1.5px solid #e0e0e0 !important;
    padding: 10px 14px !important;
    font-size: 0.92rem !important;
}
.stTextInput input:focus {
    border-color: #2d6a4f !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.12) !important;
}

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primaryFormSubmit"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1b4332, #2d6a4f) !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(27,67,50,0.3) !important;
    color: white !important;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeInUp 0.5s ease forwards; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
hr { border: none; border-top: 1px solid #eee; margin: 18px 0; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #2d6a4f; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Credentials ───────────────────────────────────────────────────────────
# Remplace les hash par ceux generes avec generate_hash.py
credentials = {
    "usernames": {
        "admin": {
            "name":     "Administrateur",
            "email":    "admin@secheresse.tn",
            "password": "$2b$12$ypBoDhpmUA48rKSDUVlNIOUx9pzVQRTrvf3lM9xahbGU5mBBOtmi.",
            "role":     "admin",
            "avatar":   "👨‍💼"
        },
        "souha": {
            "name":     "Souha Guezguez",
            "email":    "souha.guezguez@etudiant.tn",
            "password": "$2b$12$UE1LOeQNuFWNGvkUd5P0tu.Yh3u6gTFjXQQxTtspu9UZHimBTiiYa",
            "role":     "etudiant",
            "avatar":   "👩‍🎓"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "secheresse_auth",
    "secheresse_secret_key_2026",
    1
)

# ── Page Login ────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_mid, col_r = st.columns([1, 1.2, 1])

    with col_mid:
        # Logo et titre
        st.markdown("""
        <div class="fade-in" style="text-align:center; padding: 32px 0 24px;">
            <div style="font-size:3.5rem; margin-bottom:10px;">🌾</div>
            <div style="font-family:'Playfair Display',serif; font-size:1.9rem;
                        color:#1b4332; font-weight:700; line-height:1.2;">
                Secheresse Agricole
            </div>
            <div style="color:#999; font-size:0.82rem; margin-top:6px;
                        letter-spacing:0.15em; text-transform:uppercase;">
                Tunisie — ML Dashboard
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Formulaire login via authenticator
        authenticator.login(
            location='main',
            fields={
                'Form name': 'Connexion',
                'Username':  "Nom d'utilisateur",
                'Password':  'Mot de passe',
                'Login':     '🔐 Se connecter'
            }
        )

        # Messages d'état
        auth_status = st.session_state.get("authentication_status")

        if auth_status is False:
            st.markdown("""
            <div style='background:#fde8e8; border:1px solid #e74c3c;
                        border-radius:10px; padding:12px 16px; color:#c0392b;
                        font-size:0.88rem; text-align:center; margin-top:8px;'>
                ❌ Identifiants incorrects. Veuillez reessayer.
            </div>
            """, unsafe_allow_html=True)
        elif auth_status is None:
            st.markdown("""
            <div style='background:#fff3cd; border:1px solid #f0d060;
                        border-radius:10px; padding:12px 16px; color:#856404;
                        font-size:0.88rem; text-align:center; margin-top:8px;'>
                💡 Comptes demo : <strong>admin/admin123</strong>
                ou <strong>souha/souha2026</strong>
            </div>
            """, unsafe_allow_html=True)

# ── App principale ────────────────────────────────────────────────────────
def show_app():
    username  = st.session_state.get("username", "")
    name      = st.session_state.get("name", "Utilisateur")
    user_info = credentials["usernames"].get(username, {})
    avatar    = user_info.get("avatar", "👤")
    role      = user_info.get("role", "user")
    email     = user_info.get("email", "")

    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding:20px 0 16px;'>
            <div style='font-size:2.6rem; margin-bottom:8px;'>{avatar}</div>
            <div style='font-family:serif; font-size:1rem; color:white;
                        font-weight:600;'>{name}</div>
            <div style='font-size:0.72rem; opacity:0.45; margin-top:2px;'>{email}</div>
            <div style='display:inline-block; background:rgba(255,255,255,0.13);
                        border-radius:20px; padding:3px 12px;
                        font-size:0.72rem; margin-top:8px;'>
                {'⚙️ Admin' if role == 'admin' else '🎓 Etudiante'}
            </div>
        </div>
        <hr style='border-color:rgba(255,255,255,0.10); margin:0 0 14px;'>
        <div style='font-size:0.68rem; opacity:0.4; padding:0 8px 6px;
                    letter-spacing:0.1em; text-transform:uppercase;'>Navigation</div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "nav",
            [
                "🏠  Accueil",
                "🗺️  Carte interactive",
                "🔬  Prediction",
                "📊  Dashboard EDA",
                "🏆  Comparaison Modeles",
                "👤  Mon Profil",
            ],
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        authenticator.logout(
            button_name="🚪  Se deconnecter",
            location="sidebar"
        )
        st.markdown("""
        <div style='font-size:0.68rem; opacity:0.3; text-align:center; margin-top:10px;'>
            v2.0 — 2025/2026
        </div>
        """, unsafe_allow_html=True)

    # Routing
    if "Accueil"    in page: import home       as p; p.render()
    elif "Carte"    in page: import carte      as p; p.render()
    elif "Prediction" in page: import prediction as p; p.render()
    elif "EDA"      in page: import eda        as p; p.render()
    elif "Comparaison" in page: import models  as p; p.render()
    elif "Profil"   in page: import profile    as p; p.render(name, username, user_info)

# ── Point d'entree ────────────────────────────────────────────────────────
auth_status = st.session_state.get("authentication_status")

if auth_status is True:
    show_app()
else:
    show_login()
