from flask import Flask, request, jsonify, send_from_directory
from db import get_connection

app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")


@app.route("/health")
def health():
    return "OK"


@app.route("/info")
def info():
    return "HelpDesk App v1.0"


@app.route("/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    title = data.get("title")

    description = data.get("description")

    priority = data.get("priority", "MEDIUM")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    allowed_priorities = ["LOW", "MEDIUM", "HIGH"]

    if priority not in allowed_priorities:
        return jsonify({
            "error": "Invalid priority",
            "allowed_priorities": allowed_priorities
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tickets (title, description, priority)
        VALUES (%s, %s, %s)
        RETURNING id, title, description, priority, status, created_at;
        """,
        (title, description, priority)
    )

    ticket = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "id": ticket[0],
        "title": ticket[1],
        "description": ticket[2],
        "priority": ticket[3],
        "status": ticket[4],
        "created_at": ticket[5].isoformat()
    }), 201

@app.route("/tickets", methods=["GET"])
def get_tickets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, description, priority, status, created_at
        FROM tickets
        ORDER BY id;
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    tickets = []

    for row in rows:
        tickets.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "priority": row[3],
            "status": row[4],
            "created_at": row[5].isoformat()
        })

    return jsonify(tickets)

@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, description, priority, status, created_at
        FROM tickets
        WHERE id = %s;
        """,
        (ticket_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify({
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "priority": row[3],
        "status": row[4],
        "created_at": row[5].isoformat()
    })

@app.route("/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    data = request.get_json()

    status = data.get("status")

    if not status:
        return jsonify({"error": "Status is required"}), 400

    allowed_statuses = ["OPEN", "IN_PROGRESS", "CLOSED"]

    if status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status",
            "allowed_statuses": allowed_statuses
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tickets
        SET status = %s
        WHERE id = %s
        RETURNING id, title, description, priority, status, created_at;
        """,
        (status, ticket_id)
    )

    row = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    if row is None:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify({
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "priority": row[3],
        "status": row[4],
        "created_at": row[5].isoformat()
    })

@app.route("/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tickets
        WHERE id = %s
        RETURNING id;
        """,
        (ticket_id,)
    )

    row = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    if row is None:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify({
        "message": "Ticket deleted successfully",
        "id": row[0]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
