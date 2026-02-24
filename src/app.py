import streamlit as st
import pandas as pd
import plotly.express as px
from main import save_log, GymLog, engine
from sqlmodel import Session, select

# 1. Page Configuration
st.set_page_config(page_title="BioPulse-AI", page_icon="💪", layout="wide")

st.title("💪 BioPulse-AI: Smart Fitness Log")
st.markdown("---")

# 2. Sidebar / Input Section
st.sidebar.header("Log New Activity")
with st.sidebar.form("log_form"):
    exercise_name = st.text_input("Exercise Name", placeholder="e.g., Bench Press")
    raw_log = st.text_input("Log Details", placeholder="e.g., 80kg for 3 sets of 10")
    submit_button = st.form_submit_button("Save Entry")

if submit_button:
    if exercise_name and raw_log:
        try:
            save_log(raw_log, exercise_name)
            st.sidebar.success(f"Saved {exercise_name}!")
            # Reruns the app to refresh the table and chart
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Please fill in both fields.")

# 3. Main Dashboard Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📜 Recent History")
    with Session(engine) as session:
        statement = select(GymLog).order_by(GymLog.timestamp.desc())
        results = session.exec(statement).all()
        
        if results:
            # Converting to DataFrame for a cleaner look in Streamlit
            data_list = [log.model_dump() for log in results]
            df_history = pd.DataFrame(data_list)
            # Reordering columns for better readability
            df_history = df_history[["timestamp", "exercise", "weight", "sets", "reps", "total_volume"]]
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("No logs found. Start your workout!")

with col2:
    st.header("📈 Progress Analytics")
    with Session(engine) as session:
        statement = select(GymLog).order_by(GymLog.timestamp)
        results = session.exec(statement).all()
        
        if results:
            data_list = [log.model_dump() for log in results]
            df_charts = pd.DataFrame(data_list)
            
            # Creating the Progressive Overload Chart
            fig = px.line(
                df_charts, 
                x="timestamp", 
                y="total_volume", 
                color="exercise",
                title="Total Volume Trend (Weight x Sets x Reps)",
                markers=True,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Log more data to visualize your gains.")