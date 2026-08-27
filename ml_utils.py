import os
import joblib
import logging

import pandas as pd

# Configure basic logging for the ML module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables to hold models and data in memory
model_rf = None
model_xgb = None
ensemble_weight = None
feature_cols = None
max_runs_dict = None
df = None

def load_data():
    """
    Load the master dataset into memory.
    """
    global df
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "master_player_match_features.csv")
    
    try:
        # Load the CSV. For date filtering later, ensure date column is datetime
        df = pd.read_csv(data_path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        logger.info(f"Successfully loaded dataset with {len(df)} rows.")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise

def load_models():
    """
    Load the trained machine learning models and configurations from disk.
    """
    global model_rf, model_xgb, ensemble_weight, feature_cols, max_runs_dict

    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "models")

    try:
        model_rf = joblib.load(os.path.join(models_dir, "squad_generator_rf.pkl"))
        model_xgb = joblib.load(os.path.join(models_dir, "squad_generator_xgb.pkl"))
        ensemble_weight = joblib.load(os.path.join(models_dir, "squad_generator_weight.pkl"))
        feature_cols = joblib.load(os.path.join(models_dir, "squad_generator_features.pkl"))
        max_runs_dict = joblib.load(os.path.join(models_dir, "squad_generator_max_runs.pkl"))

        logger.info("Successfully loaded 5 ML models and configurations.")
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")
        raise

# Auto-load models and data when this module is imported
load_models()
load_data()

def classify_role(row):
    """
    Classify a player as Batsman, Bowler, or All-rounder based on career statistics.
    """
    batting_avg = row.get("career_batting_avg", 0)
    bowling_avg = row.get("career_bowling_avg", 0)
    wickets_last10 = row.get("wickets_last10", 0)

    is_genuine_bowler = (bowling_avg > 0) and (wickets_last10 > 0)
    is_genuine_batsman = batting_avg >= 20

    if is_genuine_bowler and is_genuine_batsman:
        return "All-rounder"
    elif is_genuine_bowler:
        return "Bowler"
    else:
        return "Batsman"

def generate_squad(format_filter, opposition_filter):
    """
    Generate the 11-man squad using the trained models and constraints.
    """
    pass
