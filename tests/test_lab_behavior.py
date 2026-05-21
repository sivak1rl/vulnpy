import io
import json
import os

import config
import db


def test_seeded_homepage_loads_published_posts(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to VulnPy" in response.data
    assert b"Understanding SQL Injection" in response.data
    assert b"Upcoming Security Audit Results" not in response.data


def test_login_sql_injection_bypass_remains_available(client):
    response = client.post(
        "/login",
        data={"username": "' OR 1=1 --", "password": "wrong"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session["username"] == "admin"
        assert session["role"] == "admin"


def test_search_sql_injection_can_extract_seeded_users(client):
    payload = "%') UNION SELECT id,username,password,bio,role,created_at FROM users --"
    response = client.get("/search", query_string={"q": payload})

    assert response.status_code == 200
    assert b"0192023a7bbd73250516f069df18b500" in response.data
    assert b"5f4dcc3b5aa765d61d8327deb882cf99" in response.data


def test_admin_dashboard_is_reachable_without_login(client):
    response = client.get("/admin/")

    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data
    assert b"Upcoming Security Audit Results" in response.data


def test_draft_post_idor_exposes_seeded_draft(client):
    response = client.get("/post/5")

    assert response.status_code == 200
    assert b"CONFIDENTIAL" in response.data
    assert b"DRAFT" in response.data


def test_logged_in_user_can_edit_another_profile(client, login):
    login("alice", "password")

    response = client.post(
        "/user/admin/edit",
        data={"bio": "<script>alert('owned')</script>"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"<script>alert('owned')</script>" in response.data

    user = db.query_db("SELECT bio FROM users WHERE username = ?", ("admin",), one=True)
    assert user["bio"] == "<script>alert('owned')</script>"


def test_uploaded_html_is_served_inline(client, tmp_path):
    response = client.post(
        "/upload",
        data={"file": (io.BytesIO(b"<script>alert('upload')</script>"), "xss.html")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"xss.html" in response.data

    uploaded = client.get("/uploads/xss.html")
    assert uploaded.status_code == 200
    assert uploaded.data == b"<script>alert('upload')</script>"
    assert "attachment" not in uploaded.headers.get("Content-Disposition", "")


def test_debug_endpoint_exposes_config_and_environment(client, monkeypatch):
    monkeypatch.setenv("VULNPY_TEST_SECRET", "visible-in-debug")

    response = client.get("/debug")

    assert response.status_code == 200
    assert b"SECRET_KEY" in response.data
    assert b"visible-in-debug" in response.data


def test_insecure_session_cookie_flags_are_set(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is False
    assert app.config["SESSION_COOKIE_SECURE"] is False


def test_vulnerability_maps_stay_in_sync():
    with open("vuln_map.json", encoding="utf-8") as root_file:
        root_map = json.load(root_file)
    with open(os.path.join("static", "vuln_map.json"), encoding="utf-8") as static_file:
        static_map = json.load(static_file)

    assert root_map == static_map

    ids = [item["id"] for item in root_map["vulnerabilities"]]
    assert len(ids) == len(set(ids))
    assert len(ids) == 15

    files = [item["file"] for item in root_map["vulnerabilities"] if item.get("file")]
    assert all(os.path.exists(path) for path in files)
