from app import app
from datetime import datetime

def test_home_page():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

def test_login_requires_json():
    client = app.test_client()

    response = client.post("/login")

    assert response.status_code == 400

def test_login_invalid_credentials():
    client = app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "invalid_user",
            "password": "invalid_password"
        }
    )

    assert response.status_code == 401

def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

def test_info():
    client = app.test_client()

    response = client.get("/info")

    assert response.status_code == 200
    assert response.data.decode() == "HelpDesk App v1.0"

def test_get_tickets_requires_login():
    client = app.test_client()

    response = client.get("/tickets")

    assert response.status_code == 401

def test_raise_ticket_requires_login():
    client = app.test_client()

    response = client.post(
        "/tickets/raise",
        json={
            "customer_name": "Test User",
            "customer_email": "test@example.com",
            "title": "Test Ticket",
            "description": "Test description",
            "priority": "MEDIUM"
        }
    )

    assert response.status_code == 401

def test_dashboard_requires_login():
    client = app.test_client()

    response = client.get("/dashboard")

    assert response.status_code == 302

def test_logout():
    client = app.test_client()

    response = client.get("/logout")

    assert response.status_code == 302

def test_create_ticket_requires_json():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.post("/tickets")

    assert response.status_code == 400

def test_get_tickets_requires_support_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.get("/tickets")

    assert response.status_code == 403

def test_raise_ticket_requires_customer_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "supportuser"
        session["role"] = "SUPPORT"

    response = client.post(
        "/tickets/raise",
        json={
            "customer_email": "test@example.com",
            "title": "Test Ticket",
            "description": "Test description",
            "priority": "MEDIUM"
        }
    )

    assert response.status_code == 403

def test_raise_ticket_invalid_email():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.post(
        "/tickets/raise",
        json={
            "customer_email": "invalid-email",
            "title": "Test Ticket",
            "description": "Test description",
            "priority": "MEDIUM"
        }
    )

    assert response.status_code == 400

def test_raise_ticket_invalid_priority():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.post(
        "/tickets/raise",
        json={
            "customer_email": "customer@example.com",
            "title": "Test Ticket",
            "description": "Test description",
            "priority": "URGENT"
        }
    )

    assert response.status_code == 400

def test_raise_ticket_missing_required_fields():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.post(
        "/tickets/raise",
        json={
            "customer_email": "customer@example.com"
        }
    )

    assert response.status_code == 400

def test_raise_ticket_page_requires_login():
    client = app.test_client()

    response = client.get("/raise-ticket")

    assert response.status_code == 302
    assert response.location == "/"

def test_raise_ticket_page_support_user_redirect():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "support1"
        session["role"] = "SUPPORT"

    response = client.get("/raise-ticket")

    assert response.status_code == 302
    assert response.location == "/"

def test_raise_ticket_page_customer_access():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.get("/raise-ticket")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Expires"] == "0"

def test_login_missing_credentials():
    client = app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "testuser"
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Username and password are required"

def test_login_wrong_password():
    client = app.test_client()

    response = client.post(
        "/login",
        json={
            "username": "customer1",
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid username or password"

def test_customer_login_with_support_user(monkeypatch):
    client = app.test_client()

    monkeypatch.setattr(
        "app.get_user",
        lambda username: (
            1,
            "testuser",
            "hashed_password",
            "IT",
            "SUPPORT"
        )
    )

    monkeypatch.setattr(
        "app.check_password_hash",
        lambda stored_password, password: True
    )

    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "any_password",
            "loginType": "customer"
        }
    )

    assert response.status_code == 403
    assert response.json["error"] == "Customer login is not allowed for this user"

def test_support_login_with_customer_user(monkeypatch):
    client = app.test_client()

    monkeypatch.setattr(
        "app.get_user",
        lambda username: (
            2,
            "customer1",
            "hashed_password",
            "CUSTOMER",
            "CUSTOMER"
        )
    )

    monkeypatch.setattr(
        "app.check_password_hash",
        lambda stored_password, password: True
    )

    response = client.post(
        "/login",
        json={
            "username": "customer1",
            "password": "any_password",
            "loginType": "support"
        }
    )

    assert response.status_code == 403
    assert response.json["error"] == "Support login is not allowed for this user"

def test_login_success(monkeypatch):
    client = app.test_client()

    monkeypatch.setattr(
        "app.get_user",
        lambda username: (
            1,
            "testuser",
            "hashed_password",
            "IT",
            "SUPPORT"
        )
    )

    monkeypatch.setattr(
        "app.check_password_hash",
        lambda stored_password, password: True
    )

    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "any_password",
            "loginType": "support"
        }
    )

    assert response.status_code == 200
    assert response.json["message"] == "Login successful"
    assert response.json["username"] == "testuser"
    assert response.json["department"] == "IT"
    assert response.json["role"] == "SUPPORT"

    with client.session_transaction() as session:
        assert session["username"] == "testuser"
        assert session["department"] == "IT"
        assert session["role"] == "SUPPORT"

def test_dashboard_customer_redirect():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.get("/dashboard")

    assert response.status_code == 302
    assert response.location == "/"

