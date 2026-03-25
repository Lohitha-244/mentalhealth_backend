import os
import django
import time
import urllib.request

print("Starting deep diagnostic test...")
start = time.time()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
try:
    django.setup()
    print(f"django.setup() finished in {time.time() - start:.2f}s")
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print(f"Executing ORM query... User count: {User.objects.count()}")

    print("Testing outbound networking (google.com)...")
    try:
        urllib.request.urlopen("https://www.google.com", timeout=5)
        print("OUTBOUND NETWORKING: SUCCESS")
    except Exception as e:
        print(f"OUTBOUND NETWORKING: FAILED ({e})")

except Exception as e:
    print(f"ERROR: {e}")
