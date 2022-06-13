from rest_framework.exceptions import ValidationError
from users.models import User


def user_retrieve_by_email(email: str):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError({"detail": "Invalid email. No account has the provided email"})

    return user