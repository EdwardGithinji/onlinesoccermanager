from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework.exceptions import ValidationError
from typing import Optional
from league.services import generate_team_with_players
# from league.tasks import create_team_with_players_on_user_registration
from users.models import User


@transaction.atomic
def user_create(
    email: str,
    password1: str,
    password2: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
    ) -> User:

    if password1 != password2:
        raise ValidationError({"detail": "password1 and password2 do not match"})
    if len(password1) < 8:
        raise ValidationError({"detail": "password must be atleast 8 characters in length"})
    if User.objects.filter(email=email).exists():
        raise ValidationError({"detail": "User with provided email already exists"})
    user = User.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password1
    )
    generate_team_with_players(user)
    # transaction.on_commit(lambda: create_team_with_players_on_user_registration.delay(user.id))
    return user


def user_login(email: str, password: str, request):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError({"detail": "Invalid email. No account has the provided email"})
    user = authenticate(request=request, email=email, password=password)
    if user is None:
        raise
    return user
