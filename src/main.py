from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
from parser import parse_gym_log  # Importing your Day 1 logic

class GymLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exercise: str
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
    # Use your Day 1 parser to get the numbers
    parsed_data = parse_gym_log(raw_text)
    
    # Create the database entry
    new_log = GymLog(
        exercise=exercise_name,
        weight=parsed_data["weight"],
        sets=parsed_data["sets"],
        reps=parsed_data["reps"],
        total_volume=parsed_data["total_volume"]
    )
    
    with Session(engine) as session:
        session.add(new_log)
        session.commit()
        session.refresh(new_log)
        print(f"🚀 Saved: {new_log.exercise} | Total Volume: {new_log.total_volume}")

if __name__ == "__main__":
    create_db_and_tables()
    
    # Let's test a real entry!
    user_input = "I did 100kg bench press for 5 sets of 5 reps"
    save_log(user_input, "Bench Press")