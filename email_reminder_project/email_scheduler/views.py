from django.shortcuts import render, redirect
from .forms import EmailScheduleForm
from .tasks import send_email_task

def schedule_email(request):
    if request.method == 'POST':
        form = EmailScheduleForm(request.POST)
        if form.is_valid():
            email_schedule = form.save()
            send_email_task.apply_async(
                (email_schedule.id,), eta=email_schedule.send_date
            )
            return redirect('success') 
    else:
        form = EmailScheduleForm()
    return render(request, 'schedule_email.html', {'form': form})

from django.http import HttpResponse

def success_view(request):
    return HttpResponse("Email scheduled successfully!")
