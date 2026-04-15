import subprocess
from flask import Blueprint, render_template, request

bp = Blueprint("nettools", __name__, url_prefix="/tools")


@bp.route("/ping", methods=["GET", "POST"])
def ping():
    output = None
    host = ""

    if request.method == "POST":
        host = request.form.get("host", "")

        # VULN: CWE-78 (OS Command Injection), OWASP A03
        # User input is passed directly into a shell command without sanitization.
        # An attacker can supply: 127.0.0.1; cat /etc/passwd
        # or: 127.0.0.1 && whoami
        # to execute arbitrary commands on the server.
        try:
            result = subprocess.run(
                "ping -c 2 " + host,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "Error: command timed out."
        except Exception as e:
            output = "Error: %s" % str(e)

    return render_template("nettools.html", output=output, host=host)
