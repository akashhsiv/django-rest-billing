import getpass
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password as django_validate_password

class Command(BaseCommand):
    help = 'Creates a superuser (admin) account interactively, prompting for email, username, and password.'

    def handle(self, *args, **options):
        User = get_user_model() # Get the currently active user model

        self.stdout.write(self.style.NOTICE("--- Create Admin Account ---"))

        # --- Get Username ---
        username = ''
        while not username:
            username = input(self.style.SUCCESS("Enter Username: ")).strip()
            if not username:
                self.stderr.write(self.style.ERROR("Username cannot be empty. Please try again."))
            elif User.objects.filter(username=username).exists():
                self.stderr.write(self.style.ERROR(f"A user with username '{username}' already exists. Please choose a different username."))
                username = '' # Clear to loop again

        # --- Get Email ---
        email = ''
        while not email:
            email = input(self.style.SUCCESS("Enter Email: ")).strip()
            if not email:
                self.stderr.write(self.style.ERROR("Email cannot be empty. Please try again."))
            else:
                try:
                    validate_email(email)
                except ValidationError:
                    self.stderr.write(self.style.ERROR("Invalid email format. Please try again."))
                    email = '' # Clear to loop again
                else:
                    if User.objects.filter(email=email).exists():
                        self.stderr.write(self.style.ERROR(f"A user with email '{email}' already exists. Please use a different email."))
                        email = '' # Clear to loop again

        # --- Get Password ---
        password = ''
        password_confirm = 'a' # Initialize differently to enter loop
        while password != password_confirm or not password:
            if password and password != password_confirm:
                self.stderr.write(self.style.ERROR("Passwords do not match. Please try again."))
            elif not password and password_confirm != 'a': # Only show if not first attempt
                self.stderr.write(self.style.ERROR("Password cannot be empty. Please try again."))

            password = getpass.getpass(self.style.SUCCESS("Enter Password: "))
            password_confirm = getpass.getpass(self.style.SUCCESS("Confirm Password: "))

            if password and password == password_confirm:
                try:
                    # Apply Django's AUTH_PASSWORD_VALIDATORS defined in settings.py
                    django_validate_password(password, user=None)
                except ValidationError as e:
                    for message in e.messages:
                        self.stderr.write(self.style.ERROR(f"Password error: {message}"))
                    password = '' # Clear to force re-entry
                    password_confirm = 'a'
                else:
                    break # Passwords match and pass validation
            elif not password: # Catches if initial password is empty
                self.stderr.write(self.style.ERROR("Password cannot be empty."))
                password = ''
                password_confirm = 'a'


        self.stdout.write(self.style.NOTICE("\nCreating admin account..."))
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f"\nAdmin account '{username}' created successfully!"))
        except Exception as e:
            raise CommandError(f"Error creating admin account: {e}")