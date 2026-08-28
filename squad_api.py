from flask import Blueprint, request, jsonify
from ml_utils import generate_squad

squad_bp = Blueprint("squad_bp", __name__)

@squad_bp.route("/api/generate-squad", methods=["POST"])
def api_generate_squad():
    data = request.get_json()

    if not data or "format" not in data or "opposition" not in data:
        return jsonify({"error": "Missing format or opposition in request"}), 400

    format_filter = data["format"]
    opposition_filter = data["opposition"]
    team_filter = data.get("team")  # optional — filter squad to players from this team

    try:
        squad = generate_squad(format_filter, opposition_filter, team_filter=team_filter)
        if not squad:
            return jsonify({"error": f"No active player data found for this combination."}), 404

        return jsonify({"squad": squad}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
