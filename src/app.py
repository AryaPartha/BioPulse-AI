import streamlit as st
import pandas as pd
import plotly.express as px
import os
from main import save_log, GymLog, ExerciseGoal, CardioLog, engine
from rag_engine import process_fitness_pdf, ask_rag_ai
from sqlmodel import Session, select
from utils import predict_next_weight, calculate_relative_strength

# Page Configuration
st.set_page_config(page_title="BioPulse-AI | Partha S.", page_icon="💪", layout="wide")

st.title("💪 BioPulse-AI: Smart Fitness & RAG Insight")
st.markdown("---")

# Data Retrieval from SQLite
with Session(engine) as session:
    gym_results = session.exec(select(GymLog).order_by(GymLog.timestamp.desc())).all()
    df = pd.DataFrame([log.model_dump() for log in gym_results]) if gym_results else pd.DataFrame()
    
    cardio_results = session.exec(select(CardioLog).order_by(CardioLog.timestamp.desc())).all()
    cardio_df = pd.DataFrame([c.model_dump() for c in cardio_results]) if cardio_results else pd.DataFrame()

# --- SIDEBAR: Profile & Settings ---
st.sidebar.markdown(f"### 🧑‍💻 Developer: Partha S.")
st.sidebar.caption("Final Year CS & Design Engineering")
st.sidebar.markdown(f"**Current Weight:** 79 kg | **Focus:** Muscle Building")
st.sidebar.divider()

# Goal Setting Form
st.sidebar.header("🎯 Set a Goal")
with st.sidebar.form("goal_form"):
    goal_ex = st.text_input("Exercise", placeholder="Squat")
    target = st.number_input("Target Weight (kg)", min_value=1)
    if st.form_submit_button("Set Goal"):
        with Session(engine) as session:
            existing = session.exec(select(ExerciseGoal).where(ExerciseGoal.exercise == goal_ex)).first()
            if existing: existing.target_weight = target
            else: session.add(ExerciseGoal(exercise=goal_ex, target_weight=target))
            session.commit()
            st.rerun()

# --- MAIN DASHBOARD: TABS ---
gym_tab, cardio_tab, rag_tab = st.tabs(["🏋️ Gym & Strength", "🏸 Cardio & Badminton", "🧠 AI Insight (RAG)"])

# TAB 1: GYM LOGGING
with gym_tab:
    with st.expander("➕ Log New Gym Activity", expanded=True):
        col_ex, col_log = st.columns(2)
        with col_ex:
            ex_name = st.text_input("Exercise Name", key="gym_ex")
            if ex_name: st.caption(f"🤖 AI Tip: {predict_next_weight(df, ex_name)}")
        with col_log:
            raw_log = st.text_input("Log Details (e.g., 80kg 3x12)", key="gym_raw")
        if st.button("Save Gym Entry"):
            if save_log(raw_log, ex_name):
                st.success(f"Saved {ex_name}!")
                st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📜 Recent History")
        if not df.empty:
            df['Rel. Strength'] = df['weight'].apply(lambda x: calculate_relative_strength(x))
            st.dataframe(df[["timestamp", "exercise", "weight", "Rel. Strength", "total_volume"]], use_container_width=True)
    with c2:
        st.subheader("📈 Volume Progress")
        if not df.empty:
            fig = px.line(df.sort_values("timestamp"), x="timestamp", y="total_volume", color="exercise", markers=True, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# TAB 2: CARDIO & BADMINTON
with cardio_tab:
    st.header("🏸 Badminton & Cardio Tracking")
    with st.form("cardio_form"):
        act = st.selectbox("Activity", ["Badminton", "Running", "Swimming"])
        dur = st.number_input("Duration (mins)", min_value=1, value=60)
        inten = st.select_slider("Intensity", options=["Low", "Moderate", "High"])
        if st.form_submit_button("Log Session"):
            with Session(engine) as session:
                session.add(CardioLog(activity=act, duration_mins=dur, intensity=inten))
                session.commit()
                st.success("Session Logged!")
                st.rerun()
    
    if not cardio_df.empty:
        st.subheader("🏸 Cardio History")
        st.table(cardio_df[["timestamp", "activity", "duration_mins", "intensity"]])

# TAB 3: AI INSIGHT (RAG)
with rag_tab:
    st.header("🧠 Intelligent Document Insight")
    st.info("Upload a fitness PDF or badminton guide to query it using the RAG engine.")
    
    pdf_file = st.file_uploader("Upload Training PDF (Research, Guides, or Plans)", type="pdf")
    
    if pdf_file:
        # Save temporary file for processing
        with open("temp_rag.pdf", "wb") as f:
            f.write(pdf_file.getbuffer())
        
        with st.spinner("Analyzing document and building Vector DB..."):
            # Uses HuggingFace Embeddings + FAISS
            st.session_state.vdb = process_fitness_pdf("temp_rag.pdf")
            st.success("Knowledge Base Ready! You can now ask questions.")
            
    query = st.text_input("Ask the AI about the document:")
    if query:
        if 'vdb' in st.session_state:
            with st.spinner("Retrieving insights..."):
                # Uses Groq Llama 3 for free-tier inference
                response = ask_rag_ai(st.session_state.vdb, query)
                st.markdown(f"### 🤖 AI Insight:\n{response}")
        else:
            st.warning("Please upload a PDF first to enable the AI Insight engine.")