# Project Report: AI-Powered Cricket Squad Selector

## Chapter 1: Introduction
### 1.1 Background
Cricket is a highly dynamic sport where match outcomes depend heavily on optimal team selection. Traditionally, squad selection has relied on human intuition, historical biases, and basic statistical averages. However, with the advent of big data in sports, there is a critical need to leverage machine learning to make data-driven, objective decisions.

### 1.2 Problem Statement
Selecting an optimal 11-man cricket squad is a complex optimization problem. Selectors must balance player roles (batsmen, bowlers, all-rounders), account for recent form versus career averages, and consider opposition-specific performance. A tool is needed to automate this process using predictive modeling.

### 1.3 Project Objectives
* To develop a machine learning model capable of predicting a player's future performance (runs/impact) based on historical data.
* To build a constraint-based selection algorithm that generates a balanced 11-man squad (e.g., 5 batsmen, 4 bowlers, 2 all-rounders).
* To design an intuitive, interactive web application where users can specify match formats, teams, and oppositions to visualize squad predictions.
* To provide an interactive Player Dashboard for in-depth statistical analysis and recent form visualization.

---

## Chapter 2: Literature Review & Background
### 2.1 Machine Learning in Sports Analytics
A review of how ensemble methods and predictive algorithms are currently used in modern sports (e.g., Moneyball in baseball, expected goals (xG) in football) and their growing adaptation in cricket.

### 2.2 Existing Systems
Analysis of existing cricket analytics platforms (like ESPNCricinfo, Cricbuzz). While these platforms provide extensive historical data, they lack predictive modeling for automated squad generation, highlighting the gap this project aims to fill.

### 2.3 Selected Technologies
* **Backend Framework:** Python (Flask) for lightweight, rapid API development.
* **Machine Learning:** Scikit-Learn (Random Forest) and XGBoost for robust regression and ensemble predictions.
* **Frontend UI:** HTML5, Vanilla CSS, and JavaScript for a responsive, modern interface. Chart.js for data visualization.

---

## Chapter 3: Methodology
### 3.1 Data Collection & Preprocessing
* **Dataset:** A master dataset of over 150,000 player match records.
* **Cleaning:** Handling missing values, filtering out inactive players (no matches in the last 730 days), and normalizing data.
* **Feature Engineering:** Calculating derived metrics such as `career_batting_avg`, `strike_rate`, `economy_last10`, and opposition-specific averages.

### 3.2 Predictive Modeling (Ensemble Approach)
To predict a player's expected performance, the system uses an ensemble regression model:
* **Random Forest Regressor:** Handles non-linear relationships and prevents overfitting.
* **XGBoost Regressor:** Utilizes gradient boosting for highly accurate predictions based on recent form trends.
* **Ensemble Weighting:** The final prediction is a weighted average of both models, capped at format-specific maximums (e.g., 150 runs for T20).

### 3.3 Squad Selection Algorithm
The algorithm takes the global predictive scores and applies strict domain constraints:
1. Filters the player pool dynamically based on the selected team.
2. Classifies players into Roles (Batsman, Bowler, All-rounder) based on their career stats.
3. Selects the top `N` players per role to satisfy the required balance (e.g., exactly 4 genuine bowlers).

---

## Chapter 4: System Implementation & Architecture
### 4.1 System Architecture
The application follows a client-server architecture. The frontend communicates asynchronously (via Fetch API) with Flask REST endpoints (`/api/generate-squad`, `/api/search-players`).

### 4.2 Machine Learning Pipeline
* `ml_utils.py`: Houses the logic for loading the pre-trained `joblib` models, processing the Pandas DataFrame, running the ensemble prediction, and returning the structured JSON data.

### 4.3 User Interface (UI/UX)
* **Dynamic Form:** Format-driven dropdowns that automatically filter eligible countries and prevent same-team selections.
* **Results Grid:** Displays the predicted squad grouped by role, featuring probability confidence bars and AI-generated rationales.
* **Player Dashboard:** A dedicated profile page featuring a search autocomplete system, career statistic cards, and interactive Chart.js graphs detailing the player's last 10 matches.

---

## Chapter 5: Results, Conclusion & Future Work
### 5.1 Results and Evaluation
The system successfully generates highly realistic squads that closely mirror actual real-world selections. The dynamic team filtering ensures that players are only picked if they have recent, valid data. The visualization tools provide clear justifications for why the AI picked a specific player over another.

### 5.2 Challenges Faced
* Addressing the imbalance in predictive scoring where top-order batsmen naturally score higher than bowlers, requiring role-specific constraints and clipping mechanisms.
* Managing state and dynamic UI updates for the interconnected dropdown menus.

### 5.3 Future Enhancements
* **User Authentication:** Implementing a secure login system (Flask-Login) allowing users to save their favorite squads.
* **Live Data Integration:** Connecting to a live cricket API to continuously update the dataset with real-time match results.
* **Pitch & Weather Conditions:** Adding environmental factors as features to the predictive model to adjust squad composition (e.g., selecting extra spinners on dusty pitches).
