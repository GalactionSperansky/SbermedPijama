from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .avatar import avatar_indices
from .models import PatientProfile


@receiver(post_save, sender=User)
def ensure_patient_profile(sender, instance, created, **kwargs):
    background, dino = avatar_indices(instance.email or instance.username)
    profile, _ = PatientProfile.objects.get_or_create(
        user=instance,
        defaults={
            "role": PatientProfile.Role.ADMIN if instance.is_staff else PatientProfile.Role.PATIENT,
            "avatar_background": background,
            "avatar_dino": dino,
        },
    )
    expected_role = PatientProfile.Role.ADMIN if instance.is_staff else PatientProfile.Role.PATIENT
    if profile.role != expected_role:
        profile.role = expected_role
        profile.save(update_fields=["role"])
