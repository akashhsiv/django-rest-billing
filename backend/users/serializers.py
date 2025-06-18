from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed, ValidationError
import secrets
import string
from .models import Users
from rest_framework import serializers
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'username', 'user_type', 'mobile', 'is_first_login', 'last_login']


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'username', 'user_type', "mobile"]

    def create(self, validated_data):
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(10))

        user = Users(
            email=validated_data['email'],
            username=validated_data['username'],
            user_type=validated_data.get('user_type', 'cashier'),
            mobile=validated_data.get('mobile', None),
            is_first_login=True,
        )
        user.set_password(temp_password)
        user.save()

        self._temp_password = temp_password
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    expected_user_type = None

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_active:
            raise AuthenticationFailed(
                "Your Account is deactivated. Please contact support.")

        if user.is_first_login:
            raise ValidationError({
                "detail": "Temporary password used. Please reset your password before continuing.",
                "first_login": True,
                "email": user.email
            })

        if self.expected_user_type:
            if self.user.user_type != self.expected_user_type:
                raise AuthenticationFailed(
                    detail=f"Only {self.expected_user_type} users can log in here.",
                    code="authorization"
                )

        data['message'] = 'You have logged in successfully'
        data['user_id'] = user.id
        data['user_type'] = user.user_type

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6) 
    old_password = serializers.CharField( 
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp')
        old_password = data.get('old_password') # Get old_password from data
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        user = Users.objects.filter(email=email, reset_password_otp=otp_code).first()

        if not user:
            raise serializers.ValidationError({"detail": _("Invalid email or OTP.")})

        self.context['user'] = user
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": _("Current password provided is incorrect.")})
        if new_password != confirm_password:
            raise serializers.ValidationError({"new_password": _("New passwords do not match.")})
        try:
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})

        return data

    def save(self, **kwargs):
        user = self.context.get('user')
        new_password = self.validated_data['new_password']

        if user:
            user.set_password(new_password)
            user.reset_password_otp = None 
            user.is_first_login = False
            user.save()
            return user
        return None 

# serializers.py
class ConfirmOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=4, max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        user = Users.objects.filter(email=email, reset_password_otp=otp_code).first()

        if not user:
            raise serializers.ValidationError({"detail": _("Invalid email or OTP.")})

        self.context['user'] = user
        
        if new_password != confirm_password:
            raise serializers.ValidationError({"new_password": _("New passwords do not match.")})
        try:
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})

        return data
    
    def save(self, **kwargs):
        user = self.context.get('user')
        new_password = self.validated_data['new_password']

        if user:
            user.set_password(new_password)
            user.reset_password_otp = None 
            user.is_first_login = False
            user.save()
            return user
        return None 
