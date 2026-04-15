from flask import Blueprint, render_template, request
from db import get_db

bp = Blueprint("search", __name__)


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    error = None

    if q:
        # VULN: CWE-89 (SQL Injection), OWASP A03
        # Search query is interpolated directly into SQL.
        # UNION-based injection: ' UNION SELECT id,username,password,bio,role,created_at FROM users --
        db = get_db()
        query = (
            "SELECT p.id, p.title, p.body, p.tags, p.created_at, u.username as author_name "
            "FROM posts p JOIN users u ON p.author_id = u.id "
            "WHERE p.status = 'published' AND (p.title LIKE '%%%s%%' OR p.body LIKE '%%%s%%') "
            "ORDER BY p.created_at DESC" % (q, q)
        )
        try:
            results = db.execute(query).fetchall()
        except Exception as e:
            error = str(e)
        finally:
            db.close()

    return render_template("search_results.html", q=q, results=results, error=error)
