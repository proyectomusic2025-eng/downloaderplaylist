from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from pathlib import Path
def send_license_email(to_email, subject, license_str, user=None, download_url=None):
    context = {'user': user, 'download_url': download_url}
    body = render_to_string('downloader/emails/license_email.txt', context)
    email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [to_email])
    email.attach('license.lic', license_str, 'text/plain')
    email.send(fail_silently=False)
