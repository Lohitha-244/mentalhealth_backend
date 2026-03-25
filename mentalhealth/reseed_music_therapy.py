"""
Reset music tracks: delete ALL, then seed exactly 2-3 per mood.
Run: python reseed_music_therapy.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mentalhealth.settings")
django.setup()

from myapp.models import MusicTrack

# Delete ALL music-category tracks
deleted_count, _ = MusicTrack.objects.filter(category="music").delete()
print(f"Deleted {deleted_count} old music tracks.")

TRACKS = [
    # Calm (3)
    {"mood": "calm", "title": "Ocean Waves",          "icon": "🌊", "description": "Soothing sounds of the Pacific ocean",          "duration_seconds": 300},
    {"mood": "calm", "title": "Mountain Stream",      "icon": "🏔️", "description": "Gentle water flowing through rocks",            "duration_seconds": 300},
    {"mood": "calm", "title": "Summer Rain",          "icon": "🌦️", "description": "Soft rhythmic rain on leaves",                 "duration_seconds": 300},

    # Peace (3) - NEW
    {"mood": "peace", "title": "Zen Sanctuary",        "icon": "🧘", "description": "Deeply peaceful temple atmosphere",           "duration_seconds": 480},
    {"mood": "peace", "title": "Inner Harmony",       "icon": "🕊️", "description": "Resonant singing bowls and soft hums",        "duration_seconds": 480},
    {"mood": "peace", "title": "Evening Stillness",   "icon": "🌌", "description": "A quiet night in a peaceful valley",          "duration_seconds": 600},

    # Happy (2)
    {"mood": "happy", "title": "Morning Sunshine",    "icon": "☀️", "description": "Uplifting and bright acoustic melodies",       "duration_seconds": 240},
    {"mood": "happy", "title": "Forest Celebration",  "icon": "🦜", "description": "Cheerful birds and lively nature sounds",      "duration_seconds": 300},

    # Focus (2)
    {"mood": "focus", "title": "Deep Concentration",  "icon": "🧠", "description": "Binaural tones for mental clarity",            "duration_seconds": 600},
    {"mood": "focus", "title": "Steady Breeze",       "icon": "🌬️", "description": "Consistent white noise of a gentle wind",     "duration_seconds": 480},

    # Energize (2)
    {"mood": "energize", "title": "Vitality Pump",    "icon": "⚡", "description": "High-energy rhythmic pulses",                  "duration_seconds": 240},
    {"mood": "energize", "title": "Sunrise Energy",   "icon": "🌅", "description": "Invigorating sounds to start your day",        "duration_seconds": 300},

    # Sleep (2)
    {"mood": "sleep", "title": "Deep Slumber",        "icon": "🌙", "description": "Low-frequency ambient for deep sleep",         "duration_seconds": 600},
    {"mood": "sleep", "title": "Crickets Night",      "icon": "🦗", "description": "Natural nighttime insect chorus",              "duration_seconds": 540},

    # Meditative (2)
    {"mood": "meditative", "title": "Sacred Silence", "icon": "🕉️", "description": "Profound silence with occasional chimes",      "duration_seconds": 480},
    {"mood": "meditative", "title": "Cosmic Union",   "icon": "✨", "description": "Ethereal soundscapes for meditation",          "duration_seconds": 600},
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

print(f"\nDone! Created {len(TRACKS)} music tracks.")
