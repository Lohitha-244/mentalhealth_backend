import os
import django
from django.utils import timezone
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()

from myapp.models import UserStats, MoodCheckIn, UserProfile
from myapp.serializers import ProfileSerializer

def test_full_flow():
    User = get_user_model()
    user = User.objects.get(username='agent1')
    
    # Clear existing mood checkins for test
    MoodCheckIn.objects.filter(user=user).delete()
    
    stats, _ = UserStats.objects.get_or_create(user=user)
    stats.streak_days = 0
    stats.save()
    
    print("Initial check done.")
    
    # Create a real mood checkin
    print("Creating real MoodCheckIn...")
    MoodCheckIn.objects.create(user=user, mood='great', stress_level=2)
    
    # The view would normally call these:
    from myapp.views import award_user_xp, update_user_streak
    award_user_xp(user, xp=15, coins=5)
    update_user_streak(user)
    
    profile = UserProfile.objects.get(user=user)
    ser = ProfileSerializer(profile)
    d = ser.data
    
    print(f"Results - Days: {d['days_active']}, Level: {d['level']}, Wellness: {d['wellness_score']}%")
    
    if d['days_active'] == 1:
        print("✅ Days Active updated correctly")
    else:
        print(f"❌ Days Active mismatch: {d['days_active']}")
        
    if d['wellness_score'] == 12: # 2 (streak) + 10 (mood activity)
        print("✅ Wellness Score calculated correctly")
    else:
        print(f"❌ Wellness Score mismatch: {d['wellness_score']}")

if __name__ == "__main__":
    test_full_flow()
