import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        md5_pass = hashlib.md5(password.encode()).hexdigest()

        # VULN: CWE-89 (SQL Injection), OWASP A03
        # User input is interpolated directly into the query string.
        # An attacker can supply: ' OR 1=1 -- as the username to bypass auth.
        db = get_db()
        query = (
            "SELECT * FROM users WHERE username = '%s' AND password = '%s'"
            % (username, md5_pass)
        )
        try:
            user = db.execute(query).fetchone()
        except Exception:
            user = None
        finally:
            db.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Welcome back, %s!" % user["username"], "success")
            return redirect(url_for("blog.index"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        # VULN: CWE-916 (Weak Password Hashing), OWASP A05
        # MD5 is not a password hashing algorithm. Use bcrypt/argon2 instead.
        md5_pass = hashlib.md5(password.encode()).hexdigest()

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, md5_pass),
            )
            db.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            flash("Username already taken.", "error")
        finally:
            db.close()

    return render_template("register.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("blog.index"))
