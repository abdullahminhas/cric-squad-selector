import json
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from ml_utils import df
from ml_utils import generate_squad
from models import db, SavedSquad

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

        b_avg = round(float(latest.get("career_batting_avg", 0) or 0), 2)
        bw_avg = round(float(latest.get("career_bowling_avg", 0) or 0), 2)
        sr = round(float(latest.get("career_strike_rate", 0) or 0), 2)
        runs_l5 = round(float(latest.get("runs_last5", 0) or 0), 1)
        runs_l10 = round(float(latest.get("runs_last10", 0) or 0), 1)
        wkts_l5 = round(float(latest.get("wickets_last5", 0) or 0), 1)
        wkts_l10 = round(float(latest.get("wickets_last10", 0) or 0), 1)

        # Composite ML Profile Score (out of 100)
        bat_score = min(b_avg / 50.0, 1.0) * 30           # max 30 pts
        bowl_score = (min(40.0 / (bw_avg + 0.1), 1.6) / 1.6) * 20 if bw_avg > 0 else 0  # max 20 pts
        sr_score = min(sr / 150.0, 1.0) * 15              # max 15 pts
        form_score = min((runs_l5 + runs_l10) / 80.0, 1.0) * 20  # max 20 pts
        wkt_bonus = min((wkts_l5 + wkts_l10) / 10.0, 1.0) * 15  # max 15 pts
        ml_score = int(round(min(bat_score + bowl_score + sr_score + form_score + wkt_bonus, 100)))

        if ml_score >= 75:
            ml_rec = {"label": "Elite Profile", "css_class": "badge-elite", "score": ml_score}
        elif ml_score >= 55:
            ml_rec = {"label": "Strong Profile", "css_class": "badge-strong", "score": ml_score}
        elif ml_score >= 35:
            ml_rec = {"label": "Average Profile", "css_class": "badge-average", "score": ml_score}
        else:
            ml_rec = {"label": "Developing Profile", "css_class": "badge-developing", "score": ml_score}

        profile = {
            "player_name":        latest["player_name"],
            "team":               latest["team"],
            "career_batting_avg": b_avg,
            "career_bowling_avg": bw_avg,
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
            "ml_recommendation":  ml_rec,
        }

        return jsonify({"player": profile}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Save Squad ────────────────────────────────────────────────────────────────
@squad_bp.route("/api/save-squad", methods=["POST"])
@login_required
def api_save_squad():
    """
    Saves the current generated squad to the logged-in user's account.
    Body: { format, team, opposition, players: [...] }
    """
    data = request.get_json()
    if not data or not data.get("players") or not data.get("team"):
        return jsonify({"error": "Missing required squad data"}), 400

    label = f"{data['team']} vs {data.get('opposition', '?')} — {data.get('format', '?')}"

    squad = SavedSquad(
        user_id      = current_user.id,
        label        = label,
        format       = data.get("format", ""),
        team         = data.get("team", ""),
        opposition   = data.get("opposition", ""),
        players_json = json.dumps(data["players"]),
    )
    db.session.add(squad)
    db.session.commit()

    return jsonify({"message": "Squad saved!", "id": squad.id}), 201


# ─── Get My Squads ─────────────────────────────────────────────────────────────
@squad_bp.route("/api/my-squads", methods=["GET"])
@login_required
def api_my_squads():
    """Returns all squads saved by the currently logged-in user."""
    squads = (
        SavedSquad.query
        .filter_by(user_id=current_user.id)
        .order_by(SavedSquad.created_at.desc())
        .all()
    )
    return jsonify({"squads": [s.to_dict() for s in squads]}), 200


# ─── Delete Saved Squad ────────────────────────────────────────────────────────
@squad_bp.route("/api/saved-squad/<int:squad_id>", methods=["DELETE"])
@login_required
def api_delete_squad(squad_id):
    """Deletes a saved squad owned by the current user."""
    squad = SavedSquad.query.filter_by(id=squad_id, user_id=current_user.id).first()
    if not squad:
        return jsonify({"error": "Squad not found"}), 404
    db.session.delete(squad)
    db.session.commit()
    return jsonify({"message": "Squad deleted"}), 200
