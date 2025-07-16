from __future__ import absolute_import, unicode_literals

import datetime
import logging

from celery import Task, shared_task
from celery.worker.control import control_command
from celery.worker.request import Request
from django.conf import settings
from django.utils.timezone import now

from threat_matrix import secrets

logger = logging.getLogger(__name__)


# === Custom Celery Classes === #
class FailureLoggedRequest(Request):
    def on_timeout(self, soft, timeout):
        result = super().on_timeout(soft, timeout)
        if not soft:
            logger.warning(f"A hard timeout was enforced for task {self.task.name}")
        return result

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        logger.critical(
            f"Failure detected for task {self.task.name} with exception {exc_info} and request {self._request_dict}"
        )
        return super().on_failure(exc_info, send_failed_event, return_ok)


class FailureLoggedTask(Task):
    Request = FailureLoggedRequest


# === Control Commands === #
@control_command(args=[("python_module_pk", int)])
def update_plugin(state, python_module_pk: int):
    from api_app.models import PythonModule

    pm = PythonModule.objects.get(pk=python_module_pk)
    pm.python_class.update()


# === Shared Tasks === #


@shared_task(base=FailureLoggedTask, name="execute_ingestor", soft_time_limit=300)
def execute_ingestor(config_name: str):
    from api_app.ingestors_manager.models import IngestorConfig

    config = IngestorConfig.objects.get(name=config_name)
    if config.disabled:
        logger.info(f"Not executing ingestor {config.name} because disabled")
        return

    class_ = config.python_module.python_class
    obj = class_(config=config)
    obj.start({}, None, None)
    logger.info(f"Executing ingestor {config.name}")


@shared_task(base=FailureLoggedTask, name="remove_old_jobs", soft_time_limit=10000)
def remove_old_jobs():
    from api_app.models import Job

    logger.info("started remove_old_jobs")
    retention_days = int(secrets.get_secret("OLD_JOBS_RETENTION_DAYS", 14))
    date_to_check = now() - datetime.timedelta(days=retention_days)
    old_jobs = Job.objects.filter(finished_analysis_time__lt=date_to_check)
    logger.info(f"found {old_jobs.count()} old jobs to delete")

    for job in old_jobs.iterator():
        if job.analyzable.jobs.count() == 1 and job.analyzable.file:
            job.analyzable.file.delete()
        try:
            job.delete()
        except Exception as e:
            logger.warning(
                f"Failed to delete job {job.id}. Error: {e}", stack_info=True
            )

    logger.info("finished remove_old_jobs")
    return old_jobs.count()


@shared_task(base=FailureLoggedTask, name="refresh_cache", soft_time_limit=120)
def refresh_cache(python_class_str: str):
    from django.utils.module_loading import import_string

    from api_app.models import PythonConfig

    logger.info(f"Refreshing cache for {python_class_str}")
    python_class = import_string(python_class_str)
    python_class.delete_class_cache_keys()

    if issubclass(python_class, PythonConfig):
        for config in python_class.objects.all():
            config.refresh_cache_keys()


@shared_task(base=FailureLoggedTask, name="check_stuck_analysis", soft_time_limit=120)
def check_stuck_analysis(minutes_ago: int = 25, check_pending: bool = False):
    from api_app.models import Job

    def fail_job(job):
        logger.error(f"found stuck analysis, job_id:{job.id}. Setting status to FAILED")
        job.status = Job.STATUSES.FAILED.value
        job.finished_analysis_time = now()
        job.save(update_fields=["status", "finished_analysis_time"])

    logger.info("started check_stuck_analysis")
    running_jobs = Job.objects.running(
        check_pending=check_pending, minutes_ago=minutes_ago
    )
    logger.info(f"checking if {running_jobs.count()} jobs are stuck")

    stuck_ids = []
    for job in running_jobs:
        stuck_ids.append(job.id)
        if job.status == Job.STATUSES.RUNNING.value:
            fail_job(job)
        elif job.status == Job.STATUSES.PENDING.value:
            if job.received_request_time < (
                now() - datetime.timedelta(minutes=(minutes_ago * 2) + 1)
            ):
                fail_job(job)
            elif job.received_request_time < (
                now() - datetime.timedelta(minutes=minutes_ago)
            ):
                logger.info(f"Re-running job {job.id}")
                job.retry()

    logger.info("finished check_stuck_analysis")
    return stuck_ids


@shared_task(base=FailureLoggedTask, name="update", soft_time_limit=150)
def update(python_module_pk: int):
    from api_app.models import PythonModule
    from threat_matrix.celery import broadcast

    module = PythonModule.objects.get(pk=python_module_pk)
    if settings.NFS:
        update_plugin(None, python_module_pk)
    else:
        for queue in {c.queue for c in module.configs}:
            broadcast(
                update_plugin,
                queue=queue,
                arguments={"python_module_pk": python_module_pk},
            )


# Additional task definitions remain unchanged but should follow similar cleanup:
# - health_check
# - update_notifications_with_releases
# - job_set_final_status
# - job_set_pipeline_status
# - job_pipeline
# - run_plugin
# - create_caches
# - beat_init_connect
# - send_bi_to_elastic
# - send_plugin_report_to_elastic
# - enable_configuration_for_org_for_rate_limit
# - config_loggers

# For brevity, those are omitted here but I can refactor those as well if you'd like.
