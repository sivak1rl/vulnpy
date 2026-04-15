import os
import sys
import sqlite3
from flask import Blueprint, render_template, current_app
import config

bp = Blueprint("debug", __name__)


@bp.route("/debug")
def debug_info():
    # VULN: CWE-215 (Information Exposure Through Debug Information), OWASP A05
    # This endpoint exposes environment variables, application config,
    # Python version, database path, and table schemas to anyone — no auth required.

    env_vars = dict(os.environ)

    app_config = {
        k: str(v) for k, v in current_app.config.items()
        if k not in ("PERMANENT_SESSION_LIFETIME",)
    }

    db_info = {}
    try:
        db = sqlite3.connect(config.DATABASE)
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            cols = db.execute("PRAGMA table_info(%s)" % table).fetchall()
            db_info[table] = [
                {"name": col[1], "type": col[2], "notnull": col[3], "pk": col[5]}
                for col in cols
            ]
        db.close()
    except Exception as e:
        db_info = {"error": str(e)}

    sys_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "executable": sys.executable,
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "db_path": config.DATABASE,
    }

    return render_template(
        "debug.html",
        env_vars=env_vars,
        app_config=app_config,
        db_info=db_info,
        sys_info=sys_info,
    )
