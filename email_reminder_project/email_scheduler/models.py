from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class EmailTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EmailSchedule(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        SENT = 'Sent', 'Sent'
        FAILED = 'Failed', 'Failed'

    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    send_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    recurring = models.CharField(max_length=10, choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], blank=True, null=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_next_send_date(self):
        if self.recurring == 'Daily':
            return self.send_date + timedelta(days=1)
        elif self.recurring == 'Weekly':
            return self.send_date + timedelta(weeks=1)
        elif self.recurring == 'Monthly':
            return self.send_date + timedelta(weeks=4)
        return None

    def __str__(self):
        return f"{self.subject} to {self.email}"