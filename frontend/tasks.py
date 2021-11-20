from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from cv_generator.celery import app

from .tokens import account_activation_token

@app.task(name='send_verification_email')
def send_verification_email(user_pk):
    print('Sending email to user {}'.format(user_pk))

    user = User.objects.filter(id=user_pk).first()
    if user:

        message = get_template('frontend/auth/account_activation_email.html').render({
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'year' : date.today().year,
        })
        mail_subject = 'Activate your account.'
        to_email = user.email
        send_mail(mail_subject, "", settings.EMAIL_HOST_USER, [to_email], html_message = message,fail_silently=False)
