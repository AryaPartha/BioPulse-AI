import logging
import os
import pandas as pd

# Professional Logging Setup
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intelligence Layer: Exercise to Muscle Group Mapping
EXERCISE_MAPPING = {
    "bench press": "Chest",
    "pushups": "Chest",
    "squat": "Legs",
    "leg press": "Legs",
    "deadlift": "Back",
    "pullups": "Back",
    "overhead press": "Shoulders",
    "bicep curl": "Arms",
    "tricep": "Arms"
}

def get_muscle_group(exercise_name):
    """Categorizes an exercise into its target muscle group."""
    exercise_name = exercise_name.lower()
    for key, value in EXERCISE_MAPPING.items():
        if key in exercise_name:
            return value
    return "Other"

def predict_next_weight(history_df, exercise_name):
    """Suggests the next weight based on recent trends."""
    if history_df.empty:
        return "Log your first session!"
    exercise_data = history_df[history_df['exercise'].str.lower() == exercise_name.lower()]
    if len(exercise_data) < 1:
        return "New exercise detected! Let's set a baseline."
    latest_weight = exercise_data.iloc[0]['weight']
    return f"Target {latest_weight + 2.5}kg for your next set!"

def calculate_relative_strength(lift_weight, body_weight=79):
    """Calculates strength-to-weight ratio (Lift / 79kg)."""
    return round(lift_weight / body_weight, 2)