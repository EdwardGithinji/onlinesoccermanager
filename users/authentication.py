import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model


class CustomJWTAuthentication(BaseAuthentication):
    '''
        custom authentication class for DRF and JWT
        https://github.com/encode/django-rest-framework/blob/master/rest_framework/authentication.py
    '''

    def authenticate(self, request):

        User = get_user_model()
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return None
        auth_header_list = authorization_header.split(' ')
        try:
            access_token = auth_header_list[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('signature has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding signature')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')
        if auth_header_list[0] != settings.JWT_AUTH_HEADER_PREFIX:
            raise exceptions.AuthenticationFailed('Invalid token prefix')

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        return (user, None)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        # dummy WWW-Authenticate return for 401 errors
        return f'Bearer realm="{request.build_absolute_uri("/api/auth/login/")}"'