import streamlit as st
import requests
from streamlit_lottie import st_lottie
from database import init_db, add_user, verify_user
from app import run_dashboard, run_admin_dashboard

# Ensure database exists
init_db()

st.set_page_config(page_title="BioPulse-AI Elite", layout="wide")

# Helper to clear session on logout
def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.is_admin = 0
    st.rerun()

# Safe Lottie Loader
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
            if lottie_anim:
                st_lottie(lottie_anim, height=400)
            else:
                st.title("🧬 BioPulse-AI")
                st.info("Neural Interface Ready. Please Authenticate.")
        
        with r_col:
            t1, t2 = st.tabs(["🔒 Secure Login", "✨ Register Profile"])
            with t1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.button("Unlock Dashboard"):
                    user_data = verify_user(u, p)
                    if user_data:
                        st.session_state.update({
                            "logged_in": True, "user_id": user_data[0], 
                            "user_name": user_data[1], "is_admin": user_data[4]
                        })
                        st.rerun()
                    else: st.error("Access Denied: Check Credentials")
            with t2:
                new_u = st.text_input("Choose Username")
                new_p = st.text_input("Choose Password", type="password")
                w = st.number_input("Starting Weight (kg)", value=70.0)
                # Secret Key: MUKESH2026
                admin_code = st.text_input("Admin Code (Optional)", type="password")
                if st.button("Initialize"):
                    role = 1 if admin_code == "MUKESH2026" else 0
                    if add_user(new_u, new_p, w, role):
                        st.success("Sync Complete! Please Log In.")
                    else: st.error("Username already active.")
    else:
        # Sidebar with Logout and Identity
        st.sidebar.title("🧬 BioPulse-AI")
        st.sidebar.write(f"User: **{st.session_state.user_name}**")
        if st.sidebar.button("🚪 Logout System"):
            logout()
            
        if st.session_state.is_admin == 1:
            mode = st.sidebar.radio("Navigation", ["Personal Hub", "System Admin"])
            run_admin_dashboard() if mode == "System Admin" else run_dashboard()
        else:
            run_dashboard()

if __name__ == "__main__":
    main()