from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Token

class CustomTokenAuthentication(TokenAuthentication):
    model = Token
    
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')
            
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')
            
        # Update token last used time
        token.last_used = timezone.now()
        token.save(update_fields=['last_used'])
        
        return (token.user, token)
