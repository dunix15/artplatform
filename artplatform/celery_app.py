import os

import dotenv
from celery import Celery

# find the django config env file
# Stack Overflow: 57525847
env_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), ".env"
)
dotenv.read_dotenv(env_file)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artplatform.settings")

app = Celery("artplatform")

# Pull configuration values from the main config file
# that begin with "CELERY_"
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
