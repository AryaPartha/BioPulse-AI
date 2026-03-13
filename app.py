import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

# --- AI LOGIC: MUSCLE GROUP RECOMMENDER ---
def get_ai_workout_recommendation(user_id):
    conn = sqlite3.connect('biopulse.db')
    query = f"SELECT exercise, MAX(date) as last_done FROM workouts WHERE user_id = {user_id} GROUP BY exercise"
    df = pd.read_sql(query, conn)
    conn.close()
    
    all_ex = sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"])
    if df.empty: 
        return "Welcome! AI suggests starting with **Squats** to build a strong foundation."
    
    done = df['exercise'].tolist()
    missing = [ex for ex in all_ex if ex not in done]
    if missing: 
        return f"Focus on balance! You haven't logged **{missing[0]}** yet. Try it today."
    
    df['last_done'] = pd.to_datetime(df['last_done'])
    suggestion = df.sort_values('last_done').iloc[0]['exercise']
    return f"AI Insight: It's been a while since you did **{suggestion}**. Time to hit it today!"

def run_dashboard():
    user_id = st.session_state.user_id
    
    st.markdown("""<style>
        [data-testid="stMetric"] { background: rgba(22, 27, 34, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 15px; }
        .ai-card { background: rgba(0, 153, 255, 0.1); border-left: 5px solid #0099ff; border-radius: 10px; padding: 20px; margin-bottom: 25px; }
        .pb-card { background: #1a1a1a; border-bottom: 3px solid #ffd700; border-radius: 10px; padding: 10px; text-align: center; }
    </style>""", unsafe_allow_html=True)

    st.header(f"🏆 BioPulse Elite: {st.session_state.user_name}")

    # --- 1. AI RECOMMENDATION & HEALTH FORECAST ---
    col_ai, col_health = st.columns([1, 1])
    
    with col_ai:
        rec = get_ai_workout_recommendation(user_id)
        st.markdown(f'<div class="ai-card"><h4 style="margin:0; color:#0099ff;">🧠 AI Strategy</h4><p>{rec}</p></div>', unsafe_allow_html=True)

    with col_health:
        conn = sqlite3.connect('biopulse.db')
        df_weight = pd.read_sql(f"SELECT metric FROM logs WHERE user_id = {user_id} AND activity = 'Weight' ORDER BY date ASC", conn)
        if len(df_weight) > 3:
            model = SimpleExpSmoothing(df_weight['metric'].values, initialization_method="estimated").fit(smoothing_level=0.7)
            forecast = model.forecast(7)[-1]
            st.metric("AI 7-Day Weight Forecast", f"{forecast:.2f} kg")
        else:
            st.info("Log 4 weight entries to unlock AI Forecasting.")

    # --- 2. TROPHY CABINET ---
    pb_df = pd.read_sql(f"SELECT exercise, reps, weight_lifted FROM workouts WHERE user_id = {user_id}", conn)
    if not pb_df.empty:
        st.subheader("🥇 Personal Bests (1RM)")
        pb_df['1rm'] = pb_df['weight_lifted'] / (1.0278 - (0.0278 * pb_df['reps']))
        peaks = pb_df.groupby('exercise')['1rm'].max().sort_index().tail(4)
        cols = st.columns(len(peaks))
        for i, (ex_name, val) in enumerate(peaks.items()):
            with cols[i]:
                st.markdown(f'<div class="pb-card"><b>{ex_name}</b><br>{val:.1f} kg</div>', unsafe_allow_html=True)

    # --- 3. MAIN INTERFACE TABS ---
    st.divider()
    t1, t2, t3 = st.tabs(["🏋️ Gym Log", "📈 Analytics", "🏸 Badminton Mode"])
    
    with t1:
        with st.form("gym_form", clear_on_submit=True):
            is_custom = st.checkbox("Custom Exercise")
            c1, c2, c3 = st.columns(3)
            default_ex = sorted(["Bench Press", "Squat", "Deadlift", "Overhead Press", "Pull-ups"])
            ex = c1.text_input("Name").strip().title() if is_custom else c1.selectbox("Exercise", default_ex)
            s = c2.number_input("Sets", 1, 10, 3)
            r = c3.number_input("Reps", 1, 50, 10)
            lw = st.slider("Weight (kg)", 0.0, 300.0, 50.0)
            if st.form_submit_button("Log Set"):
                conn.cursor().execute("INSERT INTO workouts (user_id, date, exercise, sets, reps, weight_lifted) VALUES (?, ?, ?, ?, ?, ?)",
                                   (user_id, datetime.now().strftime("%Y-%m-%d"), ex, s, r, lw))
                conn.commit()
                st.success(f"Logged {ex}!")
                st.rerun()

    with t2:
        w_df = pd.read_sql(f"SELECT * FROM workouts WHERE user_id = {user_id}", conn)
        if not w_df.empty:
            target = st.selectbox("Exercise to Analyze", sorted(w_df['exercise'].unique()))
            sub_df = w_df[w_df['exercise'] == target].copy()
            sub_df['1rm'] = sub_df['weight_lifted'] / (1.0278 - (0.0278 * sub_df['reps']))
            fig = px.area(sub_df, x='date', y='1rm', title=f"{target} Peak Strength Curve", template="plotly_dark")
            fig.update_traces(line_color='#00ffcc', fillcolor='rgba(0, 255, 204, 0.1)')
            st.plotly_chart(fig, use_container_width=True)

    with t3:
        st.subheader("🏸 Shuttle Session Tracker")
        c1, c2 = st.columns(2)
        dur = c1.slider("Session Duration (min)", 15, 120, 45)
        intensity = c2.select_slider("Intensity Level", options=["Casual", "Intense", "Pro Match"])
        met = {"Casual": 4.5, "Intense": 7.0, "Pro Match": 9.0}[intensity]
        
        # Calculate burn based on user's current weight
        user_w_query = pd.read_sql(f"SELECT weight FROM users WHERE id = {user_id}", conn)
        current_weight = user_w_query['weight'][0] if not user_w_query.empty else 75.0
        burn = met * current_weight * (dur/60)
        
        st.metric("Estimated Energy Expenditure", f"{burn:.1f} kcal")
        if st.button("Log Badminton Burn"):
            conn.cursor().execute("INSERT INTO logs (user_id, date, activity, metric) VALUES (?, ?, ?, ?)", 
                                 (user_id, datetime.now().strftime("%Y-%m-%d"), "Burn", burn))
            conn.commit()
            st.toast("Match Performance Logged!")

    conn.close()

    with st.sidebar:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- ADMIN DASHBOARD ---
def run_admin_dashboard():
    st.title("🛡️ System Administration")
    conn = sqlite3.connect('biopulse.db')
    c1, c2 = st.columns(2)
    users_df = pd.read_sql("SELECT username FROM users", conn)
    pop_df = pd.read_sql("SELECT exercise, COUNT(*) as count FROM workouts GROUP BY exercise", conn)
    c1.metric("Total Athletes", len(users_df))
    c2.metric("Total Logs", pop_df['count'].sum())
    st.subheader("Global Exercise Popularity")
    st.bar_chart(pop_df.set_index('exercise'))
    conn.close()