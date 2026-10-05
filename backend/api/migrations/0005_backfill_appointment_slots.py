from django.db import migrations


def backfill_appointment_slots(apps, schema_editor):
    Appointment = apps.get_model("api", "Appointment")
    Slot = apps.get_model("api", "Slot")
    for appointment in Appointment.objects.filter(slot__isnull=True).iterator():
        slot, _ = Slot.objects.get_or_create(
            doctor_id=appointment.doctor_id,
            date_and_time=appointment.starts_at,
            defaults={"is_available": False},
        )
        slot.is_available = False
        slot.save(update_fields=["is_available"])
        appointment.slot_id = slot.id
        appointment.save(update_fields=["slot"])


class Migration(migrations.Migration):
    dependencies = [("api", "0004_appointment_description_appointment_diagnosis_and_more")]

    operations = [migrations.RunPython(backfill_appointment_slots, migrations.RunPython.noop)]
