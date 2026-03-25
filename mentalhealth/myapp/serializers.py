# myapp/serializers.py
import base64
import uuid
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import serializers
from .models import AppSettings, Feedback
from .validators import validate_password_strength
from rest_framework import serializers
from .models import MeditationProgram, MeditationSession
from .models import (
    UserProfile,
    UserStats,
    ChatSession,
    ChatMessage,
    MoodCheckIn,
    MoodAnswer,
    JournalEntry,
    GratitudeEntry,
    GratitudePrompt,
    CreativeDrawing,
    Affirmation,
    UserAffirmationState,
    MusicTrack,
    SoundPlay,
    BodyScanStep,
    BodyScanSession,
    BodyScanStepLog,
    MeditationProgram, 
    MeditationSession,
    UserAffirmationState,
)

User = get_user_model()


# =========================
# REGISTER
# =========================
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if "@" in value:
            raise serializers.ValidationError("Username should not be an email address.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_password(self, value):
        return validate_password_strength(value)

    def create(self, validated_data):
        # We store the password as plain text here as requested
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"] 
        )
        user.save()
        return user


# =========================
# PROFILE
# =========================
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", required=False)
    first_name = serializers.CharField(source="user.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ["username", "email", "first_name", "last_name", "phone", "age", "gender", "profile_picture", "streak_days", "level", "coins", "days_active", "wellness_score"]
    
    streak_days = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    coins = serializers.SerializerMethodField()
    days_active = serializers.SerializerMethodField()
    wellness_score = serializers.SerializerMethodField()

    def _get_stats_obj(self, obj):
        # obj is UserProfile
        stats, _ = UserStats.objects.get_or_create(user=obj.user)
        return stats

    def get_streak_days(self, obj):
        return self._get_stats_obj(obj).streak_days
    
    def get_level(self, obj):
        return self._get_stats_obj(obj).level
    
    def get_coins(self, obj):
        return self._get_stats_obj(obj).coins

    def get_days_active(self, obj):
        user = obj.user
        mood_days = {timezone.localtime(o.created_at).date() for o in MoodCheckIn.objects.filter(user=user)}
        journal_days = {timezone.localtime(o.created_at).date() for o in JournalEntry.objects.filter(user=user)}
        sound_days = {timezone.localtime(o.started_at).date() for o in SoundPlay.objects.filter(user=user)}
        bodyscan_days = {timezone.localtime(o.started_at).date() for o in BodyScanSession.objects.filter(user=user, is_completed=True)}
        meditation_days = {timezone.localtime(o.started_at).date() for o in MeditationSession.objects.filter(user=user, is_completed=True)}
        gratitude_days = {timezone.localtime(o.created_at).date() for o in GratitudeEntry.objects.filter(user=user)}
        drawing_days = {timezone.localtime(o.created_at).date() for o in CreativeDrawing.objects.filter(user=user)}
        chat_days = {timezone.localtime(o.created_at).date() for o in ChatSession.objects.filter(user=user)}
        affirmation_days = {timezone.localtime(o.last_viewed_at).date() for o in UserAffirmationState.objects.filter(user=user)}

        all_active_days = (mood_days | journal_days | sound_days | bodyscan_days | 
                          meditation_days | gratitude_days | drawing_days | chat_days | affirmation_days)
        return len(all_active_days)

    def get_wellness_score(self, obj):
        user = obj.user
        stats = self._get_stats_obj(obj)
        
        # We need activity types for score
        has_mood = MoodCheckIn.objects.filter(user=user).exists()
        has_journal = JournalEntry.objects.filter(user=user).exists()
        has_sound = SoundPlay.objects.filter(user=user).exists()
        has_bodyscan = BodyScanSession.objects.filter(user=user, is_completed=True).exists()
        has_gratitude = GratitudeEntry.objects.filter(user=user).exists()
        
        streak_score = min(50, (stats.streak_days or 0) * 2)
        activity_types = sum([has_mood, has_journal, has_sound, has_bodyscan, has_gratitude])
        activity_score = min(50, activity_types * 10)
        return streak_score + activity_score

    def update(self, instance, validated_data):
        # Extract user data
        user_data = validated_data.pop('user', {})
        email = user_data.get('email')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')

        # Update User model if needed
        user = instance.user
        updated_user = False
        if email is not None:
            user.email = email
            updated_user = True
        if first_name is not None:
            user.first_name = first_name
            updated_user = True
        if last_name is not None:
            user.last_name = last_name
            updated_user = True
            
        if updated_user:
            user.save()

        # Update remaining UserProfile fields
        return super().update(instance, validated_data)


# =========================
# FORGOT PASSWORD / OTP / RESET
# =========================
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        return validate_password_strength(value)


# =========================
# HOME SUMMARY
# =========================
class HomeSummarySerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    daily_quote = serializers.SerializerMethodField()

    class Meta:
        model = UserStats
        fields = [
            "date",
            "level",
            "streak_days",
            "coins",
            "xp_current",
            "xp_target",
            "daily_quote",
        ]

    def get_date(self, obj):
        return timezone.localdate().isoformat()

    def get_daily_quote(self, obj):
        return obj.daily_quote.text if obj.daily_quote else "Stay strong. You’re doing great."


# =========================
# CHAT
# =========================
class ChatSendSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.IntegerField(required=False)


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ["id", "title", "created_at", "messages"]


# =========================
# MOOD (FRONTEND QUESTIONS ONLY)
# =========================
class MoodAnswerInputSerializer(serializers.Serializer):
    question_no = serializers.IntegerField(min_value=1)
    question_text = serializers.CharField(required=False, allow_blank=True, default="")
    selected_option = serializers.CharField(required=False, allow_blank=True, default="")
    answer_text = serializers.CharField(required=False, allow_blank=True, default="")


class MoodCheckInCreateSerializer(serializers.Serializer):
    mood = serializers.CharField()
    stress_level = serializers.IntegerField(min_value=0, max_value=10)
    answers = MoodAnswerInputSerializer(many=True)


class MoodAnswerReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodAnswer
        fields = [
            "question_no",
            "question_text",
            "selected_option_text",
            "answer_text",
            "created_at",
        ]


class MoodCheckInReadSerializer(serializers.ModelSerializer):
    answers = MoodAnswerReadSerializer(many=True, read_only=True)

    class Meta:
        model = MoodCheckIn
        fields = ["id", "mood", "stress_level", "created_at", "answers"]


# =========================
# JOURNAL
# =========================
class JournalEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ["text"]

    def validate_text(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Journal text cannot be empty.")
        return value


class JournalEntryReadSerializer(serializers.ModelSerializer):
    date_label = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = ["id", "text", "created_at", "date_label"]

    def get_date_label(self, obj):
        return timezone.localtime(obj.created_at).strftime("%A, %B %d, %Y")


# =========================
# GRATITUDE
# =========================
class GratitudeEntryCreateSerializer(serializers.Serializer):
    category = serializers.CharField()
    text = serializers.CharField()

    def validate_category(self, value):
        v = value.lower().strip()
        allowed = {"people", "moments", "things", "self", "nature", "opportunities"}
        if v not in allowed:
            raise serializers.ValidationError("Invalid category")
        return v

    def validate_text(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Text cannot be empty")
        return v


class GratitudeEntryReadSerializer(serializers.ModelSerializer):
    date_label = serializers.SerializerMethodField()

    class Meta:
        model = GratitudeEntry
        fields = ["id", "category", "text", "created_at", "date_label"]

    def get_date_label(self, obj):
        dt = timezone.localtime(obj.created_at)
        return dt.strftime("%b %d, %Y • %I:%M %p")


class GratitudeDashboardSerializer(serializers.Serializer):
    today_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    streak_days = serializers.IntegerField()
    prompt = serializers.CharField()


class GratitudePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = GratitudePrompt
        fields = ["id", "text"]


# =========================
# CREATIVE DRAWING (BASE64 SUPPORT)
# =========================
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if "base64," in data:
                data = data.split("base64,")[1]

            try:
                decoded = base64.b64decode(data)
            except Exception:
                raise serializers.ValidationError("Invalid base64 image")

            file_name = str(uuid.uuid4())[:12]
            return ContentFile(decoded, name=f"{file_name}.png")

        return super().to_internal_value(data)


class CreativeDrawingCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = CreativeDrawing
        fields = ["id", "prompt_text", "image", "strokes", "duration_seconds", "brush_size", "color_hex"]


class CreativeDrawingReadSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CreativeDrawing
        fields = ["id", "prompt_text", "image_url", "strokes", "duration_seconds", "brush_size", "color_hex", "created_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return ""
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


# =========================
# AFFIRMATIONS
# =========================
class AffirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affirmation
        fields = ["id", "category", "text"]


class UserAffirmationStateSerializer(serializers.ModelSerializer):
    affirmation = AffirmationSerializer()

    class Meta:
        model = UserAffirmationState
        fields = ["affirmation", "is_favorite", "view_count", "listened_seconds"]


# =========================
# NATURE SOUNDS / MUSIC
# =========================
class NatureSoundSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = MusicTrack
        fields = ["id", "title", "icon", "audio_url", "duration_seconds"]

    def get_audio_url(self, obj):
        request = self.context.get("request")

        if obj.audio_url:
            return obj.audio_url

        if obj.audio:
            try:
                return request.build_absolute_uri(obj.audio.url) if request else obj.audio.url
            except Exception:
                return obj.audio.url

        return ""


class MusicTrackSerializer(serializers.ModelSerializer):
    """
    For uploaded audio (optional) OR online url.
    - If audio_url exists, return it.
    - Else, return uploaded file url.
    """
    audio_play_url = serializers.SerializerMethodField()
    duration_label = serializers.SerializerMethodField()

    class Meta:
        model = MusicTrack
        fields = [
            "id",
            "category",
            "mood",
            "title",
            "icon",
            "description",
            "duration_seconds",
            "duration_label",
            "audio_play_url",
        ]

    def get_audio_play_url(self, obj):
        request = self.context.get("request")
        if obj.audio_url:
            return obj.audio_url
        if obj.audio:
            return request.build_absolute_uri(obj.audio.url) if request else obj.audio.url
        return ""

    def get_duration_label(self, obj):
        m = obj.duration_seconds // 60
        s = obj.duration_seconds % 60
        return f"{m}:{s:02d}"


class SoundPlayStartSerializer(serializers.Serializer):
    track_id = serializers.IntegerField()


class SoundPlayStopSerializer(serializers.Serializer):
    play_id = serializers.IntegerField()
    duration_sec = serializers.IntegerField(min_value=0)


class SoundPlayReadSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source="track.title", read_only=True)

    class Meta:
        model = SoundPlay
        fields = ["id", "track", "track_title", "started_at", "ended_at", "duration_seconds"]


# =========================
# BODY SCAN
# =========================
class BodyScanStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyScanStep
        fields = [
            "id",
            "title",
            "emoji",
            "instructions",
            "position_tip",
            "order",
            "tense_seconds",
            "hold_seconds",
            "release_seconds",
            "rest_seconds",
        ]


class BodyScanSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyScanSession
        fields = [
            "id",
            "started_at",
            "ended_at",
            "total_seconds",
            "steps_total",
            "steps_completed",
            "is_completed",
        ]


class BodyScanLogSerializer(serializers.ModelSerializer):
    step_title = serializers.CharField(source="step.title", read_only=True)

    class Meta:
        model = BodyScanStepLog
        fields = ["id", "step", "step_title", "phase", "seconds", "created_at"]


class AppSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSettings
        fields = [
            "auto_speak_ai",
            "voice_input_enabled",
            "high_contrast",
            "dyslexia_friendly_font",
            "icon_only_navigation",
            "font_size",
            "app_language",
            "dark_mode",
        ]
class FeedbackCreateSerializer(serializers.Serializer):
    message = serializers.CharField()
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)

    def validate_message(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("Message cannot be empty.")
        return v
    
class MoodLastSummarySerializer(serializers.Serializer):
    mood = serializers.CharField()
    stress_level = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    suggestion_title = serializers.CharField()
    suggestion_text = serializers.CharField()


class MoodTipSerializer(serializers.Serializer):
    title = serializers.CharField()
    duration_min = serializers.IntegerField()
    steps = serializers.ListField(child=serializers.CharField())


class MoodAnalyticsSerializer(serializers.Serializer):
    total_checkins = serializers.IntegerField()
    this_period_checkins = serializers.IntegerField()
    most_common_mood = serializers.DictField()
    avg_stress = serializers.FloatField()
    trend = serializers.CharField()
    insights = serializers.ListField(child=serializers.CharField())
    distribution = serializers.ListField(child=serializers.DictField())


class AIInsightsSerializer(serializers.Serializer):
    has_enough_data = serializers.BooleanField()
    data_points = serializers.IntegerField()
    insights_count = serializers.IntegerField()
    patterns_count = serializers.IntegerField()
    insights = serializers.ListField(child=serializers.CharField())
    patterns = serializers.ListField(child=serializers.CharField())

class MeditationProgramSerializer(serializers.ModelSerializer):
    audio_play_url = serializers.SerializerMethodField()
    duration_label = serializers.SerializerMethodField()

    class Meta:
        model = MeditationProgram
        fields = [
            "id",
            "title",
            "category",
            "description",
            "duration_seconds",
            "duration_label",
            "audio_play_url",
        ]

    def get_audio_play_url(self, obj):
        request = self.context.get("request")
        if obj.audio_url:
            return obj.audio_url
        if obj.audio:
            return request.build_absolute_uri(obj.audio.url) if request else obj.audio.url
        return ""

    def get_duration_label(self, obj):
        m = obj.duration_seconds // 60
        s = obj.duration_seconds % 60
        return f"{m}:{s:02d}"


class MeditationStartSerializer(serializers.Serializer):
    program_id = serializers.IntegerField()


class MeditationStopSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    duration_sec = serializers.IntegerField(min_value=0)


class MeditationProgramSerializer(serializers.ModelSerializer):
    audio_play_url = serializers.SerializerMethodField()
    duration_label = serializers.SerializerMethodField()

    class Meta:
        model = MeditationProgram
        fields = [
            "id",
            "category",
            "title",
            "description",
            "duration_seconds",
            "duration_label",
            "audio_url",
            "audio",
            "audio_play_url",
            "is_active",
        ]

    def get_audio_play_url(self, obj):
        request = self.context.get("request")
        if getattr(obj, "audio_url", None):
            return obj.audio_url
        if getattr(obj, "audio", None):
            return request.build_absolute_uri(obj.audio.url) if request else obj.audio.url
        return ""

    def get_duration_label(self, obj):
        s = int(obj.duration_seconds or 0)
        return f"{s//60}:{s%60:02d}"


class MeditationSessionSerializer(serializers.ModelSerializer):
    program_title = serializers.CharField(source="program.title", read_only=True)

    class Meta:
        model = MeditationSession
        fields = [
            "id",
            "program",
            "program_title",
            "started_at",
            "ended_at",
            "duration_seconds",
        ]