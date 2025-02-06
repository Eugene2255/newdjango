from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import EmailSchedule
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

@shared_task
def send_email_task(email_id):
    try:
        email_schedule = EmailSchedule.objects.get(id=email_id)
        
        # Create email message
        email = EmailMessage(
            subject=email_schedule.subject,
            body=render_to_string('email_template.html', {'message': email_schedule.message}),
            from_email='bruce847wayne@gmail.com',
            to=[email_schedule.email],
        )
        
        # Set content subtype after creation
        email.content_subtype = 'html'
        email.send()

        # Update status
        email_schedule.status = 'Sent'
        
        # Handle recurring emails
        if email_schedule.recurring:
            email_schedule.send_date = email_schedule.calculate_next_send_date()
            email_schedule.status = 'Pending'
            
        email_schedule.save()
        logger.info(f"Email {email_id} processed successfully")

    except EmailSchedule.DoesNotExist:
        logger.error(f"EmailSchedule not found: ID {email_id}")
    except Exception as e:
        logger.error(f"Error sending email {email_id}: {e}", exc_info=True)
        EmailSchedule.objects.filter(id=email_id).update(status='Failed')
