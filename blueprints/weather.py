import requests
from flask import Blueprint, render_template, request

bp = Blueprint("weather", __name__)


@bp.route("/weather")
def weather():
    url = request.args.get("url", "").strip()
    result = None
    error = None

    if url:
        # VULN: CWE-918 (Server-Side Request Forgery), OWASP A10
        # The server fetches any URL the user supplies, including internal services:
        #   /weather?url=http://169.254.169.254/latest/meta-data/  (AWS metadata)
        #   /weather?url=http://localhost:5000/debug                (internal debug endpoint)
        #   /weather?url=file:///etc/passwd                         (local files, depending on requests config)
        try:
            resp = requests.get(url, timeout=5)
            result = {
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.text[:5000],
            }
        except Exception as e:
            error = str(e)

    return render_template("weather.html", url=url, result=result, error=error)
