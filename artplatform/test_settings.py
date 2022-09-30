import dotenv
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.read_dotenv(os.path.join(BASE_DIR, ".env"))

# When testing, there's no celery workers;
# Instead all tasks should execute eagerly
CELERY_TASK_ALWAYS_EAGER = True

from .settings import *  # noqa: F401, F403, E402
