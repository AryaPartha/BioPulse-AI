# 💪 BioPulse-AI: Smart Fitness & Cardio Ecosystem

**Developer:** Partha S. (Final Year CS & Design Engineering)  
**Location:** Mysuru, Karnataka  
**Live App:** (https://biopulse-ai-kmga6ruzkhx4zhapngpc6p.streamlit.app)

## 🚀 Overview
BioPulse-AI is a comprehensive, data-driven fitness assistant designed to bridge the gap between strength training and cardio. Built using Python 3.14, it utilizes NLP parsing to turn messy human logs into actionable insights.

## ✨ Key Features
* **Intelligent NLP Parsing:** Automatically extracts Weight, Sets, and Reps from natural language logs (e.g., "80kg 3x12").
* **Muscle Group Intelligence:** Categorizes exercises (Chest, Legs, Back, etc.) and visualizes training distribution.
* **AI Progression Tips:** Suggests "Progressive Overload" targets based on historical performance.
* **Personalized Metrics:** Calculates "Relative Strength" ratios based on the developer's 79kg body weight.
* **Badminton Tracker:** A dedicated module for duration-based cardio and shuttle matches.
* **Data Portability:** Full CSV export functionality for offline analysis.

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python)
* **Database:** SQLModel (SQLite) with SQLAlchemy ORM
* **Visualization:** Plotly Express
* **DevOps:** GitHub, Streamlit Cloud, Dotenv for secret management

## 📦 Local Setup
1. Clone the repo: `git clone https://github.com/YOAryaPartha/BioPulse-AI.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize Database: `python src/main.py`
4. Run App: `streamlit run src/app.py`