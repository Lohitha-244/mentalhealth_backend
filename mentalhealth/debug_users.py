
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import UserProfile

print("--- User List ---")
for user in User.objects.all():
    print(f"ID: {user.id} | Username: {user.username} | Email: {user.email} | Password: {user.password}")
