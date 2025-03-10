# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

# this module must run before the others

from ._util import get_secret
from .aws import AWS_SQS

RESULT_BACKEND = "django-db"
BROKER_URL = get_secret("BROKER_URL", None)
if not BROKER_URL:
    if AWS_SQS:
        BROKER_URL = "sqs://"
    else:
        BROKER_URL = "redis://redis:6379/1"  # 0 is used by channels

DEFAULT_QUEUE = "default"
BROADCAST_QUEUE = "broadcast"
CONFIG_QUEUE = "config"

CELERY_QUEUES = get_secret("CELERY_QUEUES", DEFAULT_QUEUE).split(",")
for queue in [DEFAULT_QUEUE, CONFIG_QUEUE]:
    if queue not in CELERY_QUEUES:
        CELERY_QUEUES.append(queue)
