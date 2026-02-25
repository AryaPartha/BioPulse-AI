import os
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
from parser import parse_gym_log
from utils import logger, get_muscle_group
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GymLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exercise: str
    muscle_group: str  
    weight: int
    sets: int
    reps: int
    total_volume: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ExerciseGoal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exercise: str = Field(index=True, unique=True)
    target_weight: int

class CardioLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity: str 
    duration_mins: int
    intensity: str 
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Use environment variable or fallback to local sqlite
sqlite_url = os.getenv("DATABASE_URL", "sqlite:///data/biopulse.db")
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def save_log(raw_text: str, exercise_name: str):
    parsed_data = parse_gym_log(raw_text)
    if parsed_data:
        new_log = GymLog(
            exercise=exercise_name,
            muscle_group=get_muscle_group(exercise_name), 
            weight=parsed_data["weight"],
            sets=parsed_data["sets"],
            reps=parsed_data["reps"],
            total_volume=parsed_data["total_volume"]
        )
        with Session(engine) as session:
            session.add(new_log)
            session.commit()
            session.refresh(new_log)
            logger.info(f"🚀 Gym Log Saved: {new_log.exercise}")
            return True
    return False

if __name__ == "__main__":
    create_db_and_tables()
    print("✅ System ready for Cloud Deployment!")