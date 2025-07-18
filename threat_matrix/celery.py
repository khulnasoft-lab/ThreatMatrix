# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

from __future__ import absolute_import, unicode_literals

import logging
import os
import uuid
from typing import Dict

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from kombu import Queue
from kombu.common import Broadcast

from threat_matrix.settings import STAGE_PRODUCTION, STAGE_STAGING

logger = logging.getLogger(__name__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "threat_matrix.settings")

app = Celery("threat_matrix")


def get_queue_url(queue):
    if STAGE_PRODUCTION:
        SQS_QUEUE = "prod"
    elif STAGE_STAGING:
        SQS_QUEUE = "stag"
    else:
        SQS_QUEUE = "test"
    return f"threatmatrix-{SQS_QUEUE}-{get_queue_name(queue)}"


def get_queue_name(queue: str) -> str:
    if not settings.AWS_SQS:
        return queue
    return f"{queue}.fifo"


if settings.AWS_SQS:
    PREDEFINED_QUEUES = {
        get_queue_name(queue): {
            "url": f"https://sqs.{settings.AWS_REGION}"
            f".amazonaws.com/{settings.AWS_USER_NUMBER}/"
            f"{get_queue_url(queue)}"
        }
        for queue in settings.CELERY_QUEUES
    }
    # in this way they are printed in the Docker logs
    logger.info(f"predefined queues active: {PREDEFINED_QUEUES}")

    BROKER_TRANSPORT_OPTIONS = {
        "region": settings.AWS_REGION,
        "predefined_queues": PREDEFINED_QUEUES,
        "max_retries": 0,
        "polling_interval": 2,
        "wait_time_seconds": 0,
        # this is the highest possible value
        # https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/sqs.html#caveats
        # this must be longer than the longest possible task we execute
        "visibility_timeout": 43200,
    }
    if not settings.AWS_IAM_ACCESS:
        BROKER_TRANSPORT_OPTIONS["access_key_id"] = settings.AWS_ACCESS_KEY_ID
        BROKER_TRANSPORT_OPTIONS["secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
else:
    BROKER_TRANSPORT_OPTIONS = {
        "priority_steps": list(range(10)),
        "sep": ":",
        "queue_order_strategy": "priority",
        "task_default_priority": 7,
    }

task_queues = [
    Queue(get_queue_name(key), routing_key=key, queue_arguments={"x-max-priority": 10})
    for key in settings.CELERY_QUEUES
]
if not settings.AWS_SQS:
    task_queues.append(
        Broadcast(
            name=settings.BROADCAST_QUEUE,
            queue=get_queue_name(settings.BROADCAST_QUEUE),
            routing_key=settings.BROADCAST_QUEUE,
            unique=False,
            auto_delete=False,
        )
    )
app.conf.update(
    task_default_queue=get_queue_name(settings.DEFAULT_QUEUE),
    task_queues=task_queues,
    task_time_limit=1800,
    broker_url=settings.BROKER_URL,
    result_backend=settings.RESULT_BACKEND,
    accept_content=["application/json"],
    task_serializer="json",
    result_serializer="json",
    imports=(
        "threat_matrix.tasks",
        "api_app.engines_manager.tasks",
        "api_app.user_events_manager.tasks",
    ),
    worker_redirect_stdouts=False,
    worker_hijack_root_logger=False,
    # this is to avoid RAM issues caused by long usage of this tool
    # changing the child saves from memory leaks but is CPU intensive...so care
    worker_max_tasks_per_child=1000,
    # name is in kilobytes
    # https://medium.com/squad-engineering
    # /two-years-with-celery-in-production-bug-fix-edition-22238669601d
    # they suggest to remove this but well...maybe just put this a huge number
    # there are workers in the primary queue that use a lot of memory
    worker_max_memory_per_child=3000000,
    worker_proc_alive_timeout=20,
    # these two are needed to enable priority and correct tasks execution
    # see: https://docs.celeryq.dev/en/stable
    # /userguide/optimizing.html#reserve-one-task-at-a-time
    # UPDATE: we disabled task_acks_late because not useful.
    # We don't need to acks late because we don't want to re-get the same message
    # task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_transport_options=BROKER_TRANSPORT_OPTIONS,
    # The remote control command pool_restart sends restart requests
    # to the workers child processes.
    # It is particularly useful for forcing the worker to import new modules,
    # or for reloading already imported modules.
    # This command does not interrupt executing tasks.
    worker_pool_restarts=True,
    # required for code-coverage to work properly in tests
    task_always_eager=settings.STAGE_CI,
)

app.conf.beat_schedule = {
    "send_elastic_bi": {
        "task": "send_bi_to_elastic",
        "schedule": crontab(minute="12"),
        "options": {
            "queue": get_queue_name(settings.DEFAULT_QUEUE),
            "MessageGroupId": str(uuid.uuid4()),
        },
    },
    "send_plugin_report_to_elastic": {
        "task": "send_plugin_report_to_elastic",
        "schedule": crontab(minute="*"),
        "options": {
            "queue": get_queue_name(settings.DEFAULT_QUEUE),
            "MessageGroupId": str(uuid.uuid4()),
        },
    },
    "remove_old_jobs": {
        "task": "threat_matrix.tasks.remove_old_jobs",
        "schedule": crontab(minute="10", hour="2"),
        "options": {
            "queue": get_queue_name(settings.DEFAULT_QUEUE),
            "MessageGroupId": str(uuid.uuid4()),
        },
    },
    "check_stuck_analysis": {
        "task": "threat_matrix.tasks.check_stuck_analysis",
        "schedule": crontab(minute="*/5"),
        "kwargs": {"check_pending": True},
        "options": {
            "queue": get_queue_name(settings.DEFAULT_QUEUE),
            "MessageGroupId": str(uuid.uuid4()),
        },
    },
    "update_notifications_with_releases": {
        "task": "threat_matrix.tasks.update_notifications_with_releases",
        "schedule": crontab(minute="0", hour="22"),
        "options": {
            "queue": get_queue_name(settings.DEFAULT_QUEUE),
            "MessageGroupId": str(uuid.uuid4()),
        },
    },
    "user_events_decay": {
        "task": "api_app.user_events_manager.tasks.user_events_decay",
        "schedule": crontab(hour="3,22", minute="12"),
        "options": {
            "queue": get_queue_name(settings.DEFAULT_QUEUE),
            "MessageGroupId": str(uuid.uuid4()),
        },
    },
}
app.autodiscover_tasks()


def broadcast(function, queue: str = None, arguments: Dict = None):
    if settings.AWS_SQS:
        raise NotImplementedError("SQS does not support the broadcast at the moment.")
    else:
        if queue:
            if queue not in settings.CELERY_QUEUES:
                queue = settings.DEFAULT_QUEUE
            queue = [f"celery@worker_{queue}"]
        app.control.broadcast(function.__name__, destination=queue, arguments=arguments)
