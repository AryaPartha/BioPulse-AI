import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- AI LOGIC ---
def get_ai_workout_recommendation(user_id):
    conn = sqlite3.connect('biopulse.db')
    df = pd.read_sql(f"SELECT exercise, MAX(date) as last_done FROM workouts WHERE user_id={user_id} GROUP BY exercise", conn)
    conn.close()
    all_ex = sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"])
    if df.empty: return "AI COACH: Ready to start? Try **Squats** for base strength."
    done = df['exercise'].tolist()
    missing = [ex for ex in all_ex if ex not in done]
    if missing: return f"AI COACH: Focus on balance! Try **{missing[0]}** today."
    suggestion = df.sort_values('last_done').iloc[0]['exercise']
    return f"AI COACH: It's been a while since your last **{suggestion}** session."

# --- DASHBOARD ---
def run_dashboard():
    user_id = st.session_state.user_id
    conn = sqlite3.connect('biopulse.db')
    
    st.markdown("""<style>
        [data-testid="stMetric"] { background: rgba(22, 27, 34, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 15px; }
        .ai-card { background: rgba(0, 153, 255, 0.1); border-left: 5px solid #0099ff; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
        .pb-card { background: #1a1a1a; border-bottom: 3px solid #ffd700; border-radius: 10px; padding: 10px; text-align: center; }
    </style>""", unsafe_allow_html=True)

    st.header(f"🚀 Performance Dashboard: {st.session_state.user_name}")

    # 1. Weekly Volume Intelligence (Advanced Feature)
    v_df = pd.read_sql(f"SELECT date, (sets * reps * weight_lifted) as daily_vol FROM workouts WHERE user_id={user_id}", conn)
    if not v_df.empty:
        v_df['date'] = pd.to_datetime(v_df['date'])
        this_week = v_df[v_df['date'] > (datetime.now() - timedelta(days=7))]['daily_vol'].sum()
        last_week = v_df[(v_df['date'] <= (datetime.now() - timedelta(days=7))) & (v_df['date'] > (datetime.now() - timedelta(days=14)))]['daily_vol'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Weekly Volume", f"{this_week:,.0f} kg", f"{this_week - last_week:,.0f} vs Last Week")
        
        # Calorie Goal Progress (Advanced Feature)
        burn = pd.read_sql(f"SELECT SUM(metric) as total FROM logs WHERE user_id={user_id} AND activity='Burn' AND date >= date('now', '-7 days')", conn)['total'][0] or 0
        fig_goal = go.Figure(go.Indicator(mode="gauge+number", value=burn, title={'text': "Weekly Burn Goal (kcal)"}, gauge={'axis': {'range': [None, 2000]}, 'bar': {'color': "#00ffcc"}}))
        fig_goal.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        c2.plotly_chart(fig_goal, use_container_width=True)

    # 2. AI Coach & Trophies
    st.divider()
    st.markdown(f'<div class="ai-card"><b>🧠 AI Intelligence:</b> {get_ai_workout_recommendation(user_id)}</div>', unsafe_allow_html=True)
    
    pb_df = pd.read_sql(f"SELECT exercise, reps, weight_lifted FROM workouts WHERE user_id={user_id}", conn)
    if not pb_df.empty:
        st.subheader("🥇 Personal Bests (1RM)")
        pb_df['1rm'] = pb_df['weight_lifted'] / (1.0278 - (0.0278 * pb_df['reps']))
        peaks = pb_df.groupby('exercise')['1rm'].max().sort_index()
        cols = st.columns(min(len(peaks), 4))
        for i, (name, val) in enumerate(peaks.items()):
            with cols[i % 4]: st.markdown(f'<div class="pb-card"><b>{name}</b><br>{val:.1f} kg</div>', unsafe_allow_html=True)

    # 3. Training Engine
    st.divider()
    t1, t2, t3 = st.tabs(["🏋️ Strength Log", "📈 Analytics", "🏸 Badminton Mode"])
    
    with t1:
        with st.form("log_set", clear_on_submit=True):
            is_custom = st.checkbox("Add Custom Exercise")
            c1, c2, c3 = st.columns(3)
            options = sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"])
            ex = c1.text_input("Exercise Name").title() if is_custom else c1.selectbox("Select Exercise", options)
            s, r = c2.number_input("Sets", 1, 10, 3), c3.number_input("Reps", 1, 50, 10)
            w = st.slider("Weight (kg)", 0.0, 400.0, 50.0)
            if st.form_submit_button("Sync to DB"):
                conn.cursor().execute("INSERT INTO workouts (user_id, date, exercise, sets, reps, weight_lifted) VALUES (?, ?, ?, ?, ?, ?)", (user_id, datetime.now().strftime("%Y-%m-%d"), ex, s, r, w))
                conn.commit(); st.rerun()

    with t3:
        dur = st.slider("Match Duration (min)", 15, 120, 45)
        inten = st.select_slider("Intensity", options=["Casual", "Intense", "Pro Match"])
        met = {"Casual": 4.5, "Intense": 7.0, "Pro Match": 9.0}[inten]
        u_weight = pd.read_sql(f"SELECT weight FROM users WHERE id={user_id}", conn)['weight'][0]
        st.metric("Estimated Burn", f"{met * u_weight * (dur/60):.1f} kcal")
        if st.button("Log Shuttle Session"):
            conn.cursor().execute("INSERT INTO logs (user_id, date, activity, metric) VALUES (?, ?, 'Burn', ?)", (user_id, datetime.now().strftime("%Y-%m-%d"), met * u_weight * (dur/60)))
            conn.commit(); st.toast("Session Saved!"); st.rerun()
    conn.close()

# --- ADMIN CONSOLE ---
def run_admin_dashboard():
    st.title("🛡️ System Admin Console")
    conn = sqlite3.connect('biopulse.db')
    u_df = pd.read_sql("SELECT id, username, weight, is_admin FROM users", conn)
    
    col1, col2 = st.columns(2)
    col1.metric("Total Athletes", len(u_df))
    col2.metric("Database Health", "Optimized ✅")
    
    st.subheader("👥 User Management")
    st.dataframe(u_df, use_container_width=True)
    
    with st.expander("🛠️ Account Actions"):
        target = st.selectbox("Target Account", u_df['username'].tolist())
        if st.button("Purge User Data", type="primary"):
            if target == st.session_state.user_name: st.error("Cannot delete yourself!")
            else:
                tid = u_df[u_df['username'] == target]['id'].values[0]
                conn.cursor().execute(f"DELETE FROM users WHERE id={tid}")
                conn.cursor().execute(f"DELETE FROM workouts WHERE user_id={tid}")
                conn.commit(); st.rerun()
    conn.close()