import datetime
import os
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_otp_email(to_email, otp_code, user_name):
    subject = "Your LineUp OTP Code"
    from_email = settings.DEFAULT_FROM_EMAIL

    context = {
        "otp_code": otp_code,
        "user_name": user_name,
        "year": datetime.datetime.now().year,
    }

    html_content = render_to_string("otp_email_template.html", context)

    email = EmailMultiAlternatives(subject, "", from_email, [to_email])
    email.attach_alternative(html_content, "text/html")

    logo_path = os.path.join("static", "images", "Full Logo - light.png")
    with open(logo_path, "rb") as f:
        logo = MIMEImage(f.read(), _subtype="svg+xml")
        logo.add_header("Content-ID", "<logo>")
        logo.add_header("Content-Disposition", "inline", filename="logo.svg")
        email.attach(logo)

    email.send()
