# myapp/models.py
from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

USER_MODEL = settings.AUTH_USER_MODEL


# -------------------- USER PROFILE / OTP / STATS / CHAT --------------------

class UserProfile(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    def __str__(self):
        return getattr(self.user, "username", str(self.user))


class PasswordResetOTP(models.Model):
    email = models.EmailField(db_index=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    is_verified = models.BooleanField(default=False)
    reset_token = models.UUIDField(null=True, blank=True)
    reset_token_created_at = models.DateTimeField(null=True, blank=True)

    def otp_is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def token_is_expired(self) -> bool:
        if not self.reset_token_created_at:
            return True
        return timezone.now() > self.reset_token_created_at + timedelta(minutes=10)

    def issue_reset_token(self):
        self.reset_token = uuid.uuid4()
        self.reset_token_created_at = timezone.now()
        self.save(update_fields=["reset_token", "reset_token_created_at", "is_verified"])
        return self.reset_token


class DailyMotivationQuote(models.Model):
    text = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text[:50]


class UserStats(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name="stats")

    level = models.PositiveIntegerField(default=1)
    coins = models.PositiveIntegerField(default=0)

    xp_current = models.PositiveIntegerField(default=0)
    xp_target = models.PositiveIntegerField(default=100)

    streak_days = models.PositiveIntegerField(default=0)
    last_streak_date = models.DateField(null=True, blank=True)

    daily_quote = models.ForeignKey(
        DailyMotivationQuote, null=True, blank=True, on_delete=models.SET_NULL
    )
    daily_quote_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{getattr(self.user, 'username', self.user)} stats"


class ChatSession(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=120, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{getattr(self.user, 'username', self.user)} - {self.created_at}"


class ChatMessage(models.Model):
    ROLE_CHOICES = (("user", "user"), ("assistant", "assistant"))
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# -------------------- MOOD FLOW --------------------

class Mood(models.TextChoices):
    GREAT = "great", "Great"
    ANGRY = "angry", "Angry"
    TIRED = "tired", "Tired"
    STRESSED = "stressed", "Stressed"
    SAD = "sad", "Sad"


class MoodSession(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    mood = models.CharField(max_length=20, choices=Mood.choices)
    stress_level = models.PositiveSmallIntegerField(default=0)  # 0..10
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} {self.mood} {self.created_at}"


class MoodQuestion(models.Model):
    mood = models.CharField(max_length=20, choices=Mood.choices)
    order = models.PositiveSmallIntegerField()  # 1,2,3...
    text = models.CharField(max_length=255)

    class Meta:
        unique_together = ("mood", "order")
        ordering = ["mood", "order"]

    def __str__(self):
        return f"{self.mood} Q{self.order}: {self.text}"


class MoodOption(models.Model):
    question = models.ForeignKey(MoodQuestion, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=120)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.text


class MoodCheckIn(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="mood_checkins")
    mood = models.CharField(max_length=20, choices=Mood.choices)
    stress_level = models.PositiveSmallIntegerField(default=0)  # 0..10
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.mood} {self.created_at}"


class MoodAnswer(models.Model):
    checkin = models.ForeignKey(MoodCheckIn, on_delete=models.CASCADE, related_name="answers")

    question_no = models.PositiveSmallIntegerField()  # 1,2,3...
    question_text = models.CharField(max_length=255, blank=True, default="")
    selected_option_text = models.CharField(max_length=200, blank=True, default="")
    answer_text = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("checkin", "question_no")
        ordering = ["question_no"]

    def __str__(self):
        return f"{self.checkin_id} - Q{self.question_no}"


# -------------------- JOURNAL --------------------

class JournalEntry(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.created_at}"


# -------------------- GRATITUDE --------------------

class GratitudeCategory(models.TextChoices):
    PEOPLE = "people", "People"
    MOMENTS = "moments", "Moments"
    THINGS = "things", "Things"
    SELF = "self", "Self"
    NATURE = "nature", "Nature"
    OPPORTUNITIES = "opportunities", "Opportunities"


class GratitudePrompt(models.Model):
    text = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text


class GratitudeEntry(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="gratitude_entries")
    category = models.CharField(max_length=20, choices=GratitudeCategory.choices)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def created_date(self):
        return timezone.localtime(self.created_at).date()

    def __str__(self):
        return f"{self.user} - {self.category} - {self.created_at}"


# -------------------- CREATIVE DRAWING --------------------

class CreativeDrawing(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="creative_drawings")

    prompt_text = models.CharField(max_length=255, blank=True, default="")
    image = models.ImageField(upload_to="creative_drawings/")

    strokes = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    brush_size = models.PositiveIntegerField(default=8)
    color_hex = models.CharField(max_length=20, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} drawing {self.id}"


# -------------------- AFFIRMATIONS --------------------

class Affirmation(models.Model):
    category = models.CharField(max_length=50, default="General")
    text = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category}: {self.text[:30]}"


class UserAffirmationState(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    affirmation = models.ForeignKey(Affirmation, on_delete=models.CASCADE)

    is_favorite = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    listened_seconds = models.PositiveIntegerField(default=0)

    last_viewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "affirmation")

    def __str__(self):
        return f"{self.user} - {self.affirmation_id}"


# -------------------- MUSIC / NATURE SOUNDS --------------------

class MusicTrack(models.Model):
    CATEGORY_CHOICES = [
        ("nature", "Nature Sounds"),
        ("music", "Music"),
    ]

    MOODS = [
        ("", "None"),
        ("calm", "Calm"),
        ("happy", "Happy"),
        ("focus", "Focus"),
        ("energize", "Energize"),
        ("sleep", "Sleep"),
        ("meditative", "Meditative"),
        ("peace", "Peace"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="nature")
    mood = models.CharField(max_length=20, choices=MOODS, blank=True, default="")

    title = models.CharField(max_length=120)
    icon = models.CharField(max_length=50, blank=True, default="")
    description = models.CharField(max_length=255, blank=True, default="")

    audio_url = models.URLField(blank=True, null=True)
    audio = models.FileField(upload_to="music/", blank=True, null=True)

    duration_seconds = models.PositiveIntegerField(default=180)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}: {self.title}"


class UserMusicStats(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name="music_stats")
    listening_seconds_total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{getattr(self.user, 'username', self.user)} - {self.listening_seconds_total}s"


class SoundPlay(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="sound_plays")
    track = models.ForeignKey(MusicTrack, on_delete=models.CASCADE, related_name="plays")

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} - {self.track.title}"


