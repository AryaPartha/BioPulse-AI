import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime
from sklearn.linear_model import LinearRegression

def get_user_data(user_id):
    conn = sqlite3.connect('biopulse.db')
    df = pd.read_sql(f"SELECT date, metric FROM logs WHERE user_id = {user_id} AND activity = 'Weight' ORDER BY date ASC", conn)
    conn.close()
    return df

def save_log(user_id, activity, metric):
    conn = sqlite3.connect('biopulse.db')
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO logs (user_id, date, activity, metric) VALUES (?, ?, ?, ?)", 
              (user_id, today, activity, metric))
    conn.commit()
    conn.close()

def run_dashboard():
    user_id = st.session_state['user_id']
    
    # 1. Dashboard Header
    st.header("Personal Health Insights")
    df = get_user_data(user_id)

    # 2. Key Metrics
    col1, col2, col3 = st.columns(3)
    current_weight = df['metric'].iloc[-1] if not df.empty else 0.0
    col1.metric("Current Weight", f"{current_weight} kg")
    
    # 3. AI Prediction Logic (Scikit-Learn)
    st.subheader("🤖 AI Weight Trend Forecast")
    if len(df) > 1:
        # Convert dates to ordinal for regression
        df['date_dt'] = pd.to_datetime(df['date'])
        df['ordinal'] = df['date_dt'].map(datetime.toordinal)
        
        X = df['ordinal'].values.reshape(-1, 1)
        y = df['metric'].values
        model = LinearRegression().fit(X, y)
        
        # Predict 7 days from now
        future_date = datetime.now().toordinal() + 7
        prediction = model.predict([[future_date]])[0]
        
        st.info(f"AI Forecast: You are on track to reach **{prediction:.2f} kg** in 7 days.")
        
        fig = px.line(df, x='date', y='metric', title="Your Progress Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Log your weight for at least 2 days to activate AI Forecasting.")

    st.divider()

    # 4. Badminton Tracker
    st.subheader("🏸 Badminton Session Tracker")
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        duration = st.slider("Duration (mins)", 15, 120, 45)
        intensity = st.select_slider("Intensity", options=["Casual", "Competitive"])
    with b_col2:
        met = 7.0 if intensity == "Competitive" else 4.5
        # Calories = MET * weight_kg * duration_hrs
        calories = met * (current_weight if current_weight > 0 else 75) * (duration / 60)
        st.write(f"Estimated Burn: **{calories:.1f} kcal**")
        if st.button("Log Session"):
            save_log(user_id, "Badminton_Kcal", calories)
            st.success("Session saved!")

    # 5. Daily Logging
    with st.expander("📝 Manual Daily Log"):
        new_w = st.number_input("Enter Today's Weight (kg)", format="%.2f")
        if st.button("Update Weight"):
            save_log(user_id, "Weight", new_w)
            st.rerun()