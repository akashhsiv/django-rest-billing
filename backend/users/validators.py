from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class ContainsUppercaseValidator:
    """
    Validates that the password contains at least one uppercase letter.
    """
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("Your password must contain at least one uppercase letter."),
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter.")

class ContainsLowercaseValidator:
    """
    Validates that the password contains at least one lowercase letter.
    """
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("Your password must contain at least one lowercase letter."),
                code='password_no_lowercase',
            )

    def get_help_text(self):
        return _("Your password must contain at least one lowercase letter.")

class ContainsSymbolValidator:
    """
    Validates that the password contains at least one special character.
    """
    def validate(self, password, user=None):
        # This regex matches any character that is NOT a letter, number, or underscore.
        # Adjust if you have a specific set of allowed symbols.
        if not re.findall(r'[^0-9a-zA-Z\s]', password):
            raise ValidationError(
                _("Your password must contain at least one special character."),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _("Your password must contain at least one special character.")