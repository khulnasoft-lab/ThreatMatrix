# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

# flake8: noqa

# Tests
TEST_RUNNER = "threat_matrix.test_runner.MyTestRunner"

# Application definition
INSTALLED_APPS = [
    # default
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # admin
    "prettyjson",
    # celery, elasticsearch
    "django_celery_results",
    # rest framework libs
    "rest_framework",
    "rest_framework_filters",
    "rest_framework.authtoken",
    # certego libs
    "durin",
    "certego_saas",
    "certego_saas.apps.user",
    "certego_saas.apps.notifications",
    "certego_saas.apps.organization",
    # threatmatrix apps
    "authentication",
    "api_app",
    "api_app.analyzers_manager",
    "api_app.connectors_manager",
    "api_app.visualizers_manager",
    "api_app.playbooks_manager",
    "api_app.pivots_manager",
    "api_app.ingestors_manager",
    "api_app.investigations_manager",
    "api_app.data_model_manager",
    "api_app.engines_manager",
    "api_app.analyzables_manager",
    "api_app.user_events_manager",
    # auth
    "rest_email_auth",
    # performance debugging
    "silk",
    # celery
    "django_celery_beat",
    # websocket
    "channels",
    # tree structure
    "treebeard",
    # shell functionalities
    "django_extensions",
]

from .a_secrets import *  # lgtm [py/polluting-import]
from .auth import *  # lgtm [py/polluting-import]
from .aws import *  # lgtm [py/polluting-import]
from .cache import *  # lgtm [py/polluting-import]

# inject from other modules
from .celery import *  # lgtm [py/polluting-import]
from .certego import *  # lgtm [py/polluting-import]
from .commons import *  # lgtm [py/polluting-import]
from .db import *  # lgtm [py/polluting-import]
from .django import *  # lgtm [py/polluting-import]
from .elasticsearch import *  # lgtm [py/polluting-import]
from .logging import *  # lgtm [py/polluting-import]
from .mail import *  # lgtm [py/polluting-import]
from .rest import *  # lgtm [py/polluting-import]
from .security import *  # lgtm [py/polluting-import]
from .storage import *  # lgtm [py/polluting-import]
from .websocket import *  # lgtm [py/polluting-import]
