from flask import Blueprint, request, jsonify, session
from backend.models.db_connect import get_connection

access_logs_bp = Blueprint("access_logs_bp", __name__)


@access_logs_bp.route("/access-logs", methods=["GET"])
def get_logs():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Not logged in"
        }), 401

    date = request.args.get("date")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if date:
            cursor.execute("""
                SELECT *
                FROM access_logs
                WHERE user_id = ? AND log_date = ?
                ORDER BY log_id DESC
            """, (user_id, date))
        else:
            cursor.execute("""
                SELECT *
                FROM access_logs
                WHERE user_id = ?
                ORDER BY log_id DESC
            """, (user_id,))

        logs = cursor.fetchall()

        return jsonify({
            "status": "success",
            "logs": [dict(row) for row in logs]
        })

    finally:
        conn.close()