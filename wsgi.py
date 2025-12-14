"""
WSGI config for online_course project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_course.settings')

application = get_wsgi_application()