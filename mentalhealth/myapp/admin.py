from django.contrib import admin
from .models import MeditationProgram, MeditationSession
from .models import (
    UserProfile,
    PasswordResetOTP,
    DailyMotivationQuote,
    UserStats,
    ChatSession,
    ChatMessage,
    MoodCheckIn,
    MoodAnswer,
    MusicTrack,
    UserMusicStats,
    SoundPlay,
)

# Basic registrations
admin.site.register(UserProfile)
admin.site.register(PasswordResetOTP)
admin.site.register(DailyMotivationQuote)
admin.site.register(UserStats)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
admin.site.register(MoodCheckIn)
admin.site.register(MoodAnswer)


@admin.register(MusicTrack)
class MusicTrackAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "mood", "title", "duration_seconds", "is_active")
    list_filter = ("category", "mood", "is_active")
    search_fields = ("title", "description", "icon")


@admin.register(UserMusicStats)
class UserMusicStatsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listening_seconds_total")
    search_fields = ("user__username", "user__email")


@admin.register(SoundPlay)
class SoundPlayAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "track", "duration_seconds", "started_at", "ended_at")
    list_filter = ("track__category", "track__mood")
    search_fields = ("user__username", "track__title")


@admin.register(MeditationProgram)
class MeditationProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "title", "duration_seconds", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title",)

@admin.register(MeditationSession)
class MeditationSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "program", "duration_seconds", "is_completed", "started_at")
    list_filter = ("is_completed", "program__category")