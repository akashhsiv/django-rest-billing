from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed,ValidationError
import secrets
import string
from .models import Users


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'username', 'user_type']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    expected_user_type = None 

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_active:
            raise AuthenticationFailed("Your Account is deactivated. Please contact support.")

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

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)