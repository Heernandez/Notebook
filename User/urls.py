from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "User"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path(
        "password-reset/",
        TemplateView.as_view(template_name="User/password_reset.html"),
        name="password_reset",
    ),
]
