from datetime import datetime, time, timedelta

from django.contrib.auth import logout
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .models import Appointment, Doctor, IntakeMessage, IntakeSession, MedicalRecord, Medication, PatientProfile, Slot, Specialty, SupportRequest
from .serializers import (
    AppointmentSerializer,
    DoctorSerializer,
    LoginSerializer,
    MedicalRecordSerializer,
    MedicationSerializer,
    PatientProfileSerializer,
    RegisterSerializer,
    SpecialtySerializer,
    SupportRequestSerializer,
    IntakeTurnSerializer,
)
from .services.anamnesis import run_anamnesis_turn
from .services.gigachat import GigaChatError


APPOINTMENT_TIMES = [time(hour, minute) for hour in range(8, 21) for minute in (0, 30)]


class AnamnesisRateThrottle(UserRateThrottle):
    rate = "30/min"


def _resolve_specialty(label):
    if not label:
        return None
    exact = Specialty.objects.filter(name__iexact=label.strip()).first()
    if exact:
        return exact
    normalized = label.strip().lower().replace("ё", "е")
    aliases = {
        "лор": "ent",
        "лор-врач": "ent",
        "оториноларинголог": "ent",
        "терапевт": "therapist",
        "педиатр": "pediatrician",
        "аллерголог": "allergist",
        "аллерголог-иммунолог": "allergist",
        "невролог": "neurologist",
        "кардиолог": "cardiologist",
        "гастроэнтеролог": "gastroenterologist",
        "дерматолог": "dermatologist",
        "дерматовенеролог": "dermatologist",
        "эндокринолог": "endocrinologist",
        "офтальмолог": "ophthalmologist",
        "окулист": "ophthalmologist",
    }
    slug = aliases.get(normalized)
    return Specialty.objects.filter(slug=slug).first() if slug else None


def _recommend_doctor(specialty):
    if not specialty:
        return None
    return (
        Doctor.objects.filter(specialty=specialty, is_available=True)
        .annotate(
            upcoming_appointments=Count(
                "appointments",
                filter=Q(appointments__starts_at__gte=timezone.now()),
            )
        )
        .order_by("upcoming_appointments", "-experience_years", "full_name")
        .first()
    )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"status": "ok", "service": "clinic-assistant", "time": timezone.now()})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {"token": token.key, "user": PatientProfileSerializer(user.patient_profile).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": PatientProfileSerializer(user.patient_profile).data})


@api_view(["POST"])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "PATCH"])
def me(request):
    profile = request.user.patient_profile
    if request.method == "PATCH":
        serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(PatientProfileSerializer(profile).data)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def admin_summary(request):
    return Response(
        {
            "patients": PatientProfile.objects.filter(role=PatientProfile.Role.PATIENT).count(),
            "doctors": Doctor.objects.filter(is_available=True).count(),
            "appointments": Appointment.objects.count(),
            "support_open": SupportRequest.objects.filter(is_resolved=False).count(),
        }
    )


