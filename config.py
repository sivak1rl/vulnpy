# VULN: CWE-321 (Hardcoded Cryptographic Key), OWASP A05
# The secret key is hardcoded and trivially guessable.
# This allows session forgery and cookie tampering.

import os

SECRET_KEY = "dev"

DATABASE = os.path.join(os.path.dirname(__file__), "vulnpy.db")

# VULN: CWE-215 (Information Exposure Through Debug Information), OWASP A05
# Debug mode is left enabled, exposing stack traces and the interactive debugger.
DEBUG = True
