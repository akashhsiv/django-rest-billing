import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def generate_otp():
    """Generate a random OTP of specified length."""
    return ''.join(random.choices(string.digits, k=settings.OTP_LENGTH))

def send_otp_email(email, otp):
    """Send OTP to the user's email."""
    if settings.OTP_TEST_MODE:
        print(f"OTP for {email}: {otp}")
        return True
    
    subject = 'Your Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def store_otp(email, otp):
    """Store OTP in cache with expiration."""
    cache_key = f'otp_{email}'
    cache.set(cache_key, otp, timeout=settings.OTP_EXPIRY_MINUTES * 60)

def verify_otp(email, otp):
    """Verify if the provided OTP is correct and not expired."""
    cache_key = f'otp_{email}'
    stored_otp = cache.get(cache_key)
    
    if stored_otp and stored_otp == otp:
        cache.delete(cache_key)  # Delete OTP after successful verification
        return True
    return False

def generate_reset_token():
    """Generate a secure token for password reset."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))




# Set up logging
logger = logging.getLogger(__name__)
def send_temporary_password_email(email, temp_password):
    """
    Send a temporary password to the user's email.

    Args:
        email (str): Recipient's email address
        temp_password (str): The temporary password to send
    """
    subject = 'Your Temporary Login Password'
    
    try:
        # Render HTML content
        html_content =  render_to_string('users/temp_password.html',
 {
            'temp_password': temp_password,
        })
        
        # Create text version (for non-HTML email clients)
        text_content = strip_tags(html_content)
        
        # Create email
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        
        # Attach HTML content
        email_message.attach_alternative(html_content, "text/html")
        
        # Send email
        email_message.send()
        logger.info(f"temp_password email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending temp_password email to {email}: {str(e)}")
        # For debugging purposes, print the OTP to console in development
        if settings.DEBUG:
            print(f"DEBUG - temp_password for {email}: {temp_password}")
        return False