def test_dashboard_support_access():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store, no-cache, must-revalidate, max-age=0"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Expires"] == "0"

def test_create_ticket_requires_login():
    client = app.test_client()

    response = client.post(
        "/tickets",
        json={
            "title": "Test ticket",
            "description": "Test description"
        }
    )

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"

def test_create_ticket_requires_support_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.post(
        "/tickets",
        json={
            "title": "Test ticket",
            "description": "Test description"
        }
    )

    assert response.status_code == 403
    assert response.json["error"] == "Support access required"

def test_create_ticket_requires_title():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.post(
        "/tickets",
        json={
            "description": "Test description"
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"

def test_create_ticket_invalid_priority():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.post(
        "/tickets",
        json={
            "title": "Test ticket",
            "description": "Test description",
            "priority": "URGENT"
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid priority"
    assert response.json["allowed_priorities"] == ["LOW", "MEDIUM", "HIGH"]

def test_create_ticket_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return (
                1,
                "Test ticket",
                "Test description",
                "HIGH",
                "OPEN",
                datetime(2026, 10, 7, 12, 0, 0)
            )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.post(
        "/tickets",
        json={
            "title": "Test ticket",
            "description": "Test description",
            "priority": "HIGH"
        }
    )

    assert response.status_code == 201
    assert response.json["id"] == 1
    assert response.json["title"] == "Test ticket"
    assert response.json["description"] == "Test description"
    assert response.json["priority"] == "HIGH"
    assert response.json["status"] == "OPEN"
    assert response.json["created_at"] == "2026-10-07T12:00:00"

def test_raise_ticket_requires_json_body():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.post("/tickets/raise")

    assert response.status_code == 400
    assert response.json["error"] == "JSON body is required"

def test_raise_ticket_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return (
                1,
                "customer1",
                "customer1@example.com",
                "Test ticket",
                "Test description",
                "HIGH",
                "OPEN",
                None,
                None,
                datetime(2026, 10, 7, 12, 0, 0)
            )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.post(
        "/tickets/raise",
        json={
            "customer_email": "customer1@example.com",
            "title": "Test ticket",
            "description": "Test description",
            "priority": "HIGH"
        }
    )

    assert response.status_code == 201
    assert response.json["id"] == 1
    assert response.json["customer_name"] == "customer1"
    assert response.json["customer_email"] == "customer1@example.com"
    assert response.json["title"] == "Test ticket"
    assert response.json["description"] == "Test description"
    assert response.json["priority"] == "HIGH"
    assert response.json["status"] == "OPEN"

def test_get_tickets_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query):
            pass

        def fetchall(self):
            return [
                (
                    1,
                    "Test ticket",
                    "Test description",
                    "HIGH",
                    "OPEN",
                    None,
                    None,
                    datetime(2026, 10, 7, 12, 0, 0)
                )
            ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.get("/tickets")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["id"] == 1
    assert response.json[0]["title"] == "Test ticket"
    assert response.json[0]["priority"] == "HIGH"
    assert response.json[0]["status"] == "OPEN"
    assert response.json[0]["assigned_to"] is None
    assert response.json[0]["resolution_comment"] is None
    assert response.json[0]["created_at"] == "2026-10-07T12:00:00"

def test_take_ticket_not_found(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return None

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.put("/tickets/999/take")

    assert response.status_code == 400
    assert response.json["error"] == "Ticket not found or already assigned"

def test_take_ticket_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return (
                1,
                "Test ticket",
                "Test description",
                "HIGH",
                "IN_PROGRESS",
                "testuser",
                datetime(2026, 10, 7, 12, 0, 0)
            )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.put("/tickets/1/take")

    assert response.status_code == 200
    assert response.json["id"] == 1
    assert response.json["title"] == "Test ticket"
    assert response.json["description"] == "Test description"
    assert response.json["priority"] == "HIGH"
    assert response.json["status"] == "IN_PROGRESS"
    assert response.json["assigned_to"] == "testuser"
    assert response.json["created_at"] == "2026-10-07T12:00:00"

def test_resolve_ticket_requires_json_body():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.put("/tickets/1/resolve")

    assert response.status_code == 400
    assert response.json["error"] == "JSON body is required"

def test_resolve_ticket_requires_resolution_comment():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.put(
        "/tickets/1/resolve",
        json={"something": "test"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "Resolution comment is required"

def test_resolve_ticket_not_found(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return None

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.put(
        "/tickets/1/resolve",
        json={"resolution_comment": "Issue resolved"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "Ticket not found, not assigned to you, or already closed"

def test_resolve_ticket_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return (
                1,
                "Test ticket",
                "Test description",
                "HIGH",
                "CLOSED",
                "testuser",
                "Issue resolved",
                datetime(2026, 10, 7, 12, 0, 0)
            )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.put(
        "/tickets/1/resolve",
        json={"resolution_comment": "Issue resolved"}
    )

    assert response.status_code == 200
    assert response.json["id"] == 1
    assert response.json["title"] == "Test ticket"
    assert response.json["description"] == "Test description"
    assert response.json["priority"] == "HIGH"
    assert response.json["status"] == "CLOSED"
    assert response.json["assigned_to"] == "testuser"
    assert response.json["resolution_comment"] == "Issue resolved"
    assert response.json["created_at"] == "2026-10-07T12:00:00"

def test_take_ticket_requires_login():
    client = app.test_client()

    response = client.put("/tickets/1/take")

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"

def test_take_ticket_requires_support_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.put("/tickets/1/take")

    assert response.status_code == 403
    assert response.json["error"] == "Support access required"

def test_get_ticket_requires_login():
    client = app.test_client()

    response = client.get("/tickets/1")

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"

def test_get_ticket_requires_support_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.get("/tickets/1")

    assert response.status_code == 403
    assert response.json["error"] == "Support access required"

def test_get_ticket_not_found(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return None

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.get("/tickets/999")

    assert response.status_code == 404
    assert response.json["error"] == "Ticket not found"

def test_get_ticket_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return (
                1,
                "Test ticket",
                "Test description",
                "HIGH",
                "OPEN",
                datetime(2026, 10, 7, 12, 0, 0)
            )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.get("/tickets/1")

    assert response.status_code == 200
    assert response.json["id"] == 1
    assert response.json["title"] == "Test ticket"
    assert response.json["description"] == "Test description"
    assert response.json["priority"] == "HIGH"
    assert response.json["status"] == "OPEN"
    assert response.json["created_at"] == "2026-10-07T12:00:00"

def test_update_ticket_requires_login():
    client = app.test_client()

    response = client.put(
        "/tickets/1",
        json={"status": "CLOSED"}
    )

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"

def test_update_ticket_requires_support_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.put(
        "/tickets/1",
        json={"status": "CLOSED"}
    )

    assert response.status_code == 403
    assert response.json["error"] == "Support access required"

def test_update_ticket_requires_json_body():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.put("/tickets/1")

    assert response.status_code == 400
    assert response.json["error"] == "JSON body is required"

def test_update_ticket_requires_status():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.put(
        "/tickets/1",
        json={"something": "test"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "Status is required"

def test_update_ticket_invalid_status():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    response = client.put(
        "/tickets/1",
        json={"status": "INVALID"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid status"
    assert response.json["allowed_statuses"] == [
        "OPEN",
        "IN_PROGRESS",
        "CLOSED"
    ]

def test_update_ticket_not_found(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return None

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.put(
        "/tickets/999",
        json={"status": "CLOSED"}
    )

    assert response.status_code == 404
    assert response.json["error"] == "Ticket not found"

def test_update_ticket_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return (
                1,
                "Test ticket",
                "Test description",
                "HIGH",
                "CLOSED",
                datetime(2026, 10, 7, 12, 0, 0)
            )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.put(
        "/tickets/1",
        json={"status": "CLOSED"}
    )

    assert response.status_code == 200
    assert response.json["id"] == 1
    assert response.json["title"] == "Test ticket"
    assert response.json["description"] == "Test description"
    assert response.json["priority"] == "HIGH"
    assert response.json["status"] == "CLOSED"
    assert response.json["created_at"] == "2026-10-07T12:00:00"

def test_delete_ticket_requires_login():
    client = app.test_client()

    response = client.delete("/tickets/1")

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"

def test_delete_ticket_requires_support_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.delete("/tickets/1")

    assert response.status_code == 403
    assert response.json["error"] == "Support access required"

def test_delete_ticket_not_found(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return None

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.delete("/tickets/999")

    assert response.status_code == 404
    assert response.json["error"] == "Ticket not found"

def test_delete_ticket_success(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["role"] = "SUPPORT"

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, query, params):
            pass

        def fetchone(self):
            return (1,)

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def cursor(self):
            return FakeCursor()

        def commit(self):
            pass

    class FakePool:
        def connection(self):
            return FakeConnection()

    monkeypatch.setattr("app.pool", FakePool())

    response = client.delete("/tickets/1")

    assert response.status_code == 200
    assert response.json["message"] == "Ticket deleted successfully"
    assert response.json["id"] == 1

def test_resolve_ticket_requires_login():
    client = app.test_client()

    response = client.put(
        "/tickets/1/resolve",
        json={"resolution_comment": "Issue resolved"}
    )

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"

def test_resolve_ticket_requires_support_role():
    client = app.test_client()

    with client.session_transaction() as session:
        session["username"] = "customer1"
        session["role"] = "CUSTOMER"

    response = client.put(
        "/tickets/1/resolve",
        json={"resolution_comment": "Issue resolved"}
    )

    assert response.status_code == 403
    assert response.json["error"] == "Support access required"

def test_main_starts_flask_app(monkeypatch):
    called = {}

    def fake_run(self, host, port):
        called["host"] = host
        called["port"] = port

    from flask import Flask
    monkeypatch.setattr(Flask, "run", fake_run)

    import runpy
    runpy.run_module("app", run_name="__main__")

    assert called["host"] == "0.0.0.0"
    assert called["port"] == 5000
