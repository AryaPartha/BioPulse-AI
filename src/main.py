import streamlit as st
from database import init_db, add_user, verify_user
from app import run_dashboard

# Initialize the SQLite database on startup
init_db()

st.set_page_config(page_title="BioPulse-AI", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for UI/UX (Week 1 Roadmap)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00ffcc; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e3136; color: white; }
    </style>
    """, unsafe_allow_value=True)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🧬 BioPulse-AI")
        st.subheader("Predictive Health & Fitness Intelligence")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Password", type="password", key="login_pw")
            if st.button("Access Dashboard"):
                user_data = verify_user(u, p)
                if user_data:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user_data[0]
                    st.session_state['user_name'] = user_data[1]
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with tab2:
            new_u = st.text_input("Choose Username")
            new_p = st.text_input("Choose Password", type="password")
            weight = st.number_input("Current Weight (kg)", min_value=30.0, value=75.0)
            if st.button("Register"):
                if add_user(new_u, new_p, weight):
                    st.success("Account created! You can now log in.")
                else:
                    st.error("Username already exists.")
    else:
        # User is authenticated
        with st.sidebar:
            st.title(f"Welcome, {st.session_state['user_name']}!")
            st.divider()
            if st.button("Log Out"):
                st.session_state['logged_in'] = False
                st.rerun()
        
        run_dashboard()

if __name__ == "__main__":
    main()