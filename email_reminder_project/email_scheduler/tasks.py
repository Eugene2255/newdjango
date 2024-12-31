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
        

        subject = email_schedule.subject
        message = render_to_string('email_template.html', {
            'message': email_schedule.message,
        })


        email = EmailMessage(
            subject,
            message,
            'bruce847wayne@gmail.com',  
            [email_schedule.email]      
        )
        email.content_subtype = 'html'  
        

        email.send()

        email_schedule.status = 'Sent'
        email_schedule.save()

        logger.info(f"Email sent successfully to {email_schedule.email} for EmailSchedule ID {email_id}")


        if email_schedule.recurring:
            if email_schedule.recurring == 'Daily':
                email_schedule.send_date += timedelta(days=1)
            elif email_schedule.recurring == 'Weekly':
                email_schedule.send_date += timedelta(weeks=1)
            elif email_schedule.recurring == 'Monthly':
                email_schedule.send_date += timedelta(weeks=4)
            

            email_schedule.status = 'Pending'
            email_schedule.save()
            logger.info(f"Recurring email updated for next send: {email_schedule}")

    except EmailSchedule.DoesNotExist:
        logger.error(f"EmailSchedule not found: ID {email_id}")
    except Exception as e:
        logger.error(f"Error sending email {email_id}: {e}")
