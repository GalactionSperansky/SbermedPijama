from django.db import migrations


SPECIALTIES = [
    ("Оториноларинголог", "ent", "Диагностика и лечение заболеваний уха, горла и носа"),
    ("Терапевт", "therapist", "Первичная консультация взрослых и маршрутизация к узким специалистам"),
    ("Аллерголог", "allergist", "Диагностика и сопровождение аллергических состояний"),
    ("Педиатр", "pediatrician", "Здоровье детей и подростков"),
    ("Невролог", "neurologist", "Заболевания нервной системы, головные боли и головокружения"),
    ("Кардиолог", "cardiologist", "Заболевания сердца и сосудов"),
    ("Гастроэнтеролог", "gastroenterologist", "Заболевания желудочно-кишечного тракта"),
    ("Дерматолог", "dermatologist", "Заболевания кожи, волос и ногтей"),
    ("Эндокринолог", "endocrinologist", "Нарушения обмена веществ и эндокринной системы"),
    ("Офтальмолог", "ophthalmologist", "Диагностика заболеваний глаз и нарушений зрения"),
]


DOCTORS = [
    ("Анна Сергеевна Лебедева", "ent", 12, "Взрослый ЛОР-врач. Специализируется на заболеваниях носа и околоносовых пазух."),
    ("Михаил Олегович Воронов", "ent", 8, "ЛОР-врач для взрослых и детей от 7 лет. Ведёт пациентов с нарушениями слуха и заболеваниями уха."),
    ("Илья Павлович Романов", "ent", 17, "ЛОР-врач высшей категории. Профиль — хронические заболевания горла и эндоскопическая диагностика."),
    ("Елена Викторовна Миронова", "therapist", 15, "Терапевт широкого профиля. Проводит первичную оценку симптомов и формирует план обследований."),
    ("Алексей Николаевич Громов", "therapist", 7, "Терапевт. Профилактические осмотры, острые респираторные состояния и диспансерное наблюдение."),
    ("Дарья Андреевна Соколова", "allergist", 9, "Аллерголог-иммунолог. Респираторная аллергия, поллиноз и аллергические реакции."),
    ("Ольга Максимовна Орлова", "allergist", 13, "Аллерголог для взрослых и детей. Ведёт пациентов с бронхиальной астмой и атопическими состояниями."),
    ("Мария Игоревна Белова", "pediatrician", 11, "Педиатр. Принимает детей с рождения, ведёт острые состояния и профилактические осмотры."),
    ("Софья Денисовна Крылова", "pediatrician", 6, "Педиатр. Специализируется на частых респираторных заболеваниях у детей."),
    ("Вадим Аркадьевич Фёдоров", "neurologist", 14, "Невролог. Головные боли, головокружения, нарушения сна и боли в спине."),
    ("Наталья Романовна Ким", "cardiologist", 16, "Кардиолог. Нарушения ритма, артериальная гипертензия и профилактика сердечно-сосудистых рисков."),
    ("Павел Ильич Захаров", "gastroenterologist", 10, "Гастроэнтеролог. Боли в животе, нарушения пищеварения и заболевания печени."),
    ("Ксения Львовна Тихонова", "dermatologist", 8, "Дерматолог. Воспалительные заболевания кожи, высыпания и диагностика новообразований."),
    ("Ирина Алексеевна Волкова", "endocrinologist", 12, "Эндокринолог. Заболевания щитовидной железы, нарушения веса и углеводного обмена."),
    ("Артём Евгеньевич Сафонов", "ophthalmologist", 9, "Офтальмолог. Снижение зрения, воспалительные заболевания глаз и профилактические осмотры."),
]


def expand_catalog(apps, schema_editor):
    Specialty = apps.get_model("api", "Specialty")
    Doctor = apps.get_model("api", "Doctor")

    specialties = {}
    for name, slug, description in SPECIALTIES:
        specialty, _ = Specialty.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "description": description},
        )
        specialties[slug] = specialty

    for full_name, specialty_slug, experience_years, bio in DOCTORS:
        Doctor.objects.update_or_create(
            full_name=full_name,
            defaults={
                "specialty": specialties[specialty_slug],
                "experience_years": experience_years,
                "bio": bio,
                "is_available": True,
            },
        )


def contract_catalog(apps, schema_editor):
    Doctor = apps.get_model("api", "Doctor")
    Specialty = apps.get_model("api", "Specialty")
    original_doctors = {
        "Анна Сергеевна Лебедева",
        "Михаил Олегович Воронов",
        "Елена Викторовна Миронова",
        "Дарья Андреевна Соколова",
        "Мария Игоревна Белова",
    }
    Doctor.objects.filter(full_name__in=[name for name, *_ in DOCTORS if name not in original_doctors]).delete()
    Specialty.objects.filter(
        slug__in=[slug for _, slug, _ in SPECIALTIES if slug not in {"ent", "therapist", "allergist", "pediatrician"}]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0008_intakesession_intakemessage")]
    operations = [migrations.RunPython(expand_catalog, contract_catalog)]
