from django import forms
from django.utils import timezone
from .models import EmailSchedule, EmailTemplate

class EmailScheduleForm(forms.ModelForm):
    send_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    template = forms.ModelChoiceField(
        queryset=EmailTemplate.objects.all(),
        required=False,
        help_text="Select a template",
    )

    class Meta:
        model = EmailSchedule
        fields = ['email', 'subject', 'message', 'send_date', 'recurring', 'template']

    def clean_send_date(self):
        send_date = self.cleaned_data['send_date']
        if send_date < timezone.now():
            raise forms.ValidationError("The send date cannot be in the past.")
        return send_date

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'message']