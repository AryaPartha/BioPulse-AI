import streamlit as st
import pandas as pd
import plotly.express as px
from main import save_log, GymLog, ExerciseGoal, CardioLog, engine
from sqlmodel import Session, select
from utils import predict_next_weight, calculate_relative_strength

# 1. Page Configuration
st.set_page_config(page_title="BioPulse-AI | Partha S.", page_icon="💪", layout="wide")

# Dashboard Header
st.title("💪 BioPulse-AI: Smart Fitness Log")
st.markdown("---")

# 2. Data Retrieval
with Session(engine) as session:
    gym_results = session.exec(select(GymLog).order_by(GymLog.timestamp.desc())).all()
    df = pd.DataFrame([log.model_dump() for log in gym_results]) if gym_results else pd.DataFrame()
    
    cardio_results = session.exec(select(CardioLog).order_by(CardioLog.timestamp.desc())).all()
    cardio_df = pd.DataFrame([c.model_dump() for c in cardio_results]) if cardio_results else pd.DataFrame()

# 3. --- SIDEBAR: Profile & Controls ---
st.sidebar.markdown(f"### 🧑‍💻 Developer: Partha S.")
st.sidebar.caption("Final Year CS & Design Engineering")
st.sidebar.markdown(f"**Current Weight:** 79 kg | **Focus:** Muscle Building")
st.sidebar.divider()

# Sidebar: Goal Setting
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

# Sidebar: CSV Export
st.sidebar.divider()
st.sidebar.header("📂 Data Export")
if not df.empty:
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Download History (CSV)", csv_data, "BioPulse_History.csv", "text/csv")

# 4. --- MAIN DASHBOARD: TABS ---
gym_tab, cardio_tab = st.tabs(["🏋️ Gym & Strength", "🏸 Cardio & Badminton"])

with gym_tab:
    # Sidebar-like entry form for Gym within the tab
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

    # Visuals
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

    # Goals & Distribution
    st.divider()
    g_col, p_col = st.columns(2)
    with g_col:
        st.subheader("🏆 Goal Progress")
        with Session(engine) as session:
            goals = session.exec(select(ExerciseGoal)).all()
            for goal in goals:
                latest = df[df['exercise'].str.lower() == goal.exercise.lower()]
                if not latest.empty:
                    prog = min(latest.iloc[0]['weight'] / goal.target_weight, 1.0)
                    st.write(f"**{goal.exercise}** ({latest.iloc[0]['weight']} / {goal.target_weight}kg)")
                    st.progress(prog)
    with p_col:
        st.subheader("🎯 Muscle Split")
        if not df.empty:
            fig_p = px.pie(df, names='muscle_group', hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_p, use_container_width=True)

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