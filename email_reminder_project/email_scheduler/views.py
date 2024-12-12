from django.shortcuts import render, redirect
from .forms import EmailScheduleForm
from .tasks import send_email_task
from .models import EmailSchedule
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse

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


def success_view(request):
    return redirect('email_dashboard')

def email_dashboard(request):
    emails = EmailSchedule.objects.all().order_by('send_date')
    return render(request, 'email_dashboard.html', {'emails': emails})


def edit_email(request, email_id):
    email_schedule = get_object_or_404(EmailSchedule, id=email_id)
    if email_schedule.status != 'unsent':
        return HttpResponse("Editing is not allowed.", status=403)
    if request.method == 'POST':
        form = EmailScheduleForm(request.POST, instance=email_schedule)
        if form.is_valid():
            form.save()
            return redirect('email_dashboard')
    else:
        form = EmailScheduleForm(instance=email_schedule)
    return render(request, 'edit_email.html', {'form': form})

def delete_email(request, email_id):
    email_schedule = get_object_or_404(EmailSchedule, id=email_id)
    if email_schedule.status != 'unsent':
        return HttpResponse("Canceling is not allowed.", status=403)
    if request.method == 'POST':
        email_schedule.status = 'canceled'
        email_schedule.save()
        return redirect('email_dashboard')
    return render(request, 'confirm_delete.html', {'email': email_schedule})

