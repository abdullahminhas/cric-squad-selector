from flask import Blueprint, request, jsonify
from flask_login import login_required
from ml_utils import generate_squad

squad_bp = Blueprint("squad_bp", __name__)

@squad_bp.route("/api/generate-squad", methods=["POST"])
@login_required
def api_generate_squad():
    """
    Expects JSON payload:
    {
        "format": "T20I" or "ODI" or "Test",
        "opposition": "Australia", "India", etc.
    }
    """
    data = request.get_json()
    
    if not data or "format" not in data or "opposition" not in data:
        return jsonify({"error": "Missing format or opposition in request"}), 400
        
    format_filter = data["format"]
    opposition_filter = data["opposition"]
    
    try:
        squad = generate_squad(format_filter, opposition_filter)
        if not squad:
            return jsonify({"error": f"No active player data found against {opposition_filter} in {format_filter}"}), 404
            
        return jsonify({"squad": squad}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
