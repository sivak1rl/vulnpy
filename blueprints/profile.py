from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import query_db, execute_db

bp = Blueprint("profile", __name__)


@bp.route("/user/<username>")
def view_profile(username):
    user = query_db(
        "SELECT * FROM users WHERE username = ?", (username,), one=True
    )
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("blog.index"))

    posts = query_db(
        "SELECT * FROM posts WHERE author_id = ? AND status = 'published' "
        "ORDER BY created_at DESC",
        (user["id"],),
    )
    return render_template("profile.html", user=user, posts=posts)


@bp.route("/user/<username>/edit", methods=["GET", "POST"])
def edit_profile(username):
    if "user_id" not in session:
        flash("Please log in.", "error")
        return redirect(url_for("auth.login"))

    user = query_db(
        "SELECT * FROM users WHERE username = ?", (username,), one=True
    )
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("blog.index"))

    # VULN: CWE-639 (IDOR), OWASP A01
    # Any logged-in user can edit any other user's profile — no ownership check.

    if request.method == "POST":
        bio = request.form.get("bio", "")
        # Bio is stored as-is. The XSS vuln is in the template (|safe).
        execute_db("UPDATE users SET bio = ? WHERE id = ?", (bio, user["id"]))
        flash("Profile updated.", "success")
        return redirect(url_for("profile.view_profile", username=username))

    return render_template("profile_edit.html", user=user)
