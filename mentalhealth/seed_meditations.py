import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()

from myapp.models import MeditationProgram

def seed_meditation_programs():
    programs = [
        {
            "title": "Morning Calm",
            "category": "morning",
            "description": "Mindful awakening for a fresh start.",
            "duration_seconds": 300,
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", # Real test audio
            "is_active": True
        },
         {
            "title": "Stress Relief",
            "category": "stress",
            "description": "Quick relief for a busy mind.",
            "duration_seconds": 600,
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            "is_active": True
        },
         {
            "title": "Deep Relaxation",
            "category": "deep",
            "description": "Deep calming session for full body reset.",
            "duration_seconds": 900,
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            "is_active": True
        },
         {
            "title": "Sleep Preparation",
            "category": "sleep",
            "description": "Wind down with soothing tones.",
            "duration_seconds": 600,
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
            "is_active": True
        }
    ]

    for p in programs:
        exist = MeditationProgram.objects.filter(title=p["title"]).exists()
        if not exist:
            MeditationProgram.objects.create(**p)
            print(f"Created: {p['title']}")
        else:
            print(f"Exists: {p['title']}")

if __name__ == "__main__":
    seed_meditation_programs()
