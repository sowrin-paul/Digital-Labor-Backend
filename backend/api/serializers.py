from rest_framework import serializers
from .models import User, Worker, Job
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmPassword = serializers.CharField(write_only=True, required=True)
    is_worker = serializers.BooleanField(required=True)
    is_customer = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirmPassword', 'is_worker', 'is_customer')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmPassword']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if not (attrs['is_worker'] or attrs['is_customer']):
            raise serializers.ValidationError("User must be either a worker or customer.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmPassword')
        is_worker = validated_data['is_worker']
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_worker=is_worker,
            is_customer=validated_data['is_customer'],
            is_active=not is_worker,
        )
        return user

class JobSerializer(serializers.ModelSerializer):
    assigned_worker = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'budget', 'status', 'assigned_worker']

    def get_assigned_worker(self, obj):
        if obj.assigned_worker:
            return {
                "id": obj.assigned_worker.id,
                "username": obj.assigned_worker.user.username,
                "skills": obj.assigned_worker.skills,
                "experience": obj.assigned_worker.experience,
                "location": obj.assigned_worker.location,
            }
        return None