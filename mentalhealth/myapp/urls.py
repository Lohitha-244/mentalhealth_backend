# myapp/urls.py

from django.urls import path
from .views import (
    # Auth / Profile
    AIInsightsAPIView,
    HomeSummaryView,
    MonthlyReportAPIView,
    MoodAnalyticsAPIView,
    MoodLastSummaryAPIView,
    MoodTipsAPIView,
    ProgressSummaryAPIView,
    RegisterView,
    SimpleLoginView,
    ProfileView,
    ForgotPasswordView,
    VerifyOTPView,
    ResetPasswordView,

    # Chat
    ChatbotSendView,
    ChatHistoryView,
    ChatSessionListView,

    # Mood
    MoodCheckInCreateAPIView,
    MoodCheckInHistoryAPIView,

    # Journal
    JournalEntryListCreateAPIView,
    JournalEntryDetailAPIView,

    # Gratitude
    GratitudeDashboardAPIView,
    GratitudeEntryListCreateAPIView,
    GratitudeEntryDetailAPIView,

    # Creative Drawing
    CreativeDrawingListCreateAPIView,
    CreativeDrawingDetailAPIView,

    # Daily Affirmations
    DailyAffirmationGetNextAPIView,
    DailyAffirmationToggleFavoriteAPIView,
    DailyAffirmationAddListenTimeAPIView,

    # MUSIC (✅ use the correct names from your views.py)
    MusicMoodsView,
    MusicTrackListAPIView,
    MusicDashboardAPIView,
    MusicTrackListenAPIView,

    # Nature Sounds
    NatureSoundListAPIView,
    NatureSoundPlayStartAPIView,
    NatureSoundPlayStopAPIView,
    NatureSoundStatsAPIView,

    # Body Scan
    BodyScanStepsAPIView,
    BodyScanDashboardAPIView,
    BodyScanStartSessionAPIView,
    BodyScanActionAPIView,
    BodyScanSessionLogsAPIView,
    BodyScanResetSessionAPIView,
    WeeklyReportAPIView,

    # Meditation
    MeditationProgramListAPIView,
    MeditationProgramDetailAPIView,
    MeditationStartAPIView,
    MeditationStopAPIView,
    MeditationDashboardAPIView,

    # settings & feedback
    SettingsAPIView, 
    PrivacyExportAPIView, 
    DeleteAccountAPIView,
    FeedbackAPIView,
    ProfileSummaryAPIView,

    # progress & reports
    MoodLastSummaryAPIView,
    MoodTipsAPIView,
    MoodAnalyticsAPIView,
    AIInsightsAPIView,

)

