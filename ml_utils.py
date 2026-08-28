import os
import joblib
import logging
import pandas as pd
import numpy as np

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

def suggest_squad(format_filter, opposition_filter, top_n=200):
    global df, model_rf, model_xgb, ensemble_weight, feature_cols, max_runs_dict

    # Filter out old matches - active within last 730 days
    cutoff_date = df["date"].max() - pd.Timedelta(days=730)
    active_players = df[df["date"] >= cutoff_date]["player_id"].unique()

    relevant_matches = df[
        (df["format"] == format_filter) &
        (df["opposition"] == opposition_filter) &
        (df["player_id"].isin(active_players))
    ]

    latest_snapshot = relevant_matches.sort_values("date").groupby("player_id").tail(1).copy()

    if latest_snapshot.empty:
        logger.warning(f"No recent matches found for format={format_filter}, opposition={opposition_filter}")
        return pd.DataFrame()

    latest_snapshot_encoded = pd.get_dummies(latest_snapshot, columns=["team", "opposition", "format"], drop_first=True)
    encoded_cols = {col: 0 for col in feature_cols if col not in latest_snapshot_encoded.columns}
    if encoded_cols:
        latest_snapshot_encoded = pd.concat([latest_snapshot_encoded, pd.DataFrame(encoded_cols, index=latest_snapshot_encoded.index)], axis=1)

    X_latest = latest_snapshot_encoded[feature_cols].replace([np.inf, -np.inf], 0).fillna(0)

    pred_rf = model_rf.predict(X_latest)
    pred_xgb = model_xgb.predict(X_latest)
    pred_final = ensemble_weight * pred_rf + (1 - ensemble_weight) * pred_xgb

    latest_snapshot["predicted_runs"] = pred_final
    cap = max_runs_dict.get(format_filter, 150)
    latest_snapshot["predicted_runs_capped"] = latest_snapshot["predicted_runs"].clip(upper=cap)

    result = latest_snapshot[[
        "player_name", "team", "avg_vs_opposition", "predicted_runs_capped",
        "career_batting_avg", "career_bowling_avg", "career_economy",
        "career_strike_rate", "runs_last5", "runs_last10",
        "wickets_last5", "wickets_last10", "economy_last5", "economy_last10"
    ]]

    return result.sort_values("predicted_runs_capped", ascending=False).head(top_n)


def generate_squad(format_filter, opposition_filter, team_filter=None, num_batsmen=5, num_bowlers=4, num_allrounders=2):
    """
    Generate the 11-man squad using the trained models and constraints.
    Optionally filter by team to only pick players from a specific side.
    """
    candidates = suggest_squad(format_filter, opposition_filter, top_n=500)

    if candidates.empty:
        return []

    # If a specific team is requested, filter candidates to that team
    if team_filter:
        candidates = candidates[candidates["team"] == team_filter]
        if candidates.empty:
            return []

    candidates = candidates.copy()
    candidates["role"] = candidates.apply(classify_role, axis=1)

    # Normalize predicted score into a 0-100 selection probability
    max_score = candidates["predicted_runs_capped"].max()
    if max_score > 0:
        candidates["selection_probability"] = (candidates["predicted_runs_capped"] / max_score * 100).round(1)
    else:
        candidates["selection_probability"] = 0

    batsmen = candidates[candidates["role"] == "Batsman"].head(num_batsmen)
    bowlers = candidates[candidates["role"] == "Bowler"].head(num_bowlers)
    allrounders = candidates[candidates["role"] == "All-rounder"].head(num_allrounders)

    squad = pd.concat([batsmen, bowlers, allrounders]).reset_index(drop=True)
    squad["captain"] = ""
    if len(squad) > 0:
        squad.loc[0, "captain"] = "Captain"
    if len(squad) > 1:
        squad.loc[1, "captain"] = "Vice-Captain"

    cols = [
        "player_name", "team", "role", "captain", "predicted_runs_capped",
        "selection_probability", "avg_vs_opposition",
        "runs_last5", "runs_last10", "wickets_last5", "wickets_last10",
        "economy_last5", "economy_last10", "career_batting_avg",
        "career_bowling_avg", "career_economy", "career_strike_rate"
    ]
    return squad[cols].fillna(0).round(2).to_dict(orient="records")

# Auto-load models and data when this module is imported
load_models()
load_data()

