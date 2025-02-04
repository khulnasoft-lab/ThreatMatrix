# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

from threat_matrix import secrets

# this must be first because the function get_secretes depends from it
AWS_REGION = secrets.get_secret("AWS_REGION", "eu-central-1")
