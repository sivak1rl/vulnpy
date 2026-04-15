from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import query_db, execute_db

bp = Blueprint("admin", __name__, url_prefix="/admin")


# VULN: CWE-284 (Improper Access Control), OWASP A01
# There is NO authentication or authorization check on any admin route.
# Any user (or unauthenticated visitor) can access /admin and manage all posts.


@bp.route("/")
def dashboard():
    posts = query_db(
        "SELECT p.*, u.username as author_name FROM posts p "
        "JOIN users u ON p.author_id = u.id "
        "ORDER BY p.created_at DESC"
    )
    users = query_db("SELECT * FROM users ORDER BY created_at DESC")
    return render_template("admin/dashboard.html", posts=posts, users=users)


@bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    post = query_db("SELECT * FROM posts WHERE id = ?", (post_id,), one=True)
    if not post:
        flash("Post not found.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        tags = request.form.get("tags", "").strip()
        status = request.form.get("status", "published")

        execute_db(
            "UPDATE posts SET title = ?, body = ?, tags = ?, status = ? WHERE id = ?",
            (title, body, tags, status, post_id),
        )
        flash("Post updated.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/post_edit.html", post=post)


@bp.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    execute_db("DELETE FROM posts WHERE id = ?", (post_id,))
    flash("Post deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@bp.route("/user/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    execute_db("DELETE FROM users WHERE id = ?", (user_id,))
    flash("User deleted.", "success")
    return redirect(url_for("admin.dashboard"))
