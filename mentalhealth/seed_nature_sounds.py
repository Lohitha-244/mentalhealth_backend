import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()

from myapp.models import MusicTrack

def seed_nature_sounds():
    sounds = [
        {"title": "Gentle Rain", "icon": "rain", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "duration_seconds": 300},
        {"title": "Ocean Waves", "icon": "waves", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", "duration_seconds": 450},
        {"title": "Morning Birds", "icon": "birds", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", "duration_seconds": 360},
        {"title": "Night Forest", "icon": "night", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3", "duration_seconds": 600},
        {"title": "Soft Wind", "icon": "wind", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3", "duration_seconds": 240},
        {"title": "Babbling Brook", "icon": "brook", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3", "duration_seconds": 500},
    ]

    # Clear existing nature sounds
    MusicTrack.objects.filter(category="nature").delete()

    for s in sounds:
        MusicTrack.objects.create(
            category="nature",
            title=s["title"],
            icon=s["icon"],
            audio_url=s["audio_url"],
            duration_seconds=s["duration_seconds"],
            is_active=True
        )
    print(f"Successfully seeded {len(sounds)} nature sounds.")

if __name__ == "__main__":
    seed_nature_sounds()
