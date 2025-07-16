# api/wsgi.py

import sys
import os

# Add the Django project root to Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ThreatMatrix"))
)

# Set the Django settings module environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "threat_matrix.settings")

# Import the WSGI application from your existing Django wsgi.py
from threat_matrix.wsgi import application as app
