from django.urls import path
from users.views import RegisterUserView, UserLoginView


urlpatterns = [
    path('registration/', RegisterUserView.as_view()),
    path('login/', UserLoginView.as_view()),
]
