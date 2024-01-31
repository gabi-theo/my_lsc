import os

from celery import Celery
from celery.schedules import crontab

__all__ = ("app",)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_lsc.settings")

app = Celery("core", include=["app.tasks"])
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_default_queue = "emails"
app.conf.worker_hijack_root_logger = False
# example of cronjobs:
# app.conf.beat_schedule = {
#     "send-email-every-15-seconds": {
#         "task": "api.tasks.send_email",
#         "schedule": 15.0,
#     },
#     "reset-number-of-trials-every-beginning-of-month": {
#         "task": "api.tasks.reset_trials",
#         "schedule": crontab(0, 0, day_of_month="1"),
#     },
# }
app.autodiscover_tasks()
