# VulnPy

VulnPy is an intentionally vulnerable Flask blogging app for local security training.
It includes examples of SQL injection, command injection, stored XSS, SSRF,
broken access control, weak password storage, insecure session settings, and
debug information exposure.

Do not expose this application to the public internet.

## Run Locally

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

The direct Flask entry point listens on all interfaces because this is a lab
target. Prefer Docker Compose for a safer local binding.

```sh
docker compose up --build
```

Docker Compose binds the service to `127.0.0.1:5000`.

## Seed Accounts

| Username | Password |
| --- | --- |
| `admin` | `admin123` |
| `alice` | `password` |
| `bob` | `letmein` |

## Vulnerability Hints

The floating hint button loads `static/vuln_map.json` and shows vulnerabilities
mapped to the current page. The source map is also available at `vuln_map.json`.

## Tests

Install test dependencies and run:

```sh
pip install -r requirements-dev.txt
pytest
```

The tests use a temporary database and verify the lab's intended vulnerable
behaviors and mapping consistency. They are not security hardening tests.
