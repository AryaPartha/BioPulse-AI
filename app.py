import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_ai_workout_recommendation(user_id):
    conn = sqlite3.connect('biopulse.db')
    df = pd.read_sql(f"SELECT exercise, MAX(date) as last_done FROM workouts WHERE user_id={user_id} GROUP BY exercise", conn)
    conn.close()
    all_ex = sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"])
    if df.empty: return "AI COACH: Start with **Squats** to initialize your profile."
    missing = [ex for ex in all_ex if ex not in df['exercise'].tolist()]
    if missing: return f"AI COACH: Balance is key! Try **{missing[0]}** next."
    suggestion = df.sort_values('last_done').iloc[0]['exercise']
    return f"AI COACH: It's time to revisit **{suggestion}**."

def run_dashboard():
    user_id = st.session_state.user_id
    conn = sqlite3.connect('biopulse.db')
    
    st.markdown("""<style>
        [data-testid="stMetric"] { background: rgba(22, 27, 34, 0.7); border-radius: 12px; padding: 15px; }
        .ai-card { background: rgba(0, 153, 255, 0.1); border-left: 5px solid #0099ff; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
        .pb-card { background: #1a1a1a; border-bottom: 3px solid #ffd700; border-radius: 10px; padding: 10px; text-align: center; }
    </style>""", unsafe_allow_html=True)

    st.header(f"🚀 Performance: {st.session_state.user_name}")

    # --- ENHANCED ANALYTICS SECTION ---
    vol_query = f"SELECT date, (sets * reps * weight_lifted) as daily_vol FROM workouts WHERE user_id={user_id}"
    v_df = pd.read_sql(vol_query, conn)
    
    if not v_df.empty:
        st.subheader("📊 Volume & Activity Intelligence")
        c1, c2 = st.columns(2)
        
        # Volume Logic
        total_vol = v_df['daily_vol'].sum()
        c1.metric("Lifetime Volume Moved", f"{total_vol:,.0f} kg")
        
        # Activity Goal Gauge
        burn = pd.read_sql(f"SELECT SUM(metric) as total FROM logs WHERE user_id={user_id} AND activity='Burn'", conn)['total'][0] or 0
        fig_goal = go.Figure(go.Indicator(mode="gauge+number", value=burn, title={'text': "Activity Burn (kcal)"}, gauge={'axis': {'range': [None, 2000]}, 'bar': {'color': "#00ffcc"}}))
        fig_goal.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        c2.plotly_chart(fig_goal, use_container_width=True)
    
    # AI Coach & Trophies
    st.markdown(f'<div class="ai-card"><b>🧠 AI Strategy:</b> {get_ai_workout_recommendation(user_id)}</div>', unsafe_allow_html=True)
    
    pb_df = pd.read_sql(f"SELECT exercise, reps, weight_lifted FROM workouts WHERE user_id={user_id}", conn)
    if not pb_df.empty:
        pb_df['1rm'] = pb_df['weight_lifted'] / (1.0278 - (0.0278 * pb_df['reps']))
        peaks = pb_df.groupby('exercise')['1rm'].max().sort_index()
        cols = st.columns(min(len(peaks), 4))
        for i, (name, val) in enumerate(peaks.items()):
            with cols[i % 4]: st.markdown(f'<div class="pb-card"><b>{name}</b><br>{val:.1f} kg</div>', unsafe_allow_html=True)

    st.divider()
    t1, t2, t3 = st.tabs(["🏋️ Gym Log", "📈 Strength Analytics", "🏸 Badminton"])
    
    with t1:
        with st.form("gym", clear_on_submit=True):
            custom = st.checkbox("Custom")
            c1, c2, c3 = st.columns(3)
            ex = c1.text_input("Name").title() if custom else c1.selectbox("Exercise", sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"]))
            s, r = c2.number_input("Sets", 1, 10, 3), c3.number_input("Reps", 1, 50, 10)
            w = st.slider("Weight (kg)", 0.0, 300.0, 50.0)
            if st.form_submit_button("Log Set"):
                conn.cursor().execute("INSERT INTO workouts (user_id, date, exercise, sets, reps, weight_lifted) VALUES (?, ?, ?, ?, ?, ?)", (user_id, datetime.now().strftime("%Y-%m-%d"), ex, s, r, w))
                conn.commit(); st.rerun()

    with t2:
        if not pb_df.empty:
            fig = px.line(pb_df, x='exercise', y='1rm', title="Strength Profile", markers=True, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    with t3:
        dur = st.slider("Duration (min)", 15, 120, 45)
        inten = st.select_slider("Intensity", options=["Casual", "Intense", "Pro Match"])
        met = {"Casual": 4.5, "Intense": 7.0, "Pro Match": 9.0}[inten]
        u_w = pd.read_sql(f"SELECT weight FROM users WHERE id={user_id}", conn)['weight'][0]
        burn_val = met * u_w * (dur/60)
        st.metric("Estimated Burn", f"{burn_val:.1f} kcal")
        if st.button("Log Match"):
            conn.cursor().execute("INSERT INTO logs (user_id, date, activity, metric) VALUES (?, ?, 'Burn', ?)", (user_id, datetime.now().strftime("%Y-%m-%d"), burn_val))
            conn.commit(); st.rerun()
    conn.close()

def run_admin_dashboard():
    st.title("🛡️ Admin Console")
    conn = sqlite3.connect('biopulse.db')
    u_df = pd.read_sql("SELECT id, username, is_admin FROM users", conn)
    st.metric("Total Athletes", len(u_df))
    st.dataframe(u_df, use_container_width=True)
    target = st.selectbox("Select User to Purge", u_df['username'].tolist())
    if st.button("Delete User", type="primary"):
        tid = u_df[u_df['username'] == target]['id'].values[0]
        conn.cursor().execute(f"DELETE FROM users WHERE id={tid}")
        conn.commit(); st.rerun()
    conn.close()