urlpatterns = [
    # =========================
    # AUTH / PROFILE
    # =========================
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", SimpleLoginView.as_view(), name="login"),
    path("auth/profile/", ProfileView.as_view(), name="auth-profile"),

    path("profile/", ProfileView.as_view(), name="profile"),

    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("forgot-password/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    path("home/summary/", HomeSummaryView.as_view(), name="home-summary"),

    # =========================
    # CHAT
    # =========================
    path("chat/send/", ChatbotSendView.as_view(), name="chat-send"),
    path("chat/history/", ChatHistoryView.as_view(), name="chat-history"),
    path("chat/sessions/", ChatSessionListView.as_view(), name="chat-sessions"),

    # =========================
    # MOOD
    # =========================
    path("mood/checkin/", MoodCheckInCreateAPIView.as_view(), name="mood-checkin"),
    path("mood/history/", MoodCheckInHistoryAPIView.as_view(), name="mood-history"),

    # =========================
    # JOURNAL
    # =========================
    path("journal/entries/", JournalEntryListCreateAPIView.as_view(), name="journal-entries"),
    path("journal/entries/<int:pk>/", JournalEntryDetailAPIView.as_view(), name="journal-entry-detail"),

    # =========================
    # GRATITUDE
    # =========================
    path("gratitude/dashboard/", GratitudeDashboardAPIView.as_view(), name="gratitude-dashboard"),
    path("gratitude/entries/", GratitudeEntryListCreateAPIView.as_view(), name="gratitude-entries"),
    path("gratitude/entries/<int:pk>/", GratitudeEntryDetailAPIView.as_view(), name="gratitude-entry-detail"),

    # =========================
    # CREATIVE DRAWING
    # =========================
    path("creative/entries/", CreativeDrawingListCreateAPIView.as_view(), name="creative-entries"),
    path("creative/entries/<int:pk>/", CreativeDrawingDetailAPIView.as_view(), name="creative-entry-detail"),

    # =========================
    # AFFIRMATIONS
    # =========================
    path("affirmations/next/", DailyAffirmationGetNextAPIView.as_view(), name="affirmations-next"),
    path("affirmations/<int:pk>/favorite/", DailyAffirmationToggleFavoriteAPIView.as_view(), name="affirmations-favorite"),
    path("affirmations/<int:pk>/listen/", DailyAffirmationAddListenTimeAPIView.as_view(), name="affirmations-listen"),

    # =========================
    # MUSIC
    # =========================
    path("music/moods/", MusicMoodsView.as_view(), name="music-moods"),
    path("music/tracks/", MusicTrackListAPIView.as_view(), name="music-tracks"),
    path("music/dashboard/", MusicDashboardAPIView.as_view(), name="music-dashboard"),
    path("music/tracks/<int:pk>/listen/", MusicTrackListenAPIView.as_view(), name="music-track-listen"),

    # =========================
    # NATURE SOUNDS
    # =========================
    path("sounds/nature/", NatureSoundListAPIView.as_view(), name="sounds-nature"),
    path("sounds/play/start/", NatureSoundPlayStartAPIView.as_view(), name="sounds-play-start"),
    path("sounds/play/stop/", NatureSoundPlayStopAPIView.as_view(), name="sounds-play-stop"),
    path("sounds/stats/", NatureSoundStatsAPIView.as_view(), name="sounds-stats"),

    # =========================
    # BODY SCAN
    # =========================
    path("body-scan/steps/", BodyScanStepsAPIView.as_view(), name="body-scan-steps"),
    path("body-scan/dashboard/", BodyScanDashboardAPIView.as_view(), name="body-scan-dashboard"),
    path("body-scan/sessions/start/", BodyScanStartSessionAPIView.as_view(), name="body-scan-start"),
    path("body-scan/sessions/<int:session_id>/action/", BodyScanActionAPIView.as_view(), name="body-scan-action"),
    path("body-scan/sessions/<int:session_id>/logs/", BodyScanSessionLogsAPIView.as_view(), name="body-scan-logs"),
    path("body-scan/sessions/<int:session_id>/reset/", BodyScanResetSessionAPIView.as_view(), name="body-scan-reset"),

    # =========================
    # PROGRESS & REPORTS
    # =========================

    path("progress/summary/", ProgressSummaryAPIView.as_view()),
    path("progress/weekly/", WeeklyReportAPIView.as_view()),
    path("progress/monthly/", MonthlyReportAPIView.as_view()),

    # =========================
    # SETTINGS & FEEDBACK
    # =========================

    path("profile/summary/", ProfileSummaryAPIView.as_view()),
    path("settings/", SettingsAPIView.as_view()),
    path("privacy/export/", PrivacyExportAPIView.as_view()),
    path("privacy/delete-account/", DeleteAccountAPIView.as_view()),
    path("feedback/", FeedbackAPIView.as_view()),



    # =========================
    # MEDITATION
    # =========================
    path("meditations/", MeditationProgramListAPIView.as_view(), name="meditations"),
    path("meditations/<int:pk>/", MeditationProgramDetailAPIView.as_view(), name="meditation-detail"),
    path("meditations/start/", MeditationStartAPIView.as_view(), name="meditation-start"),
    path("meditations/stop/", MeditationStopAPIView.as_view(), name="meditation-stop"),
    path("meditations/dashboard/", MeditationDashboardAPIView.as_view(), name="meditation-dashboard"),

    # Mood extra
    path("mood/last-summary/", MoodLastSummaryAPIView.as_view()),
    path("mood/tips/", MoodTipsAPIView.as_view()),
    path("mood/analytics/", MoodAnalyticsAPIView.as_view()),

    # AI Insights / Recommendations
    path("ai/insights/", AIInsightsAPIView.as_view()),
]