"""
Seed script for Music Therapy tracks.
Run: python manage.py shell < seed_music_tracks.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mentalhealth.settings")
django.setup()

from myapp.models import MusicTrack

TRACKS = [
    # Calm
    {"category": "music", "mood": "calm", "title": "Ocean Breeze", "icon": "🌊", "description": "Gentle ocean waves with soft piano melodies", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "duration_seconds": 300},
    {"category": "music", "mood": "calm", "title": "Tranquil Forest", "icon": "🌲", "description": "Peaceful forest ambiance with bird songs", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", "duration_seconds": 360},
    {"category": "music", "mood": "calm", "title": "Soft Rain", "icon": "🌧️", "description": "Soothing rain sounds for deep relaxation", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", "duration_seconds": 420},
    {"category": "music", "mood": "calm", "title": "Zen Garden", "icon": "🎋", "description": "Traditional Japanese zen garden atmosphere", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3", "duration_seconds": 300},

    # Happy
    {"category": "music", "mood": "happy", "title": "Sunshine Vibes", "icon": "☀️", "description": "Uplifting acoustic guitar melodies", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3", "duration_seconds": 240},
    {"category": "music", "mood": "happy", "title": "Morning Joy", "icon": "🌅", "description": "Bright and cheerful morning tunes", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3", "duration_seconds": 300},
    {"category": "music", "mood": "happy", "title": "Feel Good Beats", "icon": "🎶", "description": "Light rhythmic beats to boost your mood", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3", "duration_seconds": 280},
    {"category": "music", "mood": "happy", "title": "Spring Bloom", "icon": "🌸", "description": "Delicate floral-themed melodies", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3", "duration_seconds": 330},

    # Focus
    {"category": "music", "mood": "focus", "title": "Deep Concentration", "icon": "🧠", "description": "Binaural beats for enhanced focus", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3", "duration_seconds": 600},
    {"category": "music", "mood": "focus", "title": "Study Lounge", "icon": "📚", "description": "Lo-fi beats for productive study sessions", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3", "duration_seconds": 480},
    {"category": "music", "mood": "focus", "title": "Brain Waves", "icon": "⚡", "description": "Alpha wave frequencies for mental clarity", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3", "duration_seconds": 540},
    {"category": "music", "mood": "focus", "title": "Coding Flow", "icon": "💻", "description": "Ambient electronic for deep work", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3", "duration_seconds": 600},

    # Energize
    {"category": "music", "mood": "energize", "title": "Power Up", "icon": "🔥", "description": "High-energy beats to kickstart your day", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3", "duration_seconds": 240},
    {"category": "music", "mood": "energize", "title": "Adrenaline Rush", "icon": "💪", "description": "Intense rhythms for workout motivation", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3", "duration_seconds": 300},
    {"category": "music", "mood": "energize", "title": "Electric Pulse", "icon": "⚡", "description": "Pulsating electronic energy tracks", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3", "duration_seconds": 280},
    {"category": "music", "mood": "energize", "title": "Victory March", "icon": "🏆", "description": "Triumphant orchestral compositions", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3", "duration_seconds": 320},

    # Sleep
    {"category": "music", "mood": "sleep", "title": "Dreamscape", "icon": "🌙", "description": "Ultra-soft ambient for deep sleep induction", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "duration_seconds": 600},
    {"category": "music", "mood": "sleep", "title": "Lullaby Nights", "icon": "🌟", "description": "Gentle lullaby melodies for peaceful rest", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", "duration_seconds": 480},
    {"category": "music", "mood": "sleep", "title": "Midnight Rain", "icon": "🌧️", "description": "Soft rain and thunder for sleep", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", "duration_seconds": 540},
    {"category": "music", "mood": "sleep", "title": "Deep Slumber", "icon": "😴", "description": "Delta wave frequencies for deep sleep", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3", "duration_seconds": 600},

    # Meditative
    {"category": "music", "mood": "meditative", "title": "Inner Peace", "icon": "🕉️", "description": "Traditional meditation bowls and chimes", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3", "duration_seconds": 480},
    {"category": "music", "mood": "meditative", "title": "Sacred Silence", "icon": "🧘", "description": "Minimal ambient for deep meditation", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3", "duration_seconds": 600},
    {"category": "music", "mood": "meditative", "title": "Chakra Harmony", "icon": "🔮", "description": "Chakra balancing frequency tones", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3", "duration_seconds": 540},
    {"category": "music", "mood": "meditative", "title": "Temple Bells", "icon": "🔔", "description": "Serene temple bell meditation sounds", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3", "duration_seconds": 420},
]

created = 0
for t in TRACKS:
    obj, was_created = MusicTrack.objects.get_or_create(
        title=t["title"],
        category=t["category"],
        mood=t["mood"],
        defaults={
            "icon": t["icon"],
            "description": t["description"],
            "audio_url": t["audio_url"],
            "duration_seconds": t["duration_seconds"],
            "is_active": True,
        },
    )
    if was_created:
        created += 1
        print(f"  [OK] Created: {obj.title} ({obj.mood})")
    else:
        print(f"  [SKIP] Already exists: {obj.title}")

print(f"\nDone! Created {created} new music tracks.")
