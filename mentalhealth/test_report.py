import os
import sys
import django

sys.path.append(r"c:\Users\kamat\OneDrive\Desktop\django\mentalhealth")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mentalhealth.settings")
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from myapp.views import WeeklyReportAPIView, MonthlyReportAPIView

User = get_user_model()
user = User.objects.first()

if not user:
    print("No user found")
    sys.exit(1)

factory = APIRequestFactory()

request = factory.get('/api/progress/weekly/')
force_authenticate(request, user=user)
response = WeeklyReportAPIView.as_view()(request)
print("Weekly Status:", response.status_code)
if response.status_code == 200:
    print("Weekly Data:", response.data)
else:
    print("Weekly Error:", getattr(response, 'data', None))

request = factory.get('/api/progress/monthly/')
force_authenticate(request, user=user)
response = MonthlyReportAPIView.as_view()(request)
print("Monthly Status:", response.status_code)
if response.status_code == 200:
    print("Monthly Data:", response.data)
else:
    print("Monthly Error:", getattr(response, 'data', None))
