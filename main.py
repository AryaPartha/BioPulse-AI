import streamlit as st
import requests
import sqlite3
from streamlit_lottie import st_lottie
from database import init_db, add_user, verify_user
from app import run_dashboard, run_admin_dashboard

# Initialize database on startup
init_db()

st.set_page_config(page_title="BioPulse-AI Elite", layout="wide", initial_sidebar_state="expanded")

# --- SAFE LOTTIE LOADER ---
# Prevents the app from crashing if the URL is down or internet is slow
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Load a high-quality fitness/data animation
lottie_fitness = load_lottieurl("https://lottie.host/8e23f114-6467-428a-814d-16f3d4400570/hYmS8Qp1xL.json")

# --- GLOBAL PREMIUM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e9ecef; }
    
    /* Neon Gradient Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #0099ff 0%, #00ffcc 100%);
        color: #0b0e11 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.4);
    }
    
    /* Glassmorphic Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 8px 8px 0 0;
        color: #8b949e;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Layout: Animation on left, Login on right
        left_col, right_col = st.columns([1, 1])
        
        with left_col:
            # Defensive check: only render if data was successfully fetched
            if lottie_fitness:
                st_lottie(lottie_fitness, height=400, key="fitness_anim")
            else:
                st.info("🧬 BioPulse-AI: System Online & Secured")
                st.caption("Neural data processing active...")
        
        with right_col:
            st.title("BioPulse-AI Elite")
            st.markdown("#### *Predictive Fitness Intelligence*")
            
            tab1, tab2 = st.tabs(["🔒 Secure Login", "✨ Create Profile"])
            
            with tab1:
                u = st.text_input("Username", placeholder="e.g., Mukesh")
                p = st.text_input("Password", type="password")
                if st.button("Access Dashboard"):
                    user_data = verify_user(u, p)
                    if user_data:
                        # Map database columns to session state
                        st.session_state.update({
                            "logged_in": True, 
                            "user_id": user_data[0], 
                            "user_name": user_data[1], 
                            "is_admin": user_data[4]
                        })
                        st.rerun()
                    else:
                        st.error("Invalid Credentials. Access Denied.")
            
            with tab2:
                new_u = st.text_input("Choose Username")
                new_p = st.text_input("Create Password", type="password")
                w = st.number_input("Current Weight (kg)", value=70.0, step=0.1)
                if st.button("Initialize Account"):
                    if add_user(new_u, new_p, w):
                        st.success("Account Synced! You can now log in.")
                    else:
                        st.error("Username already exists in the system.")
    else:
        # Role-Based Access Control (RBAC)
        if st.session_state.is_admin == 1:
            mode = st.sidebar.radio("🧭 Navigation", ["Personal Dashboard", "System Admin"])
            if mode == "System Admin":
                run_admin_dashboard()
            else:
                run_dashboard()
        else:
            run_dashboard()

if __name__ == "__main__":
    main()