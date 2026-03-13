import streamlit as st
import requests
from streamlit_lottie import st_lottie
from database import init_db, add_user, verify_user
from app import run_dashboard, run_admin_dashboard

init_db()

# --- SAFE LOTTIE LOADER ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5) # Added timeout to prevent hanging
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Load the animation
lottie_fitness = load_lottieurl("https://lottie.host/8e23f114-6467-428a-814d-16f3d4400570/hYmS8Qp1xL.json")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Layout: Animation on left, Login on right
        left_col, right_col = st.columns([1, 1])
        
        with left_col:
            # ONLY render if lottie_fitness is NOT None
            if lottie_fitness:
                st_lottie(lottie_fitness, height=400, key="fitness_anim")
            else:
                # Fallback: Show a nice static image or just a header if no internet
                st.info("🧬 BioPulse-AI: Neural Network Active")
        
        with right_col:
            # ... (Rest of your login tab logic stays exactly the same)
            st.title("Welcome Back")
            # [Your existing tab1 and tab2 code here]