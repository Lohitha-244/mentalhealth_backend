import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .ai import generate_reply
from .validators import validate_password_strength
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Count
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import MeditationProgram, MeditationSession

from .models import AppSettings, Feedback, MoodCheckIn, JournalEntry, GratitudeEntry, SoundPlay, BodyScanSession, UserStats
from .serializers import AppSettingsSerializer, FeedbackCreateSerializer

from .models import MoodCheckIn, JournalEntry, SoundPlay, BodyScanSession, UserStats
from django.db.models import Count, Avg
from .models import MoodCheckIn, MoodAnswer

from .models import (
    UserProfile,
    PasswordResetOTP,
    UserStats,
    DailyMotivationQuote,
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
    UserMusicStats,
    SoundPlay,
    BodyScanStep,
    BodyScanSession,
    BodyScanStepLog,
   
)

from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    ChatSendSerializer,
    ChatSessionSerializer,
    MoodCheckInCreateSerializer,
    MoodCheckInReadSerializer,
    JournalEntryCreateSerializer,
    JournalEntryReadSerializer,
    GratitudeEntryCreateSerializer,
    GratitudeEntryReadSerializer,
    GratitudeDashboardSerializer,
    CreativeDrawingCreateSerializer,
    CreativeDrawingReadSerializer,
    AffirmationSerializer,
    MusicTrackSerializer,
    NatureSoundSerializer,
    SoundPlayReadSerializer,
    BodyScanStepSerializer,
    BodyScanSessionSerializer,
    BodyScanLogSerializer,
    MoodLastSummarySerializer,
    MoodTipSerializer,
    MoodAnalyticsSerializer,
    AIInsightsSerializer,
    MeditationProgramSerializer,
    MeditationStartSerializer,
    MeditationStopSerializer,
)

User = get_user_model()


# =========================
# HELPERS
# =========================
def award_user_xp(user, xp=10, coins=2):
    from .models import UserStats
    stats, _ = UserStats.objects.get_or_create(user=user)
    stats.coins += coins
    stats.xp_current += xp
    while stats.xp_current >= stats.xp_target:
        stats.xp_current -= stats.xp_target
        stats.level += 1
        stats.xp_target += 50
    stats.save()

def update_user_streak(user):
    from .models import UserStats
    from django.utils import timezone
    stats, _ = UserStats.objects.get_or_create(user=user)
    today = timezone.localdate()
    if stats.last_streak_date == today:
        return
    if stats.last_streak_date == today - timezone.timedelta(days=1):
        stats.streak_days += 1
    else:
        stats.streak_days = 1
    stats.last_streak_date = today
    stats.save()

