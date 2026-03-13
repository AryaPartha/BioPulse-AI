import streamlit as st
import requests
from streamlit_lottie import st_lottie
from database import init_db, add_user, verify_user
from app import run_dashboard, run_admin_dashboard

# Ensure DB is initialized
init_db()

st.set_page_config(page_title="BioPulse-AI Elite", layout="wide")

# Safe Lottie Loader: Prevents "NoneType" crashes on slow networks
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

lottie_anim = load_lottieurl("https://lottie.host/8e23f114-6467-428a-814d-16f3d4400570/hYmS8Qp1xL.json")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        l_col, r_col = st.columns([1, 1])
        with l_col:
            if lottie_anim:
                st_lottie(lottie_anim, height=400, key="login_anim")
            else:
                st.title("🧬 BioPulse-AI")
                st.info("System Online. Neural Interface Ready.")
        
        with r_col:
            t1, t2 = st.tabs(["🔒 Secure Login", "✨ Sign Up"])
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
                    else: st.error("Access Denied: Invalid Credentials")
            with t2:
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                w = st.number_input("Starting Weight (kg)", value=70.0)
                # SECRET ADMIN CODE FOR LIVE DEPLOYMENT
                admin_code = st.text_input("Admin Invite Code (Optional)", type="password")
                if st.button("Initialize Profile"):
                    role = 1 if admin_code == "PARTHA2026" else 0
                    if add_user(new_u, new_p, w, is_admin=role):
                        st.success("Profile Created! Switch to Login tab.")
                    else: st.error("Username taken.")
    else:
        # Role-Based Navigation
        if st.session_state.is_admin == 1:
            mode = st.sidebar.radio("🧭 View Mode", ["My Fitness", "System Admin"])
            run_admin_dashboard() if mode == "System Admin" else run_dashboard()
        else:
            run_dashboard()

if __name__ == "__main__":
    main()