import streamlit as st
import pandas as pd
import plotly.express as px
from main import save_log, GymLog, engine
from sqlmodel import Session, select

st.set_page_config(page_title="BioPulse-AI", page_icon="💪", layout="wide")

st.title("💪 BioPulse-AI: Smart Fitness Log")
st.markdown("---")

# Sidebar Input
st.sidebar.header("Log New Activity")
with st.sidebar.form("log_form"):
    exercise_name = st.text_input("Exercise Name", placeholder="e.g., Squat")
    raw_log = st.text_input("Log Details", placeholder="e.g., 80kg 3x12")
    submit_button = st.form_submit_button("Save Entry")

if submit_button and exercise_name and raw_log:
    success = save_log(raw_log, exercise_name)
    if success:
        st.sidebar.success(f"Saved {exercise_name}!")
        st.rerun()
    else:
        st.sidebar.error("Failed to parse log. Try: 80kg 3x10")

# Dashboard Sections
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📜 Recent History")
    with Session(engine) as session:
        statement = select(GymLog).order_by(GymLog.timestamp.desc())
        results = session.exec(statement).all()
        if results:
            df = pd.DataFrame([log.model_dump() for log in results])
            # Added muscle_group to the display
            display_df = df[["timestamp", "exercise", "muscle_group", "weight", "sets", "reps", "total_volume"]]
            st.dataframe(display_df, use_container_width=True)

with col2:
    st.header("📈 Progress Analytics")
    with Session(engine) as session:
        statement = select(GymLog).order_by(GymLog.timestamp)
        results = session.exec(statement).all()
        if results:
            df_charts = pd.DataFrame([log.model_dump() for log in results])
            fig = px.line(df_charts, x="timestamp", y="total_volume", color="exercise", markers=True, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)