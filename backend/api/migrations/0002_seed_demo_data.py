from django.db import migrations


def seed_demo_data(apps, schema_editor):
    Specialty = apps.get_model("api", "Specialty")
    Doctor = apps.get_model("api", "Doctor")

    specialty_data = [
        ("Оториноларинголог", "ent", "Заболевания уха, горла и носа"),
        ("Терапевт", "therapist", "Первичная консультация взрослых"),
        ("Аллерголог", "allergist", "Диагностика и сопровождение аллергических состояний"),
        ("Педиатр", "pediatrician", "Здоровье детей и подростков"),
    ]
    specialties = {}
    for name, slug, description in specialty_data:
        specialties[slug], _ = Specialty.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "description": description},
        )

    doctors = [
        ("Анна Сергеевна Лебедева", "ent", 12),
        ("Михаил Олегович Воронов", "ent", 8),
        ("Елена Викторовна Миронова", "therapist", 15),
        ("Дарья Андреевна Соколова", "allergist", 9),
        ("Мария Игоревна Белова", "pediatrician", 11),
    ]
    for full_name, specialty_slug, experience_years in doctors:
        Doctor.objects.get_or_create(
            full_name=full_name,
            defaults={
                "specialty": specialties[specialty_slug],
                "experience_years": experience_years,
                "is_available": True,
            },
        )


def remove_demo_data(apps, schema_editor):
    Doctor = apps.get_model("api", "Doctor")
    Specialty = apps.get_model("api", "Specialty")
    Doctor.objects.filter(
        full_name__in=[
            "Анна Сергеевна Лебедева",
            "Михаил Олегович Воронов",
            "Елена Викторовна Миронова",
            "Дарья Андреевна Соколова",
            "Мария Игоревна Белова",
        ]
    ).delete()
    Specialty.objects.filter(slug__in=["ent", "therapist", "allergist", "pediatrician"]).delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0001_initial")]
    operations = [migrations.RunPython(seed_demo_data, remove_demo_data)]

