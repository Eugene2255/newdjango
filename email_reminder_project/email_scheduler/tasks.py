from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import EmailSchedule

@shared_task
def send_email_task(email_id):
    email_schedule = EmailSchedule.objects.get(id=email_id)
    subject = email_schedule.subject
    message = render_to_string('email_template.html', {
        'message': email_schedule.message,
    })
    email = EmailMessage(subject, message, 'bruce847wayne@gmail.com', [email_schedule.email])
    email.content_subtype = 'html'
    email.send()
