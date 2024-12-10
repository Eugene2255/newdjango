from django.db import models

class EmailSchedule(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    send_date = models.DateTimeField()

    def __str__(self):
        return f"{self.subject} to {self.email}"
