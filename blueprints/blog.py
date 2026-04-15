from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import query_db, execute_db, get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    posts = query_db(
        "SELECT p.*, u.username as author_name FROM posts p "
        "JOIN users u ON p.author_id = u.id "
        "WHERE p.status = 'published' "
        "ORDER BY p.created_at DESC"
    )
    return render_template("index.html", posts=posts)


@bp.route("/post/<int:post_id>")
def post_detail(post_id):
    # VULN: CWE-639 (IDOR), OWASP A01
    # No check on post status — draft posts are accessible if you know the ID.
    # An attacker can enumerate /post/1, /post/2, ... to find draft posts
    # belonging to other users.
    post = query_db(
        "SELECT p.*, u.username as author_name FROM posts p "
        "JOIN users u ON p.author_id = u.id "
        "WHERE p.id = ?",
        (post_id,),
        one=True,
    )
    if not post:
        flash("Post not found.", "error")
        return redirect(url_for("blog.index"))

    comments = query_db(
        "SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC",
        (post_id,),
    )
    return render_template("post.html", post=post, comments=comments)


@bp.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    author_name = request.form.get("author_name", "Anonymous")
    body = request.form.get("body", "")

    if not body.strip():
        flash("Comment cannot be empty.", "error")
        return redirect(url_for("blog.post_detail", post_id=post_id))

    # Comment is stored as-is — the XSS vuln is in the template (|safe)
    execute_db(
        "INSERT INTO comments (post_id, author_name, body) VALUES (?, ?, ?)",
        (post_id, author_name, body),
    )
    flash("Comment posted!", "success")
    return redirect(url_for("blog.post_detail", post_id=post_id))


@bp.route("/post/new", methods=["GET", "POST"])
def new_post():
    if "user_id" not in session:
        flash("Please log in to create a post.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        tags = request.form.get("tags", "").strip()
        status = request.form.get("status", "published")

        if not title or not body:
            flash("Title and body are required.", "error")
            return render_template("post_new.html")

        slug = title.lower().replace(" ", "-")
        # rough reading time: ~200 words per minute
        reading_time = max(1, len(body.split()) // 200)

        execute_db(
            "INSERT INTO posts (title, slug, body, author_id, status, tags, reading_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, slug, body, session["user_id"], status, tags, reading_time),
        )
        flash("Post created!", "success")
        return redirect(url_for("blog.index"))

    return render_template("post_new.html")
