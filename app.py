import os
from werkzeug.security import check_password_hash
from flask import Flask, request, jsonify, send_from_directory, session, render_template, redirect, make_response
from db import pool, get_user

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

JSON_BODY_REQUIRED = "JSON body is required"
LOGIN_REQUIRED = "Please login first"
SUPPORT_ACCESS_REQUIRED = "Support access required"

@app.route("/", methods=["GET"])
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/raise-ticket")
def raise_ticket_page():
    if "username" not in session:
        return redirect("/")

    if session.get("role") != "CUSTOMER":
        return redirect("/")

    response = render_template("raise_ticket.html")
    response = make_response(response)

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

@app.route("/health")
def health():
    return "OK"


@app.route("/info")
def info():
    return "HelpDesk App v1.0"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": JSON_BODY_REQUIRED}), 400

    username = data.get("username")
    password = data.get("password")
    login_type = data.get("loginType")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = get_user(username)

    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    if not check_password_hash(user[2], password):
        return jsonify({"error": "Invalid username or password"}), 401

    if login_type == "customer" and user[4] != "CUSTOMER":
        return jsonify({"error": "Customer login is not allowed for this user"}), 403

    if login_type == "support" and user[4] != "SUPPORT":
        return jsonify({"error": "Support login is not allowed for this user"}), 403
    session["username"] = user[1]
    session["department"] = user[3]
    session["role"] = user[4]

    return jsonify({
        "message": "Login successful",
        "username": user[1],
        "department": user[3],
        "role": user[4]
    })

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "username" not in session:
        return redirect("/")

    if session.get("role") != "SUPPORT":
        return redirect("/")

    response = render_template("dashboard.html")
    response = make_response(response)

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

@app.route("/tickets", methods=["POST"])
def create_ticket():

    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "SUPPORT":
        return jsonify({"error": SUPPORT_ACCESS_REQUIRED}), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": JSON_BODY_REQUIRED}), 400

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

    with pool.connection() as conn:
        with conn.cursor() as cursor:
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

    return jsonify({
        "id": ticket[0],
        "title": ticket[1],
        "description": ticket[2],
        "priority": ticket[3],
        "status": ticket[4],
        "created_at": ticket[5].isoformat()
    }), 201

@app.route("/tickets/raise", methods=["POST"])
def raise_ticket():

    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "CUSTOMER":
        return jsonify({"error": "Customer access required"}), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": JSON_BODY_REQUIRED}), 400

    customer_name = session["username"]
    customer_email = data.get("customer_email")
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "MEDIUM")

    if not customer_name or not customer_email or not title:
        return jsonify({
            "error": "Customer name, customer email and title are required"
        }), 400

    if (
          "@" not in customer_email
          or " " in customer_email
          or "." not in customer_email.split("@")[-1]
    ):
        

          return jsonify({"error": "Invalid customer email"}), 400

    allowed_priorities = ["LOW", "MEDIUM", "HIGH"]

    if priority not in allowed_priorities:
        return jsonify({
            "error": "Invalid priority",
            "allowed_priorities": allowed_priorities
        }), 400

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tickets
                (
                    customer_name,
                    customer_email,
                    title,
                    description,
                    priority
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING
                    id,
                    customer_name,
                    customer_email,
                    title,
                    description,
                    priority,
                    status,
                    assigned_to,
                    resolution_comment,
                    created_at;
                """,
                (
                    customer_name,
                    customer_email,
                    title,
                    description,
                    priority
                )
            )

            ticket = cursor.fetchone()
            conn.commit()

    return jsonify({
        "id": ticket[0],
        "customer_name": ticket[1],
        "customer_email": ticket[2],
        "title": ticket[3],
        "description": ticket[4],
        "priority": ticket[5],
        "status": ticket[6],
        "assigned_to": ticket[7],
        "resolution_comment": ticket[8],
        "created_at": ticket[9].isoformat()
    }), 201

@app.route("/tickets", methods=["GET"])
def get_tickets():
    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "SUPPORT":
        return jsonify({"error": SUPPORT_ACCESS_REQUIRED}), 403

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, priority, status, assigned_to, resolution_comment, created_at
                FROM tickets ORDER BY id;
                """
            )

            rows = cursor.fetchall()

    tickets = []

    for row in rows:
        tickets.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "priority": row[3],
            "status": row[4],
            "assigned_to": row[5],
            "resolution_comment": row[6],
            "created_at": row[7].isoformat()
        })

    return jsonify(tickets)

@app.route("/tickets/<int:ticket_id>/take", methods=["PUT"])
def take_ticket(ticket_id):
    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "SUPPORT":
        return jsonify({"error": SUPPORT_ACCESS_REQUIRED}), 403

    username = session["username"]

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tickets
                SET assigned_to = %s,
                    status = 'IN_PROGRESS'
                WHERE id = %s
                  AND assigned_to IS NULL
                RETURNING id, title, description, priority, status, assigned_to, created_at;
                """,
                (username, ticket_id)
            )

            row = cursor.fetchone()
            conn.commit()

    if row is None:
        return jsonify({
            "error": "Ticket not found or already assigned"
        }), 400

    return jsonify({
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "priority": row[3],
        "status": row[4],
        "assigned_to": row[5],
        "created_at": row[6].isoformat()
    })

@app.route("/tickets/<int:ticket_id>/resolve", methods=["PUT"])
def resolve_ticket(ticket_id):
    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "SUPPORT":
        return jsonify({"error": SUPPORT_ACCESS_REQUIRED}), 403

    username = session["username"]

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": JSON_BODY_REQUIRED}), 400

    resolution_comment = data.get("resolution_comment")

    if not resolution_comment:
        return jsonify({"error": "Resolution comment is required"}), 400

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tickets
                SET status = 'CLOSED',
                    resolution_comment = %s
                WHERE id = %s
                  AND assigned_to = %s
                  AND status = 'IN_PROGRESS'
                RETURNING id, title, description, priority,
                          status, assigned_to, resolution_comment, created_at;
                """,
                (resolution_comment, ticket_id, username)
            )

            row = cursor.fetchone()
            conn.commit()

    if row is None:
        return jsonify({
            "error": "Ticket not found, not assigned to you, or already closed"
        }), 400

    return jsonify({
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "priority": row[3],
        "status": row[4],
        "assigned_to": row[5],
        "resolution_comment": row[6],
        "created_at": row[7].isoformat()
    })

@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):

    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "SUPPORT":
        return jsonify({"error": SUPPORT_ACCESS_REQUIRED}), 403

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, priority, status, created_at
                FROM tickets
                WHERE id = %s;
                """,
                (ticket_id,)
            )

            row = cursor.fetchone()

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

    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "SUPPORT":
        return jsonify({"error": SUPPORT_ACCESS_REQUIRED}), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": JSON_BODY_REQUIRED}), 400

    status = data.get("status")

    if not status:
        return jsonify({"error": "Status is required"}), 400

    allowed_statuses = ["OPEN", "IN_PROGRESS", "CLOSED"]

    if status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status",
            "allowed_statuses": allowed_statuses
        }), 400

    with pool.connection() as conn:
        with conn.cursor() as cursor:
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

    if "username" not in session:
        return jsonify({"error": LOGIN_REQUIRED}), 401

    if session.get("role") != "SUPPORT":
        return jsonify({"error": SUPPORT_ACCESS_REQUIRED}), 403

    with pool.connection() as conn:
        with conn.cursor() as cursor:
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
    if row is None:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify({
        "message": "Ticket deleted successfully",
        "id": row[0]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
