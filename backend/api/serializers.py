from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Appointment, Doctor, MedicalRecord, Medication, PatientProfile, Specialty, SupportRequest


class PatientProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", required=False, allow_blank=True)
    full_name = serializers.SerializerMethodField()
    avatar_background_url = serializers.SerializerMethodField()
    avatar_dino_url = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = [
            "id", "email", "first_name", "last_name", "middle_name", "full_name", "phone", "birth_date",
            "policy_number", "role", "avatar_background", "avatar_dino",
            "avatar_background_url", "avatar_dino_url",
        ]
        read_only_fields = ["role", "avatar_background", "avatar_dino"]

    def get_full_name(self, obj):
        return " ".join(filter(None, [obj.user.first_name, obj.middle_name, obj.user.last_name])) or obj.user.email

    def get_avatar_background_url(self, obj):
        return f"/avatars/background_{obj.avatar_background}.png"

    def get_avatar_dino_url(self, obj):
        return f"/avatars/dino_{obj.avatar_dino}.png"

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if user_data:
            for field in ("first_name", "last_name"):
                if field in user_data:
                    setattr(instance.user, field, user_data[field])
            instance.user.save(update_fields=list(user_data.keys()))
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    middle_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(username=normalized).exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return normalized

    def create(self, validated_data):
        phone = validated_data.pop("phone")
        middle_name = validated_data.pop("middle_name", "")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User.objects.create_user(username=email, email=email, password=password, **validated_data)
        profile = user.patient_profile
        profile.phone = phone
        profile.middle_name = middle_name
        profile.save(update_fields=["phone", "middle_name"])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"].strip().lower(), password=attrs["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError("Неверный email или пароль.")
        attrs["user"] = user
        return attrs


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = "__all__"


class DoctorSerializer(serializers.ModelSerializer):
    specialty_name = serializers.CharField(source="specialty.name", read_only=True)

    class Meta:
        model = Doctor
        fields = ["id", "full_name", "name", "surname", "middle_name", "phone_number", "email", "specialty", "specialty_name", "experience_years", "bio", "is_available"]


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.full_name", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ["patient", "patient_name", "phone", "doctor", "starts_at", "status", "created_at"]

    def validate(self, attrs):
        slot = attrs.get("slot")
        if self.instance is None and not slot:
            raise serializers.ValidationError({"slot": "Выберите время приёма."})
        if slot and (not slot.is_available or hasattr(slot, "appointment")):
            raise serializers.ValidationError({"slot": "Это время уже недоступно."})
        return attrs


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = "__all__"
        read_only_fields = ["patient"]


class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = ["id", "name", "email", "message", "created_at"]
        read_only_fields = ["name", "email", "created_at"]


class MedicalRecordSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ["id", "category", "category_label", "title", "summary", "occurred_at", "doctor_name", "document_url"]


class IntakeTurnSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000, trim_whitespace=True)
    session_id = serializers.IntegerField(required=False, min_value=1)
