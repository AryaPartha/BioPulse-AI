import logging
import os

# Professional Logging Setup
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- NEW: Week 2 Intelligence Layer ---
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