from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from django.core.cache import cache
from functools import lru_cache

class EmailTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @lru_cache(maxsize=128)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.__str__.cache_clear() 
        super().save(*args, **kwargs)


class EmailSchedule(models.Model):

    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    send_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Sent', 'Sent'), ('Failed', 'Failed'), ('Canceled', 'Canceled')],default='Pending')
    recurring = models.CharField(max_length=10, choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], blank=True, null=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Default ordering
        indexes = [
            models.Index(fields=['send_date']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    RECURRING_INTERVALS = {
        'Daily': lambda date: date + timedelta(days=1),
        'Weekly': lambda date: date + timedelta(weeks=1),
        'Monthly': lambda date: date + timedelta(weeks=4),
    }

    def calculate_next_send_date(self):
        if not self.recurring:
            return None
        calculate = self.RECURRING_INTERVALS.get(self.recurring)
        return calculate(self.send_date) if calculate else None

    def __str__(self):
        return f"{self.subject} to {self.email}"