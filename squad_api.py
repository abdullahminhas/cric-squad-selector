from flask import Blueprint, request, jsonify
from ml_utils import df
from ml_utils import generate_squad

squad_bp = Blueprint("squad_bp", __name__)


# ─── Squad Generation ──────────────────────────────────────────────────────────
@squad_bp.route("/api/generate-squad", methods=["POST"])
def api_generate_squad():
    data = request.get_json()

    if not data or "format" not in data or "opposition" not in data:
        return jsonify({"error": "Missing format or opposition in request"}), 400

    format_filter = data["format"]
    opposition_filter = data["opposition"]
    team_filter = data.get("team")

    try:
        squad = generate_squad(format_filter, opposition_filter, team_filter=team_filter)
        if not squad:
            return jsonify({"error": "No active player data found for this combination."}), 404

        return jsonify({"squad": squad}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Player Search (autocomplete) ─────────────────────────────────────────────
@squad_bp.route("/api/search-players", methods=["GET"])
def api_search_players():
    """
    Returns a list of player names matching the query string.
    Example: /api/search-players?q=babar
    """
    query = request.args.get("q", "").strip().lower()
    if len(query) < 2:
        return jsonify({"players": []}), 200

    try:
        cutoff_date = df["date"].max() - __import__("pandas").Timedelta(days=730)
        active_players = df[df["date"] >= cutoff_date]

        matches = (
            active_players[
                active_players["player_name"].str.lower().str.contains(query, na=False)
            ][["player_name", "team"]]
            .drop_duplicates("player_name")
            .sort_values("player_name")
            .head(10)
        )

        results = matches.to_dict(orient="records")
        return jsonify({"players": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Player Profile ────────────────────────────────────────────────────────────
@squad_bp.route("/api/player/<path:player_name>", methods=["GET"])
def api_player_profile(player_name):
    """
    Returns the full profile of a player by name.
    Includes career stats and recent form for the last 5 & 10 matches.
    """
    try:
        player_rows = df[df["player_name"].str.lower() == player_name.strip().lower()]

        if player_rows.empty:
            return jsonify({"error": f"Player '{player_name}' not found."}), 404

        # Most recent row for meta info
        latest = player_rows.sort_values("date").iloc[-1]

        # Recent match history (last 10 matches — date, runs, wickets)
        history = (
            player_rows.sort_values("date")
            .tail(10)[["date", "format", "opposition", "runs", "wickets", "economy_last5"]]
            .fillna(0)
        )
        history["date"] = history["date"].astype(str)

        profile = {
            "player_name":        latest["player_name"],
            "team":               latest["team"],
            "career_batting_avg": round(float(latest.get("career_batting_avg", 0) or 0), 2),
            "career_bowling_avg": round(float(latest.get("career_bowling_avg", 0) or 0), 2),
            "career_strike_rate": round(float(latest.get("career_strike_rate", 0) or 0), 2),
            "career_economy":     round(float(latest.get("career_economy", 0) or 0), 2),
            "career_matches":     int(latest.get("career_matches_played", 0) or 0),
            "runs_last5":         round(float(latest.get("runs_last5", 0) or 0), 1),
            "runs_last10":        round(float(latest.get("runs_last10", 0) or 0), 1),
            "wickets_last5":      round(float(latest.get("wickets_last5", 0) or 0), 1),
            "wickets_last10":     round(float(latest.get("wickets_last10", 0) or 0), 1),
            "economy_last5":      round(float(latest.get("economy_last5", 0) or 0), 2),
            "economy_last10":     round(float(latest.get("economy_last10", 0) or 0), 2),
            "recent_matches":     history.to_dict(orient="records"),
        }

        return jsonify({"player": profile}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