# -------------------- BODY SCAN --------------------

class BodyScanStep(models.Model):
    title = models.CharField(max_length=120)
    emoji = models.CharField(max_length=10, blank=True, default="")
    instructions = models.TextField(blank=True, default="")
    position_tip = models.CharField(max_length=200, blank=True, default="")

    order = models.PositiveIntegerField(default=1)

    tense_seconds = models.PositiveIntegerField(default=5)
    hold_seconds = models.PositiveIntegerField(default=3)
    release_seconds = models.PositiveIntegerField(default=5)
    rest_seconds = models.PositiveIntegerField(default=3)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.title}"


class BodyScanSession(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="body_scan_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    total_seconds = models.PositiveIntegerField(default=0)
    steps_total = models.PositiveIntegerField(default=12)
    steps_completed = models.PositiveIntegerField(default=0)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{getattr(self.user, 'username', self.user)} - BodyScanSession #{self.id}"


class BodyScanStepLog(models.Model):
    PHASE_CHOICES = (
        ("TENSE", "TENSE"),
        ("HOLD", "HOLD"),
        ("RELEASE", "RELEASE"),
        ("REST", "REST"),
        ("SKIP", "SKIP"),
    )

    session = models.ForeignKey(BodyScanSession, on_delete=models.CASCADE, related_name="logs")
    step = models.ForeignKey(BodyScanStep, on_delete=models.CASCADE)

    phase = models.CharField(max_length=10, choices=PHASE_CHOICES)
    seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
 
       return f"{self.session_id} - {self.step_id} - {self.phase}"



# -------------------- SETTINGS / PRIVACY / FEEDBACK --------------------

class AppSettings(models.Model):
    FONT_SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
    ]

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("es", "Español"),
        ("fr", "Français"),
        ("de", "Deutsch"),
        ("te", "Telugu"),
        ("hi", "Hindi"),
        ("ta", "Tamil"),
    ]

    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name="app_settings")

    auto_speak_ai = models.BooleanField(default=False)
    voice_input_enabled = models.BooleanField(default=True)
    high_contrast = models.BooleanField(default=False)
    dyslexia_friendly_font = models.BooleanField(default=False)
    icon_only_navigation = models.BooleanField(default=False)

    font_size = models.CharField(max_length=2, choices=FONT_SIZE_CHOICES, default="M")
    app_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="en")

    dark_mode = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{getattr(self.user, 'username', self.user)} settings"


class Feedback(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks")
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1..5 optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} - {getattr(self.user, 'username', self.user)}"
    

# -------------------- MEDITATION / RELAX PROGRAMS --------------------

class MeditationProgram(models.Model):
    CATEGORY_CHOICES = [
        ("morning", "Morning Calm"),
        ("stress", "Stress Relief"),
        ("deep", "Deep Relaxation"),
        ("sleep", "Sleep Preparation"),
    ]

    title = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=255, blank=True, default="")
    duration_seconds = models.PositiveIntegerField(default=300)  # default 5 min
    audio_url = models.URLField(blank=True, null=True)  # optional (online)
    audio = models.FileField(upload_to="meditations/", blank=True, null=True)  # optional upload
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}: {self.title}"


class MeditationSession(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="meditation_sessions")
    program = models.ForeignKey(MeditationProgram, on_delete=models.CASCADE, related_name="sessions")

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} - {self.program.title} - {self.duration_seconds}s"