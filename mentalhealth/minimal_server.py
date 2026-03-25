import os
import django
from wsgiref.simple_server import make_server
from django.core.wsgi import get_wsgi_application

print("Initializing minimal WSGI server...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()

application = get_wsgi_application()

httpd = make_server('0.0.0.0', 8000, application)
print("Serving on port 8000 (minimal WSGI)...")
httpd.serve_forever()
