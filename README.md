# Cric Squad Selector

An intelligent cricket squad selection web application powered by Machine Learning. 

This application uses historical match data, player statistics, and machine learning models (Random Forest and XGBoost) to predict player performance and automatically generate the optimal 11-man squad for a given format and opposition.

## Key Features

- **AI Squad Generation**: Predicts the best 11-man squad tailored to match format and opposition using ML.
- **Player Form Dashboard**: Search for active players to view career stats, dynamic form charts, and an ML Profile Strength rating.
- **Selection Confidence**: View the ML confidence score and reasoning behind each selected player.
- **Saved Squads**: Securely register, log in, and save your generated squads to your personal dashboard.

## Tech Stack

- **Backend**: Python, Flask
- **Machine Learning**: Scikit-learn (Random Forest), XGBoost, Pandas, NumPy
- **Database**: SQLite (managed with SQLAlchemy)
- **Authentication**: Flask-Login, Werkzeug Security
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript, Chart.js

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abdullahminhas/cric-squad-selector.git
   cd cric-squad-selector
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   *(Ensure you have `pandas`, `flask`, `flask-sqlalchemy`, `flask-login`, `scikit-learn`, `xgboost`, and `joblib` installed).*

4. **Initialize the database and run the app:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   Navigate to `http://127.0.0.1:5000/`

## Project Architecture

- **`app.py`**: The main Flask entry point. Sets up the server, database, and routing.
- **`ml_utils.py`**: The core ML engine. Loads serialized models and generates squads with confidence scores.
- **`squad_api.py`**: The backend API for squad generation, dashboard stats, and saving squads.
- **`auth.py`**: Handles user registration, login, and secure session management.
- **`models.py`**: Defines the SQLite database schema (`User` and `SavedSquad` tables).