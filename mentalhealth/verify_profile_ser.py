import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()
from myapp.models import UserProfile
from myapp.serializers import ProfileSerializer
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='agent1')
profile = UserProfile.objects.get(user=u)
ser = ProfileSerializer(profile)
d = ser.data
print(f"Streak: {d['streak_days']}")
print(f"Level: {d['level']}")
print(f"Wellness: {d['wellness_score']}")
print(f"Days Active: {d['days_active']}")
