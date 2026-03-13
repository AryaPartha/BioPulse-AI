import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

def get_ai_workout_recommendation(user_id):
    conn = sqlite3.connect('biopulse.db')
    df = pd.read_sql(f"SELECT exercise, MAX(date) as last_done FROM workouts WHERE user_id={user_id} GROUP BY exercise", conn)
    conn.close()
    all_ex = sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"])
    if df.empty: return "AI Suggests: Start with **Squats** for a strong foundation."
    missing = [ex for ex in all_ex if ex not in df['exercise'].tolist()]
    if missing: return f"AI Suggests: Try **{missing[0]}** for balanced growth."
    suggestion = df.sort_values('last_done').iloc[0]['exercise']
    return f"AI Insight: It's been a while since you did **{suggestion}**. Time to hit it!"

def run_dashboard():
    user_id = st.session_state.user_id
    st.markdown("""<style>
        .ai-card { background: rgba(0, 153, 255, 0.1); border-left: 5px solid #0099ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .pb-card { background: #1a1a1a; border-bottom: 3px solid #ffd700; border-radius: 10px; padding: 10px; text-align: center; }
    </style>""", unsafe_allow_html=True)

    st.header(f"🏆 {st.session_state.user_name}'s Dashboard")
    
    # 1. AI Recommendation
    rec = get_ai_workout_recommendation(user_id)
    st.markdown(f'<div class="ai-card"><b>🧠 AI Strategy:</b> {rec}</div>', unsafe_allow_html=True)

    # 2. Trophy Cabinet
    conn = sqlite3.connect('biopulse.db')
    pb_df = pd.read_sql(f"SELECT exercise, reps, weight_lifted FROM workouts WHERE user_id={user_id}", conn)
    if not pb_df.empty:
        pb_df['1rm'] = pb_df['weight_lifted'] / (1.0278 - (0.0278 * pb_df['reps']))
        peaks = pb_df.groupby('exercise')['1rm'].max().sort_index()
        cols = st.columns(min(len(peaks), 4))
        for i, (name, val) in enumerate(peaks.items()):
            with cols[i % 4]: st.markdown(f'<div class="pb-card"><b>{name}</b><br>{val:.1f} kg</div>', unsafe_allow_html=True)

    # 3. Main Interface
    st.divider()
    t1, t2, t3 = st.tabs(["🏋️ Gym", "📈 Analytics", "🏸 Badminton"])
    
    with t1:
        with st.form("gym"):
            custom = st.checkbox("Custom")
            c1, c2, c3 = st.columns(3)
            ex = c1.text_input("Name").title() if custom else c1.selectbox("Exercise", sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"]))
            s, r = c2.number_input("Sets", 1, 10, 3), c3.number_input("Reps", 1, 50, 10)
            w = st.slider("Weight (kg)", 0.0, 300.0, 50.0)
            if st.form_submit_button("Log Set"):
                conn.cursor().execute("INSERT INTO workouts (user_id, date, exercise, sets, reps, weight_lifted) VALUES (?, ?, ?, ?, ?, ?)", (user_id, datetime.now().strftime("%Y-%m-%d"), ex, s, r, w))
                conn.commit(); st.rerun()

    with t3:
        dur = st.slider("Duration (min)", 15, 120, 45)
        inten = st.select_slider("Intensity", options=["Casual", "Intense", "Pro Match"])
        met = {"Casual": 4.5, "Intense": 7.0, "Pro Match": 9.0}[inten]
        u_w = pd.read_sql(f"SELECT weight FROM users WHERE id={user_id}", conn)['weight'][0]
        burn = met * u_w * (dur/60)
        st.metric("Burned", f"{burn:.1f} kcal")
    conn.close()

def run_admin_dashboard():
    st.title("🛡️ System Admin")
    conn = sqlite3.connect('biopulse.db')
    u_count = pd.read_sql("SELECT COUNT(*) as c FROM users", conn)['c'][0]
    w_count = pd.read_sql("SELECT COUNT(*) as c FROM workouts", conn)['c'][0]
    st.metric("Total Athletes", u_count)
    st.metric("Total Logs", w_count)
    pop = pd.read_sql("SELECT exercise, COUNT(*) as c FROM workouts GROUP BY exercise", conn)
    st.bar_chart(pop.set_index('exercise'))
    conn.close()