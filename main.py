import streamlit as st
import requests
import sqlite3
from streamlit_lottie import st_lottie

# Import your custom modules
try:
    from database import init_db, add_user, verify_user
    from app import run_dashboard, run_admin_dashboard
except ImportError as e:
    st.error(f"Critical Error: Missing project files. {e}")
    st.stop()

# Initialize DB
try:
    init_db()
except Exception as e:
    st.error(f"Database Initialization Failed: {e}")

st.set_page_config(page_title="BioPulse-AI Elite", layout="wide")

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_anim = load_lottieurl("https://lottie.host/8e23f114-6467-428a-814d-16f3d4400570/hYmS8Qp1xL.json")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        l_col, r_col = st.columns([1, 1])
        with l_col:
            # Check if lottie_anim exists before rendering
            if lottie_anim: 
                st_lottie(lottie_anim, height=400)
            else: 
                st.title("🧬 BioPulse-AI")
                st.warning("Animation failed to load, but system is online.")
        
        with r_col:
            t1, t2 = st.tabs(["🔒 Login", "✨ Sign Up"])
            with t1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Unlock Dashboard"):
                    user_data = verify_user(u, p)
                    if user_data:
                        st.session_state.update({
                            "logged_in": True, 
                            "user_id": user_data[0], 
                            "user_name": user_data[1], 
                            "is_admin": user_data[4]
                        })
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            with t2:
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                w = st.number_input("Weight (kg)", value=70.0)
                admin_code = st.text_input("Admin Code", type="password")
                if st.button("Create Account"):
                    role = 1 if admin_code == "PARTHA2026" else 0
                    if add_user(new_u, new_p, w, role): 
                        st.success("Account Created! Please Login.")
                    else:
                        st.error("Username already exists.")
    else:
        # Sidebar with Logout
        if st.sidebar.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
        if st.session_state.is_admin == 1:
            mode = st.sidebar.radio("Navigation", ["My Fitness", "System Admin"])
            run_admin_dashboard() if mode == "System Admin" else run_dashboard()
        else: 
            run_dashboard()

if __name__ == "__main__":
    main()