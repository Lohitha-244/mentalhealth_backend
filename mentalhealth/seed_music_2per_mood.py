"""
Reset music tracks: delete ALL, then seed exactly 2 per mood.
Run: python seed_music_2per_mood.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mentalhealth.settings")
django.setup()

from myapp.models import MusicTrack

# Delete ALL music-category tracks
deleted_count, _ = MusicTrack.objects.filter(category="music").delete()
print(f"Deleted {deleted_count} old music tracks.")

TRACKS = [
    # Calm (2)
    {"mood": "calm", "title": "Ocean Breeze",     "icon": "🌊", "description": "Gentle ocean waves with soft piano melodies",      "duration_seconds": 300},
    {"mood": "calm", "title": "Zen Garden",        "icon": "🎋", "description": "Traditional Japanese zen garden atmosphere",       "duration_seconds": 300},

    # Happy (2)
    {"mood": "happy", "title": "Sunshine Vibes",   "icon": "☀️", "description": "Uplifting acoustic guitar melodies",               "duration_seconds": 240},
    {"mood": "happy", "title": "Morning Joy",      "icon": "🌅", "description": "Bright and cheerful morning tunes",                "duration_seconds": 300},

    # Focus (2)
    {"mood": "focus", "title": "Deep Concentration","icon": "🧠", "description": "Binaural beats for enhanced focus",               "duration_seconds": 600},
    {"mood": "focus", "title": "Study Lounge",     "icon": "📚", "description": "Lo-fi beats for productive study sessions",        "duration_seconds": 480},

    # Energize (2)
    {"mood": "energize", "title": "Power Up",      "icon": "🔥", "description": "High-energy beats to kickstart your day",          "duration_seconds": 240},
    {"mood": "energize", "title": "Workout Pump",  "icon": "💪", "description": "Intense rhythms for workout motivation",           "duration_seconds": 300},

    # Sleep (2)
    {"mood": "sleep", "title": "Dreamscape",       "icon": "🌙", "description": "Ultra-soft ambient for deep sleep induction",      "duration_seconds": 600},
    {"mood": "sleep", "title": "Midnight Rain",    "icon": "🌧️", "description": "Soft rain and thunder for sleep",                  "duration_seconds": 540},

    # Meditative (2)
    {"mood": "meditative", "title": "Inner Peace",  "icon": "🕉️", "description": "Traditional meditation bowls and chimes",         "duration_seconds": 480},
    {"mood": "meditative", "title": "Sacred Silence","icon": "🧘", "description": "Minimal ambient for deep meditation",             "duration_seconds": 600},
]

for t in TRACKS:
    obj = MusicTrack.objects.create(
        category="music",
        mood=t["mood"],
        title=t["title"],
        icon=t["icon"],
        description=t["description"],
        audio_url="",
        duration_seconds=t["duration_seconds"],
        is_active=True,
    )
    print(f"  Created #{obj.id}: {obj.title} ({obj.mood})")

print(f"\nDone! Created {len(TRACKS)} music tracks (2 per mood).")
