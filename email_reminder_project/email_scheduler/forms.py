from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import EmailSchedule

class EmailScheduleForm(forms.ModelForm):
    send_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = EmailSchedule
        fields = ['email', 'subject', 'message', 'send_date']

    def clean_email(self):
        email = self.cleaned_data['email']
        if '@' not in email:
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean_send_date(self):
        send_date = self.cleaned_data['send_date']
        if send_date < timezone.now():
            raise ValidationError("The send date cannot be in the past.")
        return send_date
