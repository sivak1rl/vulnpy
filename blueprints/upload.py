import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory

bp = Blueprint("upload", __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


@bp.route("/upload", methods=["GET", "POST"])
def upload_file():
    files = []
    if os.path.isdir(UPLOAD_DIR):
        files = sorted(os.listdir(UPLOAD_DIR), reverse=True)
        files = [f for f in files if f != ".gitkeep"]

    if request.method == "POST":
        f = request.files.get("file")
        if not f or not f.filename:
            flash("No file selected.", "error")
            return redirect(url_for("upload.upload_file"))

        # VULN: CWE-434 (Unrestricted Upload of File with Dangerous Type), OWASP A05
        # No validation on file extension, MIME type, or content.
        # An attacker can upload .html (stored XSS), .py, .sh, or any file type.
        filepath = os.path.join(UPLOAD_DIR, f.filename)
        f.save(filepath)
        flash("File uploaded: %s" % f.filename, "success")
        return redirect(url_for("upload.upload_file"))

    return render_template("upload.html", files=files)


@bp.route("/uploads/<path:filename>")
def serve_upload(filename):
    # VULN: Files are served without Content-Disposition: attachment,
    # so .html files render in the browser (stored XSS via upload).
    return send_from_directory(UPLOAD_DIR, filename)
