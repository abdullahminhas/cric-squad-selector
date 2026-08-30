# Cric Squad Selector: System Architecture & Technical Details

This document provides a comprehensive technical overview of the Cric Squad Selector application. It is designed to assist in creating UML diagrams (Class, Sequence, Component, and Architecture diagrams).

---

## 1. High-Level Architecture (Component Diagram Reference)
The application follows a standard **Client-Server Architecture** utilizing a RESTful API approach for asynchronous communication.

*   **Client (Frontend):** HTML5, Vanilla JavaScript (ES6), CSS3, Chart.js.
*   **Server (Backend):** Python, Flask, Flask-SQLAlchemy (pending Day 5), Flask-Login (pending Day 5).
*   **Machine Learning / Data Layer:** Scikit-Learn (Random Forest), XGBoost, Pandas, Joblib.

---

## 2. Routing & Endpoints (Sequence Diagram Reference)
The backend uses Flask Blueprints to organize routes.

### View Routes (Served by `app.py`)
These endpoints render the base HTML templates.
*   `GET /` -> `home()`: Renders `index.html` (The Squad Selector form).
*   `GET /player-dashboard` -> `player_dashboard()`: Renders `player_dashboard.html` (The Player profile UI).

### API Routes (Served by `squad_api.py`)
These endpoints handle AJAX/Fetch requests from the frontend Javascript.

*   `POST /api/generate-squad` -> `api_generate_squad()`:
    *   **Input:** JSON payload `{ "format": "T20", "team": "Australia", "opposition": "India" }`.
    *   **Process:** Calls `ml_utils.generate_squad()`.
    *   **Output:** JSON array of 11 selected player objects containing predicted runs, roles, and stats.

*   `GET /api/search-players` -> `api_search_players()`:
    *   **Input:** Query parameter `?q=<name>`.
    *   **Process:** Filters the active players dataframe for partial string matches.
    *   **Output:** JSON array of up to 10 matching player names and their teams.

*   `GET /api/player/<player_name>` -> `api_player_profile(player_name)`:
    *   **Input:** URL parameter representing the exact player name.
    *   **Process:** Retrieves the player's latest stats and historical match data (last 10 matches) from the global dataframe.
    *   **Output:** JSON object containing the comprehensive player profile.

---

## 3. Machine Learning Pipeline (`ml_utils.py`)
This module handles all data processing and predictive logic. It loads data into memory once when the server starts.

### 3.1 Global State (Loaded on Startup)
*   `df`: Pandas DataFrame containing ~150,000 historical match records (`master_player_match_features.csv`).
*   `model_rf`: Pre-trained Scikit-Learn Random Forest model.
*   `model_xgb`: Pre-trained XGBoost model.
*   `feature_cols`: List of features required by the models.

### 3.2 `suggest_squad()` (Core Prediction Logic)
1.  **Filtering:** Identifies active players (played within the last 730 days) and filters by the requested format and team.
2.  **Snapshot Extraction:** Grabs the most recent chronological record for each eligible player to capture their current career stats and recent form.
3.  **Opposition Injection:** Overwrites the "opposition" column with the requested opponent and dynamically maps the player's historical averages against that specific opponent.
4.  **Feature Encoding:** One-hot encodes categorical variables (team, opposition, format) to match the models' expected input structure.
5.  **Prediction:** Runs the feature matrix through both `model_rf` and `model_xgb`.
6.  **Ensembling & Clipping:** Calculates a weighted average (50/50) of the two predictions, capping the maximum value based on format constraints (e.g., 150 max runs for T20).
7.  **Output:** Returns a DataFrame sorted by predicted runs.

### 3.3 `generate_squad()` (Constraint Application)
1.  Calls `suggest_squad()` to get the ranked pool of players for the chosen team.
2.  Iterates through the pool, evaluating each player via the `classify_role()` function.
    *   **Bowler:** Has a bowling average > 0 AND taken at least one wicket in their last 10 matches.
    *   **Batsman:** Has a batting average >= 20.
    *   **All-rounder:** Meets both conditions.
3.  Iteratively selects the top available players until the strict constraints are met:
    *   5 Batsmen
    *   2 All-rounders
    *   4 Bowlers
4.  Returns the finalized list of 11 players as a list of dictionaries.

---

## 4. Frontend Interaction Flow (Activity Diagram Reference)

### Scenario A: Generating a Squad
1.  User selects Format, Team, and Opposition on `index.html`.
2.  `app.js` listens for the `submit` event, disables the button, and shows the loading spinner.
3.  `app.js` sends a `POST` request to `/api/generate-squad`.
4.  Backend processes the ML prediction (see Section 3.2 & 3.3) and returns JSON.
5.  `app.js` parses the JSON, calculates a "Selection Confidence" percentage (mapping the predicted runs to a 0-100 scale based on role expectations), and determines the captain/vice-captain.
6.  `app.js` dynamically generates HTML cards grouped by role (Batsmen, All-rounders, Bowlers) and injects them into `#results-container`.

### Scenario B: Searching a Player
1.  User types in the `#dashboard-player-search` input on `player_dashboard.html`.
2.  `dashboard.js` utilizes a debounce function (250ms delay) to prevent spamming API calls.
3.  Sends `GET /api/search-players?q=...`.
4.  Renders the dropdown list.
5.  User clicks a name. `dashboard.js` sends `GET /api/player/<name>`.
6.  Backend returns the full profile JSON.
7.  `dashboard.js` populates the DOM elements, calculates the player's role tag, and instantiates two Chart.js canvases (Runs and Wickets over the last 10 matches).