# =========================
# REGISTER
# =========================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print(f"DEBUG: Signup attempt for: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            if "username" in errors:
                return Response({"message": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            if "email" in errors:
                return Response({"message": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Signup failed. Please check your details."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            UserProfile.objects.get_or_create(user=user)
            UserStats.objects.get_or_create(user=user)

            return Response({"message": "Account created successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"message": f"Server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimpleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        login_id = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "").strip()

        if not login_id or not password:
            return Response({"message": "Please provide credentials"}, status=400)

        from django.db.models import Q
        # Use iexact for both username and email for maximum compatibility
        user = User.objects.filter(
            Q(username__iexact=login_id) | Q(email__iexact=login_id)
        ).first()

        if user:
            # 1. Try plain text
            is_valid_plain = (user.password == password)
            
            # 2. Try hashed password
            is_valid_hashed = False
            if not is_valid_plain:
                from django.contrib.auth.hashers import check_password
                try:
                    is_valid_hashed = check_password(password, user.password)
                except Exception as e:
                    pass

            if is_valid_plain or is_valid_hashed:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                })
            
            return Response({"message": "Invalid password"}, status=401)
        else:
            return Response({"message": "User does not exist"}, status=401)


# =========================
# PROFILE
# =========================
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)
    

class HomeSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        from .models import UserStats, DailyMotivationQuote
        from django.utils import timezone
        
        # Get or create stats for user
        stats, _ = UserStats.objects.get_or_create(user=user)
        
        # Get daily motivation
        motivation = "You are stronger than you think."
        quote_obj = DailyMotivationQuote.objects.filter(is_active=True).order_by('?').first()
        if quote_obj:
            motivation = quote_obj.text
            
        return Response({
            "message": f"Welcome back, {getattr(user, 'username', 'User')}!",
            "date": timezone.now().strftime("%A, %B %d"),
            "level": stats.level,
            "streak": stats.streak_days,
            "coins": stats.coins,
            "xp_progress": stats.xp_current,
            "motivation": motivation
        })
# =========================
# FORGOT PASSWORD (SEND OTP)
# =========================
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import PasswordResetOTP
from .serializers import ForgotPasswordSerializer


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower().strip()

        if not User.objects.filter(email=email).exists():
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(100000, 999999))

        try:
            send_mail(
                subject="Your Password Reset OTP",
                message=f"Your OTP is {otp}. It expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            # We log the error but allow the flow to continue for development
            pass

        PasswordResetOTP.objects.create(email=email, otp=otp)
        return Response({"message": "OTP sent."}, status=status.HTTP_200_OK)
# VERIFY OTP (ISSUE reset_token)
# =========================
class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").lower().strip()
        otp = (request.data.get("otp") or "").strip()

        if not email or not otp:
            return Response({"error": "email and otp are required"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj = (
            PasswordResetOTP.objects.filter(email=email, otp=otp)
            .order_by("-created_at")
            .first()
        )
        if not otp_obj:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.otp_is_expired():
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.is_verified = True
        reset_token = otp_obj.issue_reset_token()

        return Response(
            {"message": "OTP verified successfully", "reset_token": str(reset_token)},
            status=status.HTTP_200_OK,
        )


# =========================
# RESET PASSWORD
# =========================
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").lower().strip()
        reset_token = (request.data.get("reset_token") or "").strip()
        new_password = (request.data.get("new_password") or "").strip()

        if not email or not reset_token or not new_password:
            return Response(
                {"error": "email, reset_token and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validate_password_strength(new_password)

        otp_obj = (
            PasswordResetOTP.objects.filter(email=email, reset_token=reset_token, is_verified=True)
            .order_by("-reset_token_created_at")
            .first()
        )

        if not otp_obj:
            return Response({"error": "Invalid reset token"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.token_is_expired():
            return Response({"error": "Reset token expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Use case-insensitive lookup for user email
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Store password as plain text (requested simplicity)
        user.password = new_password
        user.save()

        otp_obj.reset_token = None
        otp_obj.reset_token_created_at = None
        otp_obj.is_verified = False
        otp_obj.save(update_fields=["reset_token", "reset_token_created_at", "is_verified"])

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)


# =========================
# CHATBOT
# =========================
from .rag import retrieve_context
class ChatbotSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get("message")
        session_id = request.data.get("session_id")

        if not message:
            return Response({"error": "Message is required"}, status=400)

        user_message = message.strip()

        if session_id and session_id != 0:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({"error": "Session not found"}, status=404)
        else:
            title = message[:40] + "..." if len(message) > 40 else message
            session = ChatSession.objects.create(
                user=request.user,
                title=title
            )

        # save user message
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=user_message
        )

        # get last messages for history
        recent_msgs = ChatMessage.objects.filter(session=session).order_by("-created_at")[:12]
        recent_msgs = list(reversed(recent_msgs))

        history = [
            {"role": m.role, "content": m.content}
            for m in recent_msgs
            if m.role in ("user", "assistant")
        ]

        # RAG retrieval
        context = retrieve_context(user_message, k=4)

        # generate AI reply
        reply = generate_reply(
            user_message=user_message,
            history=history,
            context=context
        )

        # save AI reply
        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=reply
        )

        return Response({
            "reply": reply,
            "session_id": session.id
        }, status=200)

class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({"messages": []}, status=status.HTTP_200_OK)
        else:
            session = ChatSession.objects.filter(user=request.user).order_by("-created_at").first()
            
        if not session:
            return Response({"id": 0, "messages": []}, status=status.HTTP_200_OK)
        return Response(ChatSessionSerializer(session).data, status=status.HTTP_200_OK)

class ChatSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user).order_by("-created_at")
        data = [{"id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]
        return Response(data, status=200)


# =========================
# MOOD CHECK-IN
# =========================
class MoodCheckInCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # POST /api/mood/checkin/
    def post(self, request):
        serializer = MoodCheckInCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mood = serializer.validated_data["mood"].lower().strip()
        stress_level = serializer.validated_data["stress_level"]
        answers = serializer.validated_data["answers"]

        checkin = MoodCheckIn.objects.create(user=request.user, mood=mood, stress_level=stress_level)

        for a in answers:
            MoodAnswer.objects.create(
                checkin=checkin,
                question_no=a["question_no"],
                question_text=a.get("question_text", ""),
                selected_option_text=a.get("selected_option", ""),
                answer_text=a.get("answer_text", ""),
            )

        # Award rewards
        award_user_xp(request.user, xp=15, coins=5)
        update_user_streak(request.user)

        return Response(MoodCheckInReadSerializer(checkin).data, status=status.HTTP_201_CREATED)


class MoodCheckInHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/mood/history/
    def get(self, request):
        qs = MoodCheckIn.objects.filter(user=request.user).prefetch_related("answers").order_by("-created_at")[:50]
        return Response(MoodCheckInReadSerializer(qs, many=True).data, status=status.HTTP_200_OK)


# =========================
# JOURNAL
# =========================
class JournalEntryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JournalEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entry = JournalEntry.objects.create(user=request.user, text=serializer.validated_data["text"])
        
        # Award rewards
        award_user_xp(request.user, xp=10, coins=2)
        update_user_streak(request.user)
        
        return Response(JournalEntryReadSerializer(entry).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        qs = JournalEntry.objects.filter(user=request.user).order_by("-created_at")[:100]
        return Response(JournalEntryReadSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class JournalEntryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        entry = JournalEntry.objects.filter(user=request.user, pk=pk).first()
        if not entry:
            return Response({"error": "Journal entry not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(JournalEntryReadSerializer(entry).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        entry = JournalEntry.objects.filter(user=request.user, pk=pk).first()
        if not entry:
            return Response({"error": "Journal entry not found"}, status=status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response({"message": "Journal entry deleted successfully"}, status=status.HTTP_200_OK)


# =========================
# GRATITUDE
# =========================
def _calc_gratitude_streak(user):
    dates = GratitudeEntry.objects.filter(user=user).dates("created_at", "day", order="DESC")
    if not dates:
        return 0

    today = timezone.localdate()
    date_set = set(dates)

    streak = 0
    expected = today
    if expected not in date_set:
        expected = today - timezone.timedelta(days=1)

    while expected in date_set:
        streak += 1
        expected = expected - timezone.timedelta(days=1)

    return streak


class GratitudeDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()

        today_count = GratitudeEntry.objects.filter(user=request.user, created_at__date=today).count()
        total_count = GratitudeEntry.objects.filter(user=request.user).count()
        streak_days = _calc_gratitude_streak(request.user)

        prompt_obj = GratitudePrompt.objects.filter(is_active=True).order_by("?").first()
        prompt_text = prompt_obj.text if prompt_obj else "What do you appreciate about yourself?"

        return Response(
            {
                "today_count": today_count,
                "total_count": total_count,
                "streak_days": streak_days,
                "prompt": prompt_text,
            },
            status=status.HTTP_200_OK,
        )


class GratitudeEntryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GratitudeEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entry = GratitudeEntry.objects.create(
            user=request.user,
            category=serializer.validated_data["category"],
            text=serializer.validated_data["text"],
        )
        
        # Award rewards
        award_user_xp(request.user, xp=12, coins=3)
        update_user_streak(request.user)

        return Response(GratitudeEntryReadSerializer(entry).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        qs = GratitudeEntry.objects.filter(user=request.user).order_by("-created_at")[:200]
        return Response(GratitudeEntryReadSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class GratitudeEntryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        entry = GratitudeEntry.objects.filter(user=request.user, pk=pk).first()
        if not entry:
            return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response({"message": "Gratitude entry deleted successfully"}, status=status.HTTP_200_OK)


# =========================
# CREATIVE DRAWING
# =========================
# (removed award_xp_for_creative, now using award_user_xp)


class CreativeDrawingListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = CreativeDrawing.objects.filter(user=request.user).order_by("-created_at")[:100]
        data = CreativeDrawingReadSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreativeDrawingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        drawing = serializer.save(user=request.user)
        award_user_xp(request.user, xp=15, coins=5)
        update_user_streak(request.user)

        return Response(
            CreativeDrawingReadSerializer(drawing, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CreativeDrawingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        obj = get_object_or_404(CreativeDrawing, pk=pk, user=request.user)
        return Response(CreativeDrawingReadSerializer(obj, context={"request": request}).data)

    def delete(self, request, pk):
        obj = get_object_or_404(CreativeDrawing, pk=pk, user=request.user)
        obj.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)


# =========================
# AFFIRMATIONS
# =========================
class DailyAffirmationGetNextAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Affirmation.objects.filter(is_active=True)
        if not qs.exists():
            return Response({"detail": "No affirmations found."}, status=status.HTTP_404_NOT_FOUND)

        affirmation = random.choice(list(qs))

        state, _ = UserAffirmationState.objects.get_or_create(user=request.user, affirmation=affirmation)
        state.view_count += 1
        state.last_viewed_at = timezone.now()
        state.save()

        viewed_total = UserAffirmationState.objects.filter(user=request.user).aggregate(total=Sum("view_count"))["total"] or 0
        favorites_total = UserAffirmationState.objects.filter(user=request.user, is_favorite=True).count()
        time_total = UserAffirmationState.objects.filter(user=request.user).aggregate(total=Sum("listened_seconds"))["total"] or 0

        return Response(
            {
                "affirmation": AffirmationSerializer(affirmation).data,
                "is_favorite": state.is_favorite,
                "stats": {"viewed": viewed_total, "favorites": favorites_total, "time_seconds": time_total},
            },
            status=status.HTTP_200_OK,
        )


class DailyAffirmationToggleFavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        affirmation = Affirmation.objects.filter(pk=pk, is_active=True).first()
        if not affirmation:
            return Response({"detail": "Affirmation not found."}, status=status.HTTP_404_NOT_FOUND)

        state, _ = UserAffirmationState.objects.get_or_create(user=request.user, affirmation=affirmation)
        state.is_favorite = not state.is_favorite
        state.save()

        favorites_total = UserAffirmationState.objects.filter(user=request.user, is_favorite=True).count()

        return Response(
            {"affirmation_id": affirmation.id, "is_favorite": state.is_favorite, "favorites_total": favorites_total},
            status=status.HTTP_200_OK,
        )


class DailyAffirmationAddListenTimeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        seconds = int(request.data.get("seconds", 0))
        if seconds < 0:
            seconds = 0

        affirmation = Affirmation.objects.filter(pk=pk, is_active=True).first()
        if not affirmation:
            return Response({"detail": "Affirmation not found."}, status=status.HTTP_404_NOT_FOUND)

        state, _ = UserAffirmationState.objects.get_or_create(user=request.user, affirmation=affirmation)
        state.listened_seconds += seconds
        state.save()

        # Award rewards (small bonus for affirmation)
        award_user_xp(request.user, xp=2, coins=1)
        update_user_streak(request.user)

        time_total = UserAffirmationState.objects.filter(user=request.user).aggregate(total=Sum("listened_seconds"))["total"] or 0

        return Response(
            {"affirmation_id": affirmation.id, "added_seconds": seconds, "time_seconds_total": time_total},
            status=status.HTTP_200_OK,
        )

# =========================
# MUSIC + DASHBOARD + LISTEN (CLEAN)
# =========================

def seconds_to_label(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"


class MusicMoodsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Use model choices so it always matches DB
        return Response(
            [{"key": key, "label": label} for key, label in MusicTrack.MOODS if key],
            status=status.HTTP_200_OK,
        )


class MusicDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ FIX: Count ALL tracks, not only category="music"
        total_tracks = MusicTrack.objects.filter(is_active=True).count()

        stats, _ = UserMusicStats.objects.get_or_create(user=request.user)

        return Response(
            {
                "tracks_total": total_tracks,
                "listening_seconds_total": stats.listening_seconds_total,
                "listening_label": seconds_to_label(stats.listening_seconds_total),
            },
            status=status.HTTP_200_OK,
        )


class MusicTrackListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mood = request.GET.get("mood")
        category = request.GET.get("category")  # optional: music/nature

        qs = MusicTrack.objects.filter(is_active=True).order_by("id")

        if category:
            qs = qs.filter(category=category)

        if mood:
            qs = qs.filter(mood__iexact=mood)

        return Response(
            MusicTrackSerializer(qs, many=True, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class MusicTrackListenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        track = MusicTrack.objects.filter(pk=pk, is_active=True).first()
        if not track:
            return Response({"detail": "Track not found"}, status=status.HTTP_404_NOT_FOUND)

        # accept both "seconds" and "duration_seconds"
        seconds = request.data.get("seconds", None)
        if seconds is None:
            seconds = request.data.get("duration_seconds", None)

        try:
            seconds = int(seconds) if seconds is not None else int(track.duration_seconds)
        except Exception:
            seconds = int(track.duration_seconds)

        if seconds < 0:
            seconds = 0

        # Save play record (optional but useful)
        now = timezone.now()
        SoundPlay.objects.create(
            user=request.user,
            track=track,
            started_at=now,
            ended_at=now,
            duration_seconds=seconds,
        )

        # Update total stats
        stats, _ = UserMusicStats.objects.get_or_create(user=request.user)
        stats.listening_seconds_total += seconds
        stats.save(update_fields=["listening_seconds_total"])

        # Award rewards
        award_user_xp(request.user, xp=5, coins=1)
        update_user_streak(request.user)

        return Response(
            {
                "track_id": track.id,
                "added_seconds": seconds,
                "listening_seconds_total": stats.listening_seconds_total,
                "listening_label": seconds_to_label(stats.listening_seconds_total),
            },
            status=status.HTTP_200_OK,
        )

# =========================
# ✅ NATURE SOUNDS (your next screen)
# =========================
class NatureSoundListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/sounds/nature/
    def get(self, request):
        qs = MusicTrack.objects.filter(category="nature", is_active=True).order_by("id")
        return Response(NatureSoundSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class NatureSoundPlayStartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # POST /api/sounds/play/start/  body: {"track_id": 1}
    def post(self, request):
        track_id = request.data.get("track_id")
        if not track_id:
            return Response({"error": "track_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        track = MusicTrack.objects.filter(id=track_id, category="nature", is_active=True).first()
        if not track:
            return Response({"error": "Invalid track_id"}, status=status.HTTP_404_NOT_FOUND)

        play = SoundPlay.objects.create(user=request.user, track=track)
        return Response({"play_id": play.id}, status=status.HTTP_201_CREATED)


class NatureSoundPlayStopAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # POST /api/sounds/play/stop/  body: {"play_id": 1, "duration_sec": 240}
    def post(self, request):
        play_id = request.data.get("play_id")
        duration_sec = request.data.get("duration_sec")

        if not play_id or duration_sec is None:
            return Response({"error": "play_id and duration_sec are required"}, status=status.HTTP_400_BAD_REQUEST)

        play = SoundPlay.objects.filter(id=play_id, user=request.user).first()
        if not play:
            return Response({"error": "Invalid play_id"}, status=status.HTTP_404_NOT_FOUND)

        play.ended_at = timezone.now()
        play.duration_seconds = int(duration_sec)
        play.save(update_fields=["ended_at", "duration_seconds"])

        # optional: add to total stats too
        stats, _ = UserMusicStats.objects.get_or_create(user=request.user)
        stats.listening_seconds_total += max(0, int(duration_sec))
        stats.save(update_fields=["listening_seconds_total"])

        # Award rewards
        award_user_xp(request.user, xp=5, coins=1)
        update_user_streak(request.user)

        return Response({"message": "saved"}, status=status.HTTP_200_OK)


class NatureSoundStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/sounds/stats/
    def get(self, request):
        total = SoundPlay.objects.filter(user=request.user).aggregate(s=Sum("duration_seconds"))["s"] or 0
        return Response({"total_minutes": round(total / 60, 2)}, status=status.HTTP_200_OK)


# =========================
# BODY SCAN
# =========================
class BodyScanStepsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        steps = BodyScanStep.objects.filter(is_active=True).order_by("order")
        return Response(BodyScanStepSerializer(steps, many=True).data, status=status.HTTP_200_OK)


class BodyScanStartSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        steps_total = BodyScanStep.objects.filter(is_active=True).count()
        if steps_total == 0:
            return Response({"detail": "No steps configured."}, status=status.HTTP_400_BAD_REQUEST)

        session = BodyScanSession.objects.create(user=request.user, steps_total=steps_total)
        return Response(BodyScanSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class BodyScanDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        steps_total = BodyScanStep.objects.filter(is_active=True).count()
        last_session = BodyScanSession.objects.filter(user=request.user).order_by("-id").first()

        total_seconds_all = BodyScanSession.objects.filter(user=request.user).aggregate(total=Sum("total_seconds"))["total"] or 0

        return Response(
            {
                "steps_total": steps_total,
                "last_session": BodyScanSessionSerializer(last_session).data if last_session else None,
                "total_seconds_all_time": total_seconds_all,
            },
            status=status.HTTP_200_OK,
        )


class BodyScanActionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = BodyScanSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.is_completed:
            return Response({"detail": "Session already completed."}, status=status.HTTP_400_BAD_REQUEST)

        step_id = request.data.get("step_id")
        phase = request.data.get("phase")
        seconds = int(request.data.get("seconds") or 0)

        if not step_id or not phase:
            return Response({"detail": "step_id and phase are required."}, status=status.HTTP_400_BAD_REQUEST)

        step = BodyScanStep.objects.filter(id=step_id, is_active=True).first()
        if not step:
            return Response({"detail": "Step not found."}, status=status.HTTP_404_NOT_FOUND)

        phase = phase.upper().strip()
        allowed = {"TENSE", "HOLD", "RELEASE", "REST", "SKIP"}
        if phase not in allowed:
            return Response({"detail": f"Invalid phase. Use one of {sorted(list(allowed))}."}, status=status.HTTP_400_BAD_REQUEST)

        BodyScanStepLog.objects.create(session=session, step=step, phase=phase, seconds=max(0, seconds))

        session.total_seconds += max(0, seconds)

        if phase in {"RELEASE", "SKIP"}:
            completed_exists = BodyScanStepLog.objects.filter(session=session, step=step, phase__in=["RELEASE", "SKIP"]).count() > 1
            if not completed_exists:
                session.steps_completed = min(session.steps_completed + 1, session.steps_total)

        if session.steps_completed >= session.steps_total:
            session.is_completed = True
            session.ended_at = timezone.now()
            
            # Award rewards on completion
            award_user_xp(request.user, xp=20, coins=10)
            update_user_streak(request.user)

        session.save()

        return Response(
            {
                "session": BodyScanSessionSerializer(session).data,
                "last_action": {"step_id": step.id, "phase": phase, "seconds": max(0, seconds)},
            },
            status=status.HTTP_200_OK,
        )


class BodyScanSessionLogsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = BodyScanSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        logs = session.logs.all()
        return Response(BodyScanLogSerializer(logs, many=True).data, status=status.HTTP_200_OK)


class BodyScanResetSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = BodyScanSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        session.logs.all().delete()
        session.total_seconds = 0
        session.steps_completed = 0
        session.is_completed = False
        session.ended_at = None
        session.save()

        return Response({"detail": "Session reset successfully."}, status=status.HTTP_200_OK)
    

def _week_range(today=None):
    if today is None:
        today = timezone.localdate()
    end_date = today + timezone.timedelta(days=1)
    end_dt = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.min.time()))
    start_dt = end_dt - timezone.timedelta(days=7)
    return start_dt, end_dt


def _month_range(today=None):
    if today is None:
        today = timezone.localdate()
    end_date = today + timezone.timedelta(days=1)
    end_dt = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.min.time()))
    start_dt = end_dt - timezone.timedelta(days=30)
    return start_dt, end_dt


def _month_label(d_aware):
    return "Last 30 Days"




class ProfileSummaryAPIView(APIView):
    """
    Returns user profile data for the Profile screen:
    - username, email, first_name, last_name
    - streak_days, level, coins
    - days_active (total distinct days with any activity)
    - wellness_score (0–100 based on streak + activity diversity)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        stats, _ = UserStats.objects.get_or_create(user=user)

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
        days_active = len(all_active_days)

        streak_score = min(50, (stats.streak_days or 0) * 2)
        activity_types = sum([
            bool(mood_days), bool(journal_days), bool(sound_days),
            bool(bodyscan_days), bool(gratitude_days)
        ])
        activity_score = min(50, activity_types * 10)
        wellness_score = streak_score + activity_score

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile_picture_url = ""
        if profile.profile_picture:
            profile_picture_url = request.build_absolute_uri(profile.profile_picture.url)

        return Response({
            "username": getattr(user, "username", "User"),
            "email": getattr(user, "email", ""),
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "profile_picture": profile_picture_url,
            "streak_days": stats.streak_days or 0,
            "level": stats.level,
            "coins": stats.coins,
            "days_active": days_active,
            "wellness_score": wellness_score,
        })


class ProgressSummaryAPIView(APIView):

    """
    Progress main screen:
    - Mood Check-ins count
    - Journal Entries count
    - Achievements card (Level + achievements count)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mood_checkins = MoodCheckIn.objects.filter(user=request.user).count()
        journal_entries = JournalEntry.objects.filter(user=request.user).count()
        
        # New: Total meditations for the main progress screen
        sound_count = SoundPlay.objects.filter(user=request.user).count()
        bodyscan_count = BodyScanSession.objects.filter(user=request.user, is_completed=True).count()
        med_count = MeditationSession.objects.filter(user=request.user, is_completed=True).count()
        meditation_count = sound_count + bodyscan_count + med_count

        stats, _ = UserStats.objects.get_or_create(user=request.user)

        # You can change this logic later. This is a simple count for the UI.
        achievements_count = (stats.level * 5) + (stats.streak_days or 0)

        return Response({
            "mood_checkins": mood_checkins,
            "journal_entries": journal_entries,
            "meditation_sessions": meditation_count,
            "keep_going_message": "You're making great progress on your wellness journey. Consistency is key!",
            "achievements": {
                "level": stats.level,
                "count": achievements_count,
                "label": f"Level {stats.level}: {achievements_count} achievements",
            }
        })


class WeeklyReportAPIView(APIView):
    """
    Weekly Report screen:
    - total_checkins
    - meditation_sessions
    - journal_entries
    - improvement_percent + text
    - insights list
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        start, end = _week_range()
        p_start = start - timezone.timedelta(days=7)
        p_end = start

        def get_activity_counts(s, e):
            moods = MoodCheckIn.objects.filter(user=request.user, created_at__gte=s, created_at__lt=e)
            journals = JournalEntry.objects.filter(user=request.user, created_at__gte=s, created_at__lt=e).count()
            gratitudes = GratitudeEntry.objects.filter(user=request.user, created_at__gte=s, created_at__lt=e).count()
            meds = (
                SoundPlay.objects.filter(user=request.user, started_at__gte=s, started_at__lt=e).count() +
                BodyScanSession.objects.filter(user=request.user, started_at__gte=s, started_at__lt=e, is_completed=True).count() +
                MeditationSession.objects.filter(user=request.user, started_at__gte=s, started_at__lt=e, is_completed=True).count()
            )
            chats = ChatSession.objects.filter(user=request.user, created_at__gte=s, created_at__lt=e).count()
            return {
                "mood_count": moods.count(),
                "journal_count": journals,
                "gratitude_count": gratitudes,
                "med_count": meds,
                "chat_count": chats,
                "avg_stress": moods.aggregate(a=Avg("stress_level"))["a"] or 0,
                "mood_list": list(moods.values_list("mood", flat=True))
            }

        curr = get_activity_counts(start, end)
        prev = get_activity_counts(p_start, p_end)

        total_checkins = curr["mood_count"] + curr["journal_count"] + curr["gratitude_count"] + curr["chat_count"]
        meditation_sessions = curr["med_count"]
        journal_entries = curr["journal_count"]

        # Improvement calculation
        curr_score = (total_checkins * 2) + (meditation_sessions * 5) + (journal_entries * 3) + (curr["chat_count"] * 2)
        prev_score = (prev["mood_count"] + prev["journal_count"] + prev["gratitude_count"] + prev["chat_count"]) * 2 + (prev["med_count"] * 5) + (prev["journal_count"] * 3)
        
        improvement_percent = 0
        if prev_score > 0:
            improvement_percent = int(((curr_score - prev_score) / prev_score) * 100)
        elif curr_score > 0:
            improvement_percent = 100
        improvement_percent = max(-100, min(100, improvement_percent))

        # Dynamic Insights
        insights = []
        if curr["mood_list"]:
            from collections import Counter
            most_common_mood = Counter(curr["mood_list"]).most_common(1)[0][0]
            insights.append(f"Your most frequent mood this week was '{most_common_mood}'.")
        
        if curr["avg_stress"] > 0:
            insights.append(f"Average stress level: {round(curr['avg_stress'], 1)}/10")
            if prev["avg_stress"] > 0:
                if curr["avg_stress"] < prev["avg_stress"]:
                    insights.append("Great! Your stress is lower than last week.")
                elif curr["avg_stress"] > prev["avg_stress"]:
                    insights.append("Stress is up a bit—try some extra meditation.")

        if meditation_sessions > prev["med_count"]:
            insights.append(f"You've completed {meditation_sessions - prev['med_count']} more meditation(s) than last week!")
        elif meditation_sessions > 0:
            insights.append(f"You've stayed consistent with {meditation_sessions} meditations.")

        if not insights:
            insights = [
                "Start check-ins to see personalized weekly insights.",
                "Meditation correlates with better mood—try it today!",
                "Logging your thoughts helps reduce overall stress."
            ]

        status_text = f"Your wellness activity is up by {improvement_percent}%!" if improvement_percent >= 0 else f"Activity is down {abs(improvement_percent)}% - let's get back on track!"
        if improvement_percent == 0 and curr_score == 0:
            status_text = "Start your journey this week with a mood check-in!"

        return Response({
            "week_start": start.date().strftime("%b %d, %Y"),
            "week_end": (end - timezone.timedelta(days=1)).date().strftime("%b %d, %Y"),
            "summary": {
                "total_checkins": total_checkins,
                "meditation_sessions": meditation_sessions,
                "journal_entries": journal_entries,
            },
            "improvement": {
                "percent": abs(improvement_percent),
                "text": status_text,
            },
            "insights": insights[:3],
            "cta": {
                "button_text": "View Full Analytics"
            }
        })


class MonthlyReportAPIView(APIView):
    """
    Monthly Report screen:
    - month label (January 2026)
    - active_days (distinct days with any activity)
    - consistency % (active_days / days_elapsed_in_month)
    - mood_checks (MoodCheckIn count)
    - meditations (SoundPlay + BodyScan completed count)
    - achievement card (ex: 30-day wellness streak)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start, end = _month_range()
        today = timezone.localdate()

        # counts this month
        # In Monthly, we show "Mood Checks" as a specific card, 
        # but active_days should be comprehensive.
        # includes standalone MoodCheckIns and ChatSessions
        mood_checks = MoodCheckIn.objects.filter(
            user=request.user,
            created_at__gte=start,
            created_at__lt=end
        ).count()
        chat_checks = ChatSession.objects.filter(
            user=request.user,
            created_at__gte=start,
            created_at__lt=end
        ).count()
        
        combined_interactions = mood_checks + chat_checks
        
        # We can also sum all activities for a more 'complete' feel if needed
        total_activities = (combined_interactions + 
                          JournalEntry.objects.filter(user=request.user, created_at__gte=start, created_at__lt=end).count() +
                          GratitudeEntry.objects.filter(user=request.user, created_at__gte=start, created_at__lt=end).count())

        sound_sessions = SoundPlay.objects.filter(
            user=request.user,
            started_at__gte=start,
            started_at__lt=end
        ).count()

        bodyscan_sessions = BodyScanSession.objects.filter(
            user=request.user,
            started_at__gte=start,
            started_at__lt=end,
            is_completed=True
        ).count()

        program_sessions = MeditationSession.objects.filter(
            user=request.user,
            started_at__gte=start,
            started_at__lt=end,
            is_completed=True
        ).count()

        meditations = sound_sessions + bodyscan_sessions + program_sessions

        # Active days = distinct days where user did any action
        mood_days = {timezone.localtime(o.created_at).date() for o in MoodCheckIn.objects.filter(
            user=request.user, created_at__gte=start, created_at__lt=end
        )}

        journal_days = {timezone.localtime(o.created_at).date() for o in JournalEntry.objects.filter(
            user=request.user, created_at__gte=start, created_at__lt=end
        )}

        sound_days = {timezone.localtime(o.started_at).date() for o in SoundPlay.objects.filter(
            user=request.user, started_at__gte=start, started_at__lt=end
        )}

        bodyscan_days = {timezone.localtime(o.started_at).date() for o in BodyScanSession.objects.filter(
            user=request.user, started_at__gte=start, started_at__lt=end, is_completed=True
        )}

        meditation_days = {timezone.localtime(o.started_at).date() for o in MeditationSession.objects.filter(
            user=request.user, started_at__gte=start, started_at__lt=end, is_completed=True
        )}

        gratitude_days = {timezone.localtime(o.created_at).date() for o in GratitudeEntry.objects.filter(
            user=request.user, created_at__gte=start, created_at__lt=end
        )}

        drawing_days = {timezone.localtime(o.created_at).date() for o in CreativeDrawing.objects.filter(
            user=request.user, created_at__gte=start, created_at__lt=end
        )}

        chat_days = {timezone.localtime(o.created_at).date() for o in ChatSession.objects.filter(
            user=request.user, created_at__gte=start, created_at__lt=end
        )}

        affirmation_days = {timezone.localtime(o.last_viewed_at).date() for o in UserAffirmationState.objects.filter(
            user=request.user, last_viewed_at__gte=start, last_viewed_at__lt=end
        )}

        active_days = len(
            mood_days | journal_days | sound_days | bodyscan_days | 
            meditation_days | gratitude_days | drawing_days | chat_days | affirmation_days
        )

        # Consistency = active_days / days elapsed in month (up to today)
        days_elapsed = (today - start.date()).days + 1
        if days_elapsed <= 0:
            days_elapsed = 1
        consistency_percent = int(round((active_days / days_elapsed) * 100))
        if consistency_percent > 100:
            consistency_percent = 100

        stats, _ = UserStats.objects.get_or_create(user=request.user)
        unlocked = (stats.streak_days or 0) >= 30

        achievement_title = "Achievement Unlocked!" if unlocked else "Keep Building Streak!"
        achievement_subtitle = "30-Day Wellness Streak" if unlocked else "Reach 30 days to unlock"

        return Response({
            "month": _month_label(start),  # "January 2026"
            "cards": {
                "active_days": active_days,
                "consistency_percent": consistency_percent,
                "mood_checks": combined_interactions,
                "meditations": meditations,
            },
            "achievement": {
                "title": achievement_title,
                "subtitle": achievement_subtitle,
                "streak_days": stats.streak_days or 0,
            },
            "cta": {
                "button_text": "Get Next Month's Plan"
            }
        })
    




class SettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings_obj, _ = AppSettings.objects.get_or_create(user=request.user)
        return Response(AppSettingsSerializer(settings_obj).data, status=status.HTTP_200_OK)

    def put(self, request):
        settings_obj, _ = AppSettings.objects.get_or_create(user=request.user)
        ser = AppSettingsSerializer(settings_obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class PrivacyExportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        export = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "counts": {
                "mood_checkins": MoodCheckIn.objects.filter(user=user).count(),
                "journal_entries": JournalEntry.objects.filter(user=user).count(),
                "gratitude_entries": GratitudeEntry.objects.filter(user=user).count(),
                "sound_plays": SoundPlay.objects.filter(user=user).count(),
                "body_scan_sessions": BodyScanSession.objects.filter(user=user).count(),
            },
            "recent_mood_checkins": list(
                MoodCheckIn.objects.filter(user=user).order_by("-created_at")[:20]
                .values("id", "mood", "stress_level", "created_at")
            ),
            "recent_journal_entries": list(
                JournalEntry.objects.filter(user=user).order_by("-created_at")[:20]
                .values("id", "text", "created_at")
            ),
        }

        return Response(export, status=status.HTTP_200_OK)


class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password") or ""
        if not password:
            return Response({"error": "password is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(password):
            return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_200_OK)


class FeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = FeedbackCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        message = ser.validated_data["message"]
        rating = ser.validated_data.get("rating")

        fb = Feedback.objects.create(user=request.user, message=message, rating=rating)

        return Response({"message": "Feedback submitted", "id": fb.id}, status=status.HTTP_201_CREATED)
    
# -------------------------
# Helpers
# -------------------------
def _date_range_from_param(range_key: str):
    """
    range_key: week | month | all
    returns (start_dt, end_dt)
    """
    now = timezone.now()
    today = timezone.localdate()

    if range_key == "week":
        # start of week (Mon)
        start_date = today - timezone.timedelta(days=today.weekday())
        start_dt = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
        return start_dt, now

    if range_key == "month":
        start_date = today.replace(day=1)
        start_dt = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
        return start_dt, now

    # all
    return None, now


def _suggestion_for(mood: str, stress: int):
    mood = (mood or "").lower()
    stress = int(stress or 0)

    if stress >= 8:
        return ("Quick reset", "Try 4-7-8 breathing for 2 minutes. Then sip water and relax your shoulders.")
    if mood in {"stressed", "angry"}:
        return ("Calm down", "Do box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s. Repeat 4 times.")
    if mood in {"sad", "tired"}:
        return ("Gentle support", "Take a short walk or stretch for 3 minutes. Write 1 small positive thing.")
    if mood in {"great"}:
        return ("Keep going", "Awesome! Save this moment—write 1 line about what made you feel good today.")
    return ("Wellness tip", "Take 3 slow breaths and do a 1-minute body scan: head → shoulders → chest → belly.")


def _tips_for(mood: str, stress: int):
    mood = (mood or "").lower()
    stress = int(stress or 0)

    tips = []

    # Stress-based
    if stress >= 7:
        tips.append({
            "title": "2-minute breathing",
            "duration_min": 2,
            "steps": ["Inhale 4s", "Hold 2s", "Exhale 6s", "Repeat for 2 minutes"]
        })
        tips.append({
            "title": "Grounding 5-4-3-2-1",
            "duration_min": 3,
            "steps": ["5 things you see", "4 things you feel", "3 things you hear", "2 things you smell", "1 thing you taste"]
        })

    # Mood-based
    if mood in {"sad"}:
        tips.append({
            "title": "Small kindness to self",
            "duration_min": 4,
            "steps": ["Write one supportive sentence to yourself", "Drink water", "Message a friend or take fresh air"]
        })
    elif mood in {"angry"}:
        tips.append({
            "title": "Release tension",
            "duration_min": 3,
            "steps": ["Clench fists 5s", "Release 5s", "Roll shoulders", "Slow exhale"]
        })
    elif mood in {"tired"}:
        tips.append({
            "title": "Energy reset",
            "duration_min": 5,
            "steps": ["Neck stretch", "Shoulder stretch", "30s deep breathing", "Light walk inside room"]
        })
    elif mood in {"great"}:
        tips.append({
            "title": "Lock in the positive",
            "duration_min": 3,
            "steps": ["Write what went well", "What you did", "One thing to repeat tomorrow"]
        })

    if not tips:
        tips.append({
            "title": "1-minute calm",
            "duration_min": 1,
            "steps": ["Sit comfortably", "Breathe slowly", "Relax jaw and shoulders"]
        })

    return tips


# -------------------------
# 1) Check-In Complete Summary
# GET /api/mood/last-summary/
# -------------------------
class MoodLastSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        last = MoodCheckIn.objects.filter(user=request.user).order_by("-created_at").first()
        if not last:
            return Response(
                {"detail": "No mood check-ins yet."},
                status=status.HTTP_200_OK
            )

        title, text = _suggestion_for(last.mood, last.stress_level)

        payload = {
            "mood": last.mood,
            "stress_level": int(last.stress_level or 0),
            "created_at": last.created_at,
            "suggestion_title": title,
            "suggestion_text": text,
        }
        return Response(MoodLastSummarySerializer(payload).data, status=status.HTTP_200_OK)


# -------------------------
# 2) Tips (for “Get Personalized Suggestions”)
# GET /api/mood/tips/?mood=okay&stress=5
# -------------------------
class MoodTipsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mood = request.query_params.get("mood") or ""
        stress = request.query_params.get("stress") or "0"
        try:
            stress = int(stress)
        except Exception:
            stress = 0

        tips = _tips_for(mood, stress)
        return Response(MoodTipSerializer(tips, many=True).data, status=status.HTTP_200_OK)


# -------------------------
# 3) Mood Analytics Screen
# GET /api/mood/analytics/?range=week|month|all
# -------------------------
class MoodAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        range_key = (request.query_params.get("range") or "week").lower().strip()
        start_dt, end_dt = _date_range_from_param(range_key)

        base_qs = MoodCheckIn.objects.filter(user=request.user)
        if start_dt:
            period_qs = base_qs.filter(created_at__gte=start_dt, created_at__lte=end_dt)
        else:
            period_qs = base_qs

        total_checkins = base_qs.count()
        this_period_checkins = period_qs.count()

        # distribution in selected period
        dist = list(
            period_qs.values("mood").annotate(count=Count("id")).order_by("-count")
        )

        # most common mood
        most_common = dist[0] if dist else {"mood": "", "count": 0, "percent": 0}

        if this_period_checkins > 0 and most_common.get("count", 0) > 0:
            most_common["percent"] = int(round((most_common["count"] / this_period_checkins) * 100))
        else:
            most_common["percent"] = 0

        # average stress
        avg_stress = period_qs.aggregate(a=Avg("stress_level"))["a"] or 0.0
        avg_stress = float(round(avg_stress, 1))

        # trend (compare last 7 days avg stress with previous 7 days)
        now = timezone.now()
        last7_start = now - timezone.timedelta(days=7)
        prev7_start = now - timezone.timedelta(days=14)

        last7_avg = base_qs.filter(created_at__gte=last7_start).aggregate(a=Avg("stress_level"))["a"]
        prev7_avg = base_qs.filter(created_at__gte=prev7_start, created_at__lt=last7_start).aggregate(a=Avg("stress_level"))["a"]

        trend = "stable"
        if last7_avg is not None and prev7_avg is not None:
            if last7_avg < prev7_avg - 0.3:
                trend = "down"
            elif last7_avg > prev7_avg + 0.3:
                trend = "up"

        insights = []
        if this_period_checkins == 0:
            insights.append("Do at least 3 check-ins to unlock better insights.")
        else:
            insights.append(f"Most common mood: {most_common.get('mood','') or 'N/A'}")
            insights.append(f"Average stress is {avg_stress}/10")
            if trend == "down":
                insights.append("Good news: your stress levels are trending down.")
            elif trend == "up":
                insights.append("Your stress is trending up—try short breathing breaks daily.")
            else:
                insights.append("Your stress trend looks stable this period.")

        payload = {
            "total_checkins": total_checkins,
            "this_period_checkins": this_period_checkins,
            "most_common_mood": most_common,
            "avg_stress": avg_stress,
            "trend": trend,
            "insights": insights,
            "distribution": dist,
        }
        return Response(MoodAnalyticsSerializer(payload).data, status=status.HTTP_200_OK)


# -------------------------
# 4) AI Insights / Recommendations Screen
# GET /api/ai/insights/
# -------------------------
class AIInsightsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = MoodCheckIn.objects.filter(user=request.user).order_by("-created_at")
        data_points = qs.count()

        # If not enough data, show “Keep using the app” screen
        MIN_POINTS = 5
        if data_points < MIN_POINTS:
            payload = {
                "has_enough_data": False,
                "data_points": data_points,
                "insights_count": 0,
                "patterns_count": 0,
                "insights": [],
                "patterns": [],
            }
            return Response(AIInsightsSerializer(payload).data, status=status.HTTP_200_OK)

        # Simple “AI-like” insights from rules (safe + works offline)
        last = qs.first()
        last_mood = last.mood if last else ""
        avg_stress_30 = qs.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30)).aggregate(a=Avg("stress_level"))["a"] or 0
        avg_stress_30 = float(round(avg_stress_30, 1))

        common = list(qs.values("mood").annotate(c=Count("id")).order_by("-c")[:2])
        common_moods = [x["mood"] for x in common if x.get("mood")]

        insights = [
            f"Your recent mood is '{last_mood}'.",
            f"Your 30-day average stress is {avg_stress_30}/10.",
        ]
        if common_moods:
            insights.append(f"Your most frequent moods: {', '.join(common_moods)}.")

        patterns = []
        if avg_stress_30 >= 7:
            patterns.append("High stress pattern detected. Try daily 2-minute breathing.")
        if "stressed" in common_moods:
            patterns.append("Stress appears frequently. Consider scheduling short breaks.")
        if "great" in common_moods:
            patterns.append("Positive mood appears often—keep repeating what works.")

        payload = {
            "has_enough_data": True,
            "data_points": data_points,
            "insights_count": len(insights),
            "patterns_count": len(patterns),
            "insights": insights,
            "patterns": patterns,
        }
        return Response(AIInsightsSerializer(payload).data, status=status.HTTP_200_OK)



class MeditationProgramListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/meditations/
    def get(self, request):
        category = request.query_params.get("category")
        qs = MeditationProgram.objects.filter(is_active=True).order_by("id")
        if category:
            qs = qs.filter(category=category)

        data = MeditationProgramSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)


class MeditationProgramDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/meditations/<id>/
    def get(self, request, pk):
        program = get_object_or_404(MeditationProgram, pk=pk, is_active=True)
        data = MeditationProgramSerializer(program, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)


class MeditationStartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # POST /api/meditations/start/  body: {"program_id": 1}
    def post(self, request):
        ser = MeditationStartSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        program_id = ser.validated_data["program_id"]
        program = MeditationProgram.objects.filter(id=program_id, is_active=True).first()
        if not program:
            return Response({"error": "Invalid program_id"}, status=status.HTTP_404_NOT_FOUND)

        session = MeditationSession.objects.create(user=request.user, program=program)
        return Response(
            {
                "session_id": session.id,
                "program_id": program.id,
                "started_at": session.started_at,
            },
            status=status.HTTP_201_CREATED,
        )


class MeditationStopAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # POST /api/meditations/stop/  body: {"session_id": 1, "duration_sec": 240}
    def post(self, request):
        ser = MeditationStopSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        session_id = ser.validated_data["session_id"]
        duration_sec = ser.validated_data["duration_sec"]

        session = MeditationSession.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"error": "Invalid session_id"}, status=status.HTTP_404_NOT_FOUND)

        if session.ended_at:
            return Response({"error": "Session already ended"}, status=status.HTTP_400_BAD_REQUEST)

        session.ended_at = timezone.now()
        session.duration_seconds = int(duration_sec)
        session.is_completed = True
        session.save(update_fields=["ended_at", "duration_seconds", "is_completed"])

        # Award rewards
        award_user_xp(request.user, xp=20, coins=10)
        update_user_streak(request.user)

        return Response(
            {
                "message": "saved",
                "session_id": session.id,
                "duration_seconds": session.duration_seconds,
            },
            status=status.HTTP_200_OK,
        )


class MeditationDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/meditations/dashboard/
    def get(self, request):
        today = timezone.localdate()
        w_start, w_end = _week_range(today)
        m_start, m_end = _month_range(today)

        total_sessions = MeditationSession.objects.filter(user=request.user, is_completed=True).count()

        week_sessions = MeditationSession.objects.filter(
            user=request.user, is_completed=True,
            started_at__gte=w_start, started_at__lt=w_end
        ).count()

        month_sessions = MeditationSession.objects.filter(
            user=request.user, is_completed=True,
            started_at__gte=m_start, started_at__lt=m_end
        ).count()

        total_seconds = MeditationSession.objects.filter(user=request.user, is_completed=True).aggregate(
            s=Sum("duration_seconds")
        )["s"] or 0

        # simple wellness score (0..100) based on this week activity
        # 7 sessions/week -> 100%
        wellness_score = min(int((week_sessions / 7) * 100), 100)

        return Response(
            {
                "total_sessions": total_sessions,
                "week_sessions": week_sessions,
                "month_sessions": month_sessions,
                "total_minutes": round(total_seconds / 60, 2),
                "wellness_score": wellness_score,
            },
            status=status.HTTP_200_OK,
        )