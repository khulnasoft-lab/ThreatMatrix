# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

# flake8: noqa E501

from datetime import timedelta

from .commons import VERSION
from .security import WEB_CLIENT_URL

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # Auth
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "certego_saas.ext.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
    # Permission
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # Exception Handling
    "EXCEPTION_HANDLER": "api_app.exceptions.logging_exception_handler",
    # Filter
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework_filters.backends.RestFrameworkFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
}

# Django-Rest-Durin
REST_DURIN = {
    "DEFAULT_TOKEN_TTL": timedelta(days=14),
    "TOKEN_CHARACTER_LENGTH": 32,
    "USER_SERIALIZER": "certego_saas.apps.user.serializers.UserSerializer",
    "AUTH_HEADER_PREFIX": "Token",
    "TOKEN_CACHE_TIMEOUT": 300,  # 5 minutes
    "REFRESH_TOKEN_ON_LOGIN": True,
    "API_ACCESS_CLIENT_NAME": "PyThreatMatrix",
    "API_ACCESS_EXCLUDE_FROM_SESSIONS": True,
    "API_ACCESS_RESPONSE_INCLUDE_TOKEN": True,
    # not part of durin but used in data migration
    "API_ACCESS_CLIENT_TOKEN_TTL": timedelta(days=3650),
}

# django-rest-email-auth
REST_EMAIL_AUTH = {
    "EMAIL_VERIFICATION_URL": WEB_CLIENT_URL + "/verify-email?key={key}",
    "PASSWORD_RESET_URL": WEB_CLIENT_URL + "/reset-password?key={key}",
    "REGISTRATION_SERIALIZER": "authentication.serializers.RegistrationSerializer",
    "EMAIL_VERIFICATION_PASSWORD_REQUIRED": False,
    "EMAIL_SUBJECT_VERIFICATION": "ThreatMatrix - Please Verify Your Email Address",
    "EMAIL_SUBJECT_DUPLICATE": "ThreatMatrix - Registration Attempt",
    "PATH_TO_VERIFY_EMAIL_TEMPLATE": "authentication/emails/verify-email",
    "PATH_TO_DUPLICATE_EMAIL_TEMPLATE": "authentication/emails/duplicate-email",
    "PATH_TO_RESET_EMAIL_TEMPLATE": "authentication/emails/reset-password",
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "ThreatMatrix API specification",
    "VERSION": VERSION,
}

# required by the certego-saas, but GreedyBear doesn't use the recaptcha, for this reason is filled with a placeholder
DRF_RECAPTCHA_SECRET_KEY = "not-active"
