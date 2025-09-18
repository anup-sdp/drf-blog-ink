# users/serializers.py:
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser
MAX_IMAGE_KB = 500

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer used for user detail and current_user endpoints.
    is_active is read-only for normal users and editable for staff.
    """
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    full_name = serializers.ReadOnlyField() 
    class Meta:
        model = CustomUser
        fields = ["id","username","email","first_name","last_name", "full_name", "phone_number","location","bio","profile_picture","is_active","is_staff","is_subscribed"]  # Add is_subscribed here
        read_only_fields = ["id"]
    def get_fields(self):
        """
        Make is_active, is_staff, and is_subscribed editable only for staff users.     
        """
        fields = super().get_fields()
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated and user.is_staff):
            fields["is_active"].read_only = True
            fields["is_staff"].read_only = True
            fields["is_subscribed"].read_only = True  # Add this line
        return fields
    def update(self, instance, validated_data):
        # default ModelSerializer.update works, but keep explicit to avoid surprises with file fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def validate_profile_picture(self, value):
        max_kb = 500
        if value and value.size > max_kb * 1024:
            raise serializers.ValidationError(f'Profile image must be <= {max_kb} KB.')
        return value

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    For registration endpoint. Used by Djoser as 'user_create'.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={"input_type": "password"})                                     
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "phone_number", "location", "bio", "profile_picture"]  # Don't add is_subscribed here
        extra_kwargs = {"username": {"required": True},"email": {"required": True},}
        
    def validate_email(self, value):        
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    def validate_profile_picture(self, value):
        max_kb = 500
        if value and value.size > max_kb * 1024:
            raise serializers.ValidationError(f'Profile image must be <= {max_kb} KB.')
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        # get djoser config safely
        dj_settings = getattr(settings, "DJOSER", {}) or {}
        send_activation = dj_settings.get("SEND_ACTIVATION_EMAIL", False)
        
        user_kwargs = validated_data.copy()  # may contain profile_picture and other fields
        if send_activation:            
            user = CustomUser.objects.create_user(**user_kwargs, password=password, is_active=False)
        else:
            user = CustomUser.objects.create_user(**user_kwargs, password=password)
        user.save()
        return user