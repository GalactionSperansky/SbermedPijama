from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet,
    MedicalRecordViewSet,
    DoctorViewSet,
    MedicationViewSet,
    SpecialtyViewSet,
    SupportRequestViewSet,
    admin_summary,
    anamnesis_chat,
    availability,
    health,
    login,
    logout_view,
    me,
    register,
)

router = DefaultRouter()
router.register("specialties", SpecialtyViewSet)
router.register("doctors", DoctorViewSet)
router.register("appointments", AppointmentViewSet)
router.register("medications", MedicationViewSet)
router.register("support", SupportRequestViewSet)
router.register("medical-records", MedicalRecordViewSet)

urlpatterns = [
    path("health/", health),
    path("auth/register/", register),
    path("auth/login/", login),
    path("auth/logout/", logout_view),
    path("auth/me/", me),
    path("admin/summary/", admin_summary),
    path("availability/", availability),
    path("anamnesis/chat/", anamnesis_chat),
    path("", include(router.urls)),
]