@api_view(["POST"])
@throttle_classes([AnamnesisRateThrottle])
def anamnesis_chat(request):
    serializer = IntakeTurnSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session_id = serializer.validated_data.get("session_id")
    if session_id:
        session = get_object_or_404(
            IntakeSession, pk=session_id, patient=request.user, status=IntakeSession.Status.ACTIVE
        )
    else:
        session = IntakeSession.objects.create(patient=request.user)

    user_message = IntakeMessage.objects.create(
        session=session, role=IntakeMessage.Role.USER, content=serializer.validated_data["message"]
    )
    try:
        result, source = run_anamnesis_turn(session)
    except GigaChatError:
        user_message.delete()
        if not session.messages.exists():
            session.delete()
        return Response(
            {"detail": "ИИ-помощник временно недоступен. Попробуйте ещё раз позднее."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    IntakeMessage.objects.create(
        session=session, role=IntakeMessage.Role.ASSISTANT,
        content=result["message"], structured_data=result,
    )
    specialty = _resolve_specialty(result["specialty"])
    if result["anamnesis_complete"] and not specialty:
        specialty = Specialty.objects.filter(slug="therapist").first()
    if specialty:
        result["specialty"] = specialty.name
    recommended_doctor = _recommend_doctor(specialty) if result["anamnesis_complete"] else None
    session.urgency = result["urgency"]
    session.specialty = specialty
    session.summary = result["summary"]
    if result["anamnesis_complete"]:
        session.status = (
            IntakeSession.Status.URGENT
            if result["urgency"] == IntakeSession.Urgency.URGENT
            else IntakeSession.Status.COMPLETED
        )
    else:
        session.status = IntakeSession.Status.ACTIVE
    session.save(update_fields=["urgency", "specialty", "summary", "status", "updated_at"])
    return Response({
        "session_id": session.id,
        **result,
        "recommended_doctor": DoctorSerializer(recommended_doctor).data if recommended_doctor else None,
        "source": source,
    })


@api_view(["GET"])
def availability(request):
    doctor_id = request.query_params.get("doctor")
    doctor = get_object_or_404(Doctor, pk=doctor_id, is_available=True)
    today = timezone.localdate()
    start = parse_date(request.query_params.get("from", "")) or today
    start = max(start, today)
    try:
        days_count = min(max(int(request.query_params.get("days", 7)), 1), 14)
    except ValueError:
        return Response({"detail": "Параметр days должен быть числом."}, status=status.HTTP_400_BAD_REQUEST)

    range_end = start + timedelta(days=days_count)
    booked_starts = set(
        Appointment.objects.filter(
            doctor=doctor,
            starts_at__date__gte=start,
            starts_at__date__lt=range_end,
        ).values_list("starts_at", flat=True)
    )
    now = timezone.now()
    days = []
    for offset in range(days_count):
        day = start + timedelta(days=offset)
        slots = []
        for slot_index, slot_time in enumerate(APPOINTMENT_TIMES):
            starts_at = timezone.make_aware(
                datetime.combine(day, slot_time),
                timezone.get_current_timezone(),
            )
            schedule_blocked = (doctor.pk + day.toordinal() + slot_index * 2) % 7 == 0
            slot, _ = Slot.objects.get_or_create(
                doctor=doctor,
                date_and_time=starts_at,
                defaults={"is_available": not schedule_blocked},
            )
            is_past = starts_at <= now
            is_booked = starts_at in booked_starts or hasattr(slot, "appointment")
            available = slot.is_available and not is_past and not is_booked
            slots.append({
                "id": slot.id,
                "time": slot_time.strftime("%H:%M"),
                "starts_at": starts_at.isoformat(),
                "available": available,
            })
        days.append({"date": day.isoformat(), "slots": slots})

    return Response({"doctor": doctor.id, "from": start.isoformat(), "days": days})


class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [permissions.AllowAny]


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.select_related("specialty").filter(is_available=True)
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related("doctor", "doctor__specialty").all()
    serializer_class = AppointmentSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.is_staff else queryset.filter(patient=self.request.user)

    def perform_create(self, serializer):
        profile = self.request.user.patient_profile
        with transaction.atomic():
            slot = Slot.objects.select_for_update().get(pk=serializer.validated_data["slot"].pk)
            if not slot.is_available or Appointment.objects.filter(slot=slot).exists():
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"slot": "Это время уже занято."})
            serializer.save(
                slot=slot,
                doctor=slot.doctor,
                starts_at=slot.date_and_time,
                patient=self.request.user,
                patient_name=profile.user.get_full_name() or profile.user.email,
                phone=profile.phone,
            )
            slot.is_available = False
            slot.save(update_fields=["is_available"])


class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.is_staff else queryset.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class SupportRequestViewSet(viewsets.ModelViewSet):
    queryset = SupportRequest.objects.all()
    serializer_class = SupportRequestSerializer
    http_method_names = ["post", "head", "options"]

    def perform_create(self, serializer):
        profile = self.request.user.patient_profile
        serializer.save(
            patient=self.request.user,
            name=profile.user.get_full_name() or profile.user.email,
            email=profile.user.email,
        )


class MedicalRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.is_staff else queryset.filter(patient=self.request.user)
