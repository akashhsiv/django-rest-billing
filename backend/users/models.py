from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from datetime import *
from django.core.validators import RegexValidator

indian_mobile_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9."
)

class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, username, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('user_type', "super_admin")
        other_fields.setdefault('is_first_login', False)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, username, password, **other_fields)

    def create_user(self, email, username, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        if not other_fields.get('mobile'):
            raise ValueError(_('You must provide a mobile number'))

        other_fields.setdefault('is_first_login', False)  

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user
    
class Users(AbstractBaseUser, PermissionsMixin):
    is_first_login = models.BooleanField(default=True)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=255, blank=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    user_type = models.CharField(max_length=20, choices=[('super_admin', 'Super Admin'), ('manager', 'Manager'), ('cashier', 'Cashier')])
    mobile = models.CharField(
        max_length=10,
        unique=True,
        validators=[indian_mobile_validator]
    )
    reset_password_otp = models.CharField(max_length=4, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile']

    def __str__(self):
        return self.email