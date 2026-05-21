import os
import shutil

import pytest

import config
import db
from app import create_app


@pytest.fixture()
def app(tmp_path, monkeypatch):
    database_path = tmp_path / "vulnpy-test.db"
    upload_path = tmp_path / "uploads"
    upload_path.mkdir()

    monkeypatch.setattr(config, "DATABASE", str(database_path))

    import blueprints.upload as upload

    monkeypatch.setattr(upload, "UPLOAD_DIR", str(upload_path))

    app = create_app()
    app.config.update(TESTING=True)

    yield app

    if database_path.exists():
        database_path.unlink()
    shutil.rmtree(upload_path, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def _login(username="alice", password="password"):
        return client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    return _login
