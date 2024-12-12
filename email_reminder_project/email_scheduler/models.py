from django.db import models

class EmailSchedule(models.Model):
    STATUS_CHOICES = [
        ('unsent', 'Unsent'),
        ('sent', 'Sent'),
        ('canceled', 'Canceled'),
    ]
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    send_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unsent') 

    def __str__(self):
        return f"{self.subject} to {self.email}"

