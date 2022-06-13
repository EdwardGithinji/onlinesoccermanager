from django.contrib.auth import authenticate

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from users.selectors import user_retrieve_by_email
from users.services import user_create


class RegisterUserView(APIView):

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField(required=False, allow_null=True)
        last_name = serializers.CharField(required=False, allow_null=True)
        password1 = serializers.CharField()
        password2 = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField(allow_null=True)
        last_name = serializers.CharField(allow_null=True)

    def post(self, request):
        user_registration_serializer = self.InputSerializer(data=request.data)
        user_registration_serializer.is_valid(raise_exception=True)
        user = user_create(**user_registration_serializer.validated_data)
        response_data = self.OutputSerializer(user).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        class UserDetailSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            email = serializers.EmailField()
            first_name = serializers.CharField(allow_null=True)
            last_name = serializers.CharField(allow_null=True)

        token = serializers.CharField()
        user = serializers.SerializerMethodField()

        def get_user(self, user):
            return self.UserDetailSerializer(user).data

    def post(self, request):
        user_login_serializer = self.InputSerializer(data=request.data)
        user_login_serializer.is_valid(raise_exception=True)
        request_data = user_login_serializer.validated_data
        email = request_data.get('email')
        password = request_data.get('password')
        user = user_retrieve_by_email(email)
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        response_data = self.OutputSerializer(user).data
        return Response(response_data, status=status.HTTP_201_CREATED)
