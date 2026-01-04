import json
import random
from datetime import timedelta
from urllib import parse, request

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import UserOTP

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
OTP_TTL_MINUTES = 10


def _generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def _verify_recaptcha(token: str, remote_ip: str | None) -> tuple[bool, str]:
    method_name = "_verify_recaptcha"
    if not token:
        return False, "Missing reCAPTCHA token."
    if not settings.RECAPTCHA_SECRET_KEY:
        return False, "Missing reCAPTCHA secret key."

    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    data = parse.urlencode(payload).encode("utf-8")
    req = request.Request(RECAPTCHA_VERIFY_URL, data=data)
    try:
        with request.urlopen(req, timeout=6) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False, "reCAPTCHA verification failed."

    if not result.get("success"):
        return False, "reCAPTCHA rejected."

    if result.get("action") and result.get("action") != "signup":
        return False, "Invalid reCAPTCHA action."

    score = float(result.get("score", 0))
    if settings.DEBUG:
        print(
            f"{method_name} reCAPTCHA score={score} threshold={settings.RECAPTCHA_THRESHOLD}"
        )
    if score < settings.RECAPTCHA_THRESHOLD:
        return False, "reCAPTCHA score too low."

    return True, ""


def _send_otp_email(email: str, code: str, verify_link: str) -> None:
    subject = "Your Book verification code"
    message = (
        "Use this code to verify your account:\n\n"
        f"{code}\n\n"
        f"It expires in {OTP_TTL_MINUTES} minutes.\n\n"
        f"Verify directly with this link:\n{verify_link}"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        if not email:
            email = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password", "")
        token = request.POST.get("recaptcha_token", "")

        if not name or not email or not password:
            messages.error(request, "Please fill in all fields.")
            return redirect("User:signup")

        ok, error = _verify_recaptcha(token, request.META.get("REMOTE_ADDR"))
        if not ok:
            messages.error(request, error)
            return redirect("User:signup")

        User = get_user_model()
        user = User.objects.filter(username=email).first()
        if user and user.is_active:
            messages.error(request, "An account with this email already exists.")
            return redirect("User:signup")

        if not user:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                is_active=False,
            )
        else:
            user.first_name = name
            user.email = email
            user.set_password(password)
            user.save(update_fields=["first_name", "email", "password"])

        UserOTP.objects.filter(user=user, used=False).update(used=True)
        otp = _generate_otp()
        UserOTP.objects.create(
            user=user,
            code=otp,
            expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
        )

        verify_url = request.build_absolute_uri(
            reverse("User:verify_otp") + f"?uid={user.id}&code={otp}"
        )
        _send_otp_email(email, otp, verify_url)
        request.session["pending_user_id"] = user.id
        return redirect("User:verify_otp")

    filtered_messages = []
    for message in messages.get_messages(request):
        if "Successfully signed in as" in str(message):
            continue
        filtered_messages.append(message)
    return render(
        request,
        "User/signup.html",
        {
            "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
            "signup_messages": filtered_messages,
        },
    )


@require_http_methods(["GET", "POST"])
def verify_otp(request):
    User = get_user_model()
    user = None
    code = request.GET.get("code", "").strip()
    uid = request.GET.get("uid", "").strip()
    if code and uid.isdigit():
        user = User.objects.filter(id=int(uid)).first()
        if user:
            otp = UserOTP.objects.filter(
                user=user,
                used=False,
                expires_at__gt=timezone.now(),
            ).first()
            if otp and otp.code == code:
                otp.used = True
                otp.save(update_fields=["used"])
                user.is_active = True
                user.save(update_fields=["is_active"])
                login(request, user)
                request.session.pop("pending_user_id", None)
                return redirect("/")
            messages.error(request, "Invalid or expired link.")

    if not user:
        user_id = request.session.get("pending_user_id")
        if not user_id:
            messages.error(request, "Start signup again.")
            return redirect("User:signup")
        user = User.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, "Start signup again.")
            return redirect("User:signup")

    if request.method == "POST":
        code = request.POST.get("otp", "").strip()
        otp = UserOTP.objects.filter(
            user=user,
            used=False,
            expires_at__gt=timezone.now(),
        ).first()

        if not otp or otp.code != code:
            messages.error(request, "Invalid or expired code.")
            return redirect("User:verify_otp")

        otp.used = True
        otp.save(update_fields=["used"])
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        request.session.pop("pending_user_id", None)
        return redirect("/")

    return render(request, "User/verify_otp.html", {"email": user.email})
