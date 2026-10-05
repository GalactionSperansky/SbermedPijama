from django.contrib import admin
from .models import (
    Appointment,
    Certificate,
    Doctor,
    Drug,
    MedicalRecord,
    Medication,
    IntakeMessage,
    IntakeSession,
    PatientProfile,
    Prescription,
    Referral,
    Slot,
    Specialty,
    SupportRequest,
)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["full_name", "specialty", "phone_number", "email", "experience_years", "is_available"]
    list_filter = ["specialty", "is_available"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["patient_name", "doctor", "slot", "status"]
    list_filter = ["status", "doctor__specialty"]
    search_fields = ["patient_name", "phone"]


admin.site.register(Medication)
admin.site.register(SupportRequest)
admin.site.register(PatientProfile)
admin.site.register(MedicalRecord)
admin.site.register(Prescription)
admin.site.register(Certificate)
admin.site.register(Drug)
admin.site.register(Referral)


class IntakeMessageInline(admin.TabularInline):
    model = IntakeMessage
    extra = 0
    readonly_fields = ["role", "content", "structured_data", "created_at"]


@admin.register(IntakeSession)
class IntakeSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "patient", "status", "urgency", "specialty", "updated_at"]
    list_filter = ["status", "urgency", "specialty"]
    inlines = [IntakeMessageInline]


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ["doctor", "date_and_time", "is_available"]
    list_filter = ["doctor", "is_available"]
    date_hierarchy = "date_and_time"
