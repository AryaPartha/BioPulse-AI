from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session
from parser import parse_gym_log
from utils import logger, get_muscle_group

# Updated Schema with Muscle Group
class GymLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exercise: str
    muscle_group: str  # New Field added in Week 2
    weight: int
    sets: int
    reps: int
    total_volume: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

sqlite_file_name = "data/biopulse.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def save_log(raw_text: str, exercise_name: str):
    parsed_data = parse_gym_log(raw_text)
    
    if parsed_data:
        new_log = GymLog(
            exercise=exercise_name,
            muscle_group=get_muscle_group(exercise_name), # Auto-tagging
            weight=parsed_data["weight"],
            sets=parsed_data["sets"],
            reps=parsed_data["reps"],
            total_volume=parsed_data["total_volume"]
        )
        
        with Session(engine) as session:
            session.add(new_log)
            session.commit()
            session.refresh(new_log)
            logger.info(f"🚀 Database Saved: {new_log.exercise} ({new_log.muscle_group})")
            return True
    return False

if __name__ == "__main__":
    create_db_and_tables()
    print("✅ Database and Tables created successfully!")