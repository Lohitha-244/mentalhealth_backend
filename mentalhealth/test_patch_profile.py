import os
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()

from myapp.views import ProfileView

def test_patch():
    User = get_user_model()
    user = User.objects.get(username='agent1')
    
    factory = APIRequestFactory()
    view = ProfileView.as_view()
    
    # Test PATCH
    request = factory.patch('/api/profile/', {'first_name': 'Lohi_Updated'}, format='json')
    force_authenticate(request, user=user)
    response = view(request)
    
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
    
    if response.status_code == 200:
        print("✅ PATCH method supported and worked correctly")
    else:
        print(f"❌ PATCH failed with status {response.status_code}")

if __name__ == "__main__":
    test_patch()
