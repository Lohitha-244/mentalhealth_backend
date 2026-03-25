import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentalhealth.settings')
django.setup()

from myapp.models import MusicTrack, BodyScanStep, Affirmation

def seed_all():
    # 1. Nature Sounds
    nature_sounds = [
        {"title": "Gentle Rain", "icon": "rain", "audio_url": "https://assets.mixkit.co/sfx/preview/mixkit-light-rain-loop-2393.mp3", "duration_seconds": 300},
        {"title": "Ocean Waves", "icon": "waves", "audio_url": "https://assets.mixkit.co/sfx/preview/mixkit-ocean-waves-loop-1196.mp3", "duration_seconds": 450},
        {"title": "Morning Birds", "icon": "birds", "audio_url": "https://assets.mixkit.co/sfx/preview/mixkit-morning-birds-2474.mp3", "duration_seconds": 360},
        {"title": "Night Forest", "icon": "night", "audio_url": "https://assets.mixkit.co/sfx/preview/mixkit-crickets-in-the-night-forest-loop-2402.mp3", "duration_seconds": 600},
        {"title": "Soft Wind", "icon": "wind", "audio_url": "https://assets.mixkit.co/sfx/preview/mixkit-wind-blowing-ambience-loop-1158.mp3", "duration_seconds": 240},
        {"title": "Babbling Brook", "icon": "brook", "audio_url": "https://assets.mixkit.co/sfx/preview/mixkit-woodland-stream-loop-2399.mp3", "duration_seconds": 500},
    ]

    # 2. Music Therapy (Mood-based)
    mood_records = [
        {"title": "Celestial Serenity", "category": "music", "mood": "Calm", "audio_url": "https://assets.mixkit.co/music/preview/mixkit-serenity-614.mp3", "duration_seconds": 300},
        {"title": "Morning Delight", "category": "music", "mood": "Happy", "audio_url": "https://assets.mixkit.co/music/preview/mixkit-delight-613.mp3", "duration_seconds": 240},
        {"title": "Infinite Focus", "category": "music", "mood": "Focus", "audio_url": "https://assets.mixkit.co/music/preview/mixkit-deep-meditation-602.mp3", "duration_seconds": 600},
        {"title": "Urban Energy", "category": "music", "mood": "Energize", "audio_url": "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3", "duration_seconds": 400},
        {"title": "Whispering Dreams", "category": "music", "mood": "Sleep", "audio_url": "https://assets.mixkit.co/music/preview/mixkit-sleepy-cat-625.mp3", "duration_seconds": 900},
        {"title": "Eternal Zen", "category": "music", "mood": "Meditative", "audio_url": "https://assets.mixkit.co/music/preview/mixkit-zen-meditation-601.mp3", "duration_seconds": 1200},
    ]

    # Clear existing music tracks
    MusicTrack.objects.all().delete()

    for s in nature_sounds:
        MusicTrack.objects.create(
            category="nature",
            title=s["title"],
            icon=s["icon"],
            audio_url=s["audio_url"],
            duration_seconds=s["duration_seconds"],
            is_active=True
        )
    
    for m in mood_records:
        MusicTrack.objects.create(
            category=m["category"],
            title=m["title"],
            mood=m["mood"],
            audio_url=m["audio_url"],
            duration_seconds=m["duration_seconds"],
            is_active=True
        )

    # 3. Body Scan Steps
    body_steps = [
        {"title": "Hands & Fists", "emoji": "👊", "order": 1, "instructions": "Clench your fists tightly, then release completely"},
        {"title": "Arms & Shoulders", "emoji": "💪", "order": 2, "instructions": "Pull shoulders to ears, then let them drop"},
        {"title": "Face & Jaw", "emoji": "😬", "order": 3, "instructions": "Tighten facial muscles, then relax deeply"},
        {"title": "Chest & Stomach", "emoji": "🫁", "order": 4, "instructions": "Take a deep breath, hold, then exhale slowly"},
        {"title": "Legs & Feet", "emoji": "🦶", "order": 5, "instructions": "Point toes downward, then relax your feet"},
        {"title": "Whole Body", "emoji": "🧘", "order": 6, "instructions": "Scan for any remaining tension and let it go"},
    ]

    BodyScanStep.objects.all().delete()
    for b in body_steps:
        BodyScanStep.objects.create(
            title=b["title"],
            emoji=b["emoji"],
            order=b["order"],
            instructions=b["instructions"]
        )

    # 4. Daily Affirmations
    affirmations = [
        {"category": "Confidence", "text": "I am capable of achieving everything I set my mind to."},
        {"category": "Confidence", "text": "I believe in my skills and abilities."},
        {"category": "Confidence", "text": "I am proud of how far I have come."},
        {"category": "Confidence", "text": "I trust my intuition and make wise decisions."},
        {"category": "Confidence", "text": "I am becoming the best version of myself."},
        
        {"category": "Peace", "text": "I am at peace with my past and excited for my future."},
        {"category": "Peace", "text": "I breathe in calmness and breathe out tension."},
        {"category": "Peace", "text": "My mind is calm, and my heart is at ease."},
        {"category": "Peace", "text": "I find joy in the present moment."},
        {"category": "Peace", "text": "I am surrounded by serenity and tranquility."},

        {"category": "Stress", "text": "I release all tension and embrace calm."},
        {"category": "Stress", "text": "I am in control of my stress levels."},
        {"category": "Stress", "text": "I take things one step at a time."},
        {"category": "Stress", "text": "I allow myself to rest and recharge."},
        {"category": "Stress", "text": "I am stronger than my stressors."},

        {"category": "Anxiety", "text": "I am safe, I am grounded, and I am in control."},
        {"category": "Anxiety", "text": "This feeling is temporary and will pass."},
        {"category": "Anxiety", "text": "I focus on my breath and stay present."},
        {"category": "Anxiety", "text": "I am safe in this moment."},
        {"category": "Anxiety", "text": "I trust the process of life."},

        {"category": "Love", "text": "I am worthy of love and respect from myself and others."},
        {"category": "Love", "text": "I choose to be kind to myself today."},
        {"category": "Love", "text": "I radiate love and positivity to those around me."},
        {"category": "Love", "text": "I am open to receiving love in all its forms."},
        {"category": "Love", "text": "I love and accept myself exactly as I am."},

        {"category": "Success", "text": "My potential is limitless, and I am growing every day."},
        {"category": "Success", "text": "I am attracting abundance and success."},
        {"category": "Success", "text": "I am resilient and can overcome any obstacle."},
        {"category": "Success", "text": "My hard work is paying off."},
        {"category": "Success", "text": "I am a magnet for opportunities and prosperity."},

        {"category": "Gratitude", "text": "I am grateful for the gift of this new day."},
        {"category": "Gratitude", "text": "I appreciate the simple joys in my life."},
        {"category": "Gratitude", "text": "I focus on what I have rather than what I lack."},
        {"category": "Gratitude", "text": "My life is full of blessings."},
        {"category": "Gratitude", "text": "I thank the universe for its infinite kindness."},
    ]

    Affirmation.objects.all().delete()
    for a in affirmations:
        Affirmation.objects.create(
            category=a["category"],
            text=a["text"],
            is_active=True
        )

    print(f"Successfully seeded {len(affirmations)} affirmations.")

if __name__ == "__main__":
    seed_all()
