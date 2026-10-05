from django.db import models
from django.contrib.auth.models import User


class PatientProfile(models.Model):
    class Role(models.TextChoices):
        PATIENT = "patient", "Пациент"
        ADMIN = "admin", "Администратор"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    middle_name = models.CharField("Отчество", max_length=150, blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    policy_number = models.CharField("Номер полиса", max_length=32, blank=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.PATIENT)
    avatar_background = models.PositiveSmallIntegerField(default=1, editable=False)
    avatar_dino = models.PositiveSmallIntegerField(default=1, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Профиль пациента"
        verbose_name_plural = "Профили пациентов"

    def __str__(self):
        return self.user.get_full_name() or self.user.email or self.user.username


class Specialty(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Doctor(models.Model):
    full_name = models.CharField("ФИО", max_length=180)
    name = models.CharField("Имя", max_length=150, blank=True)
    surname = models.CharField("Фамилия", max_length=150, blank=True)
    middle_name = models.CharField("Отчество", max_length=150, blank=True)
    phone_number = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("Email", blank=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="doctors")
    experience_years = models.PositiveSmallIntegerField("Стаж", default=0)
    bio = models.TextField("Описание", blank=True)
    is_available = models.BooleanField("Доступен для записи", default=True)

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Slot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="slots")
    date_and_time = models.DateTimeField("Дата и время")
    is_available = models.BooleanField("Доступен", default=True)

    class Meta:
        verbose_name = "Слот приёма"
        verbose_name_plural = "Слоты приёма"
        ordering = ["date_and_time"]
        constraints = [
            models.UniqueConstraint(fields=["doctor", "date_and_time"], name="unique_doctor_date_and_time")
        ]

    def __str__(self):
        return f"{self.doctor} — {self.date_and_time:%d.%m.%Y %H:%M}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        CONFIRMED = "confirmed", "Подтверждена"
        COMPLETED = "completed", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments", null=True, blank=True)
    slot = models.OneToOneField(Slot, on_delete=models.PROTECT, related_name="appointment")
    patient_name = models.CharField("Имя пациента", max_length=180, blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments")
    starts_at = models.DateTimeField("Дата и время")
    complaint = models.TextField("Краткая жалоба", blank=True)
    description = models.TextField("Описание приёма", blank=True)
    diagnosis = models.TextField("Диагноз", blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["starts_at"]
        constraints = [
            models.UniqueConstraint(fields=["doctor", "starts_at"], name="unique_doctor_slot")
        ]

    def __str__(self):
        return f"{self.patient_name} — {self.doctor}"


class Medication(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medications", null=True, blank=True)
    title = models.CharField("Препарат", max_length=160)
    dosage = models.CharField("Дозировка", max_length=120)
    schedule = models.CharField("Расписание", max_length=180)
    next_intake_at = models.DateTimeField("Следующий прием", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Препарат"
        verbose_name_plural = "Препараты"

    def __str__(self):
        return self.title


class SupportRequest(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="support_requests", null=True, blank=True)
    name = models.CharField("Имя", max_length=120, blank=True)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Сообщение")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Обращение в поддержку"
        verbose_name_plural = "Обращения в поддержку"
        ordering = ["-created_at"]


class MedicalRecord(models.Model):
    class Category(models.TextChoices):
        EVENT = "event", "Событие"
        CERTIFICATE = "certificate", "Справка"
        LAB_RESULT = "lab_result", "Результат анализа"
        STUDY = "study", "Исследование"
        VISIT_PROTOCOL = "visit_protocol", "Протокол приёма"

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medical_records")
    category = models.CharField(max_length=24, choices=Category.choices)
    title = models.CharField("Название", max_length=220)
    summary = models.TextField("Описание", blank=True)
    occurred_at = models.DateTimeField("Дата события")
    doctor_name = models.CharField("Врач", max_length=180, blank=True)
    document_url = models.URLField("Ссылка на документ", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запись медкарты"
        verbose_name_plural = "Медкарта"
        ordering = ["-occurred_at"]

    def __str__(self):
        return self.title


class IntakeSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активен"
        COMPLETED = "completed", "Завершён"
        URGENT = "urgent", "Требует срочной помощи"

    class Urgency(models.TextChoices):
        LOW = "low", "Низкая"
        CONSULTATION = "consultation", "Нужна консультация"
        URGENT = "urgent", "Срочно"

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intake_sessions")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    urgency = models.CharField(max_length=16, choices=Urgency.choices, default=Urgency.LOW)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, related_name="intake_sessions")
    summary = models.TextField("Резюме анамнеза", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Сессия анамнеза"
        verbose_name_plural = "Сессии анамнеза"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Анамнез №{self.pk} — {self.patient}"


class IntakeMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Пациент"
        ASSISTANT = "assistant", "Ассистент"

    session = models.ForeignKey(IntakeSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=Role.choices)
    content = models.TextField("Сообщение")
    structured_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение анамнеза"
        verbose_name_plural = "Сообщения анамнеза"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:60]}"


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="prescription")
    recommendations = models.TextField("Рекомендации", blank=True)
    tests = models.TextField("Исследования", blank=True)
    analyses = models.TextField("Анализы", blank=True)

    class Meta:
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"

    def __str__(self):
        return f"Назначение к приёму №{self.appointment_id}"


class Certificate(models.Model):
    issuance_date = models.DateField("Дата выдачи")
    illness_start = models.DateField("Начало заболевания", null=True, blank=True)
    illness_end = models.DateField("Окончание заболевания", null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="certificates")
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    diagnosis = models.TextField("Диагноз", blank=True)
    notes = models.TextField("Примечания", blank=True)

    class Meta:
        verbose_name = "Справка"
        verbose_name_plural = "Справки"
        ordering = ["-issuance_date"]

    def __str__(self):
        return f"Справка №{self.pk} от {self.issuance_date:%d.%m.%Y}"


class Drug(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="drugs")
    name = models.CharField("Препарат", max_length=180)
    dose = models.DecimalField("Доза", max_digits=10, decimal_places=2)
    days = models.PositiveIntegerField("Дней курса")
    days_left = models.PositiveIntegerField("Дней осталось")

    class Meta:
        verbose_name = "Препарат в назначении"
        verbose_name_plural = "Препараты в назначениях"

    def __str__(self):
        return self.name


class Referral(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="referrals")
    issuance_date = models.DateField("Дата выдачи")
    expiration_date = models.DateField("Действительно до")

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"
        ordering = ["-issuance_date"]

    def __str__(self):
        return f"Направление №{self.pk}"
