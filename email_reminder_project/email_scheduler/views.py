from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmailScheduleForm
from .models import EmailSchedule, EmailTemplate
from .tasks import send_email_task
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import timedelta
from .forms import EmailTemplateForm
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def schedule_email(request):
    templates = EmailTemplate.objects.all()
    if request.method == 'POST':
        form = EmailScheduleForm(request.POST)
        if form.is_valid():
            email_schedule = form.save(commit=False)
            template = form.cleaned_data.get('template')
            if template:
                email_schedule.subject = template.subject
                email_schedule.message = template.message
            email_schedule.save()
            send_email_task.apply_async((email_schedule.id,), eta=email_schedule.send_date)
            logger.info(f"Email scheduled: {email_schedule}")
            return redirect('email_dashboard')
    else:
        form = EmailScheduleForm()

    return render(request, 'schedule_email.html', {'form': form, 'templates': templates})


def dynamic_template_preview(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    return JsonResponse({'subject': template.subject, 'message': template.message})


def email_dashboard(request):
    emails = EmailSchedule.objects.all()

    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if status:
        emails = emails.filter(status=status)

    if start_date:
        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    if end_date:
        try:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None  


    if start_date and end_date:
        emails = emails.filter(send_date__range=[start_date, end_date])


    sort_by = request.GET.get('sort_by', 'send_date')
    sort_order = request.GET.get('sort_order', 'asc')
    if sort_order == 'desc':
        sort_by = f"-{sort_by}"

    valid_sort_fields = ['send_date', 'status', 'subject', 'email']
    if sort_by.lstrip('-') not in valid_sort_fields:
        sort_by = 'send_date' 
    
    emails = emails.order_by(sort_by)

    context = {
        'emails': emails,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by.lstrip('-'),
        'sort_order': sort_order,
    }

    return render(request, 'email_dashboard.html', context)



def edit_email(request, email_id):
    email_schedule = get_object_or_404(EmailSchedule, id=email_id)

    if email_schedule.status == 'Sent':
        return HttpResponse("Editing is not allowed for emails that have already been sent.", status=403)

    if request.method == 'POST':
        form = EmailScheduleForm(request.POST, instance=email_schedule)
        if form.is_valid():
            updated_email = form.save(commit=False)

            if 'template' in form.cleaned_data and form.cleaned_data['template']:
                selected_template = form.cleaned_data['template']
                updated_email.subject = selected_template.subject
                updated_email.message = selected_template.message

            if email_schedule.recurring != updated_email.recurring and updated_email.recurring:
                if updated_email.recurring == 'Daily':
                    updated_email.send_date += timedelta(days=1)
                elif updated_email.recurring == 'Weekly':
                    updated_email.send_date += timedelta(weeks=1)
                elif updated_email.recurring == 'Monthly':
                    updated_email.send_date += timedelta(weeks=4)

            updated_email.status = 'Pending'
            updated_email.save()

            send_email_task.apply_async((updated_email.id,), eta=updated_email.send_date)
            logger.info(f"Email updated: {updated_email}")
            return redirect('email_dashboard')
    else:
        form = EmailScheduleForm(instance=email_schedule)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template_id = request.GET.get('template_id')
        if template_id:
            try:
                template = EmailTemplate.objects.get(id=template_id)
                return JsonResponse({
                    'subject': template.subject,
                    'message': template.message
                })
            except EmailTemplate.DoesNotExist:
                return JsonResponse({'error': 'Template not found'}, status=404)

    return render(request, 'edit_email.html', {'form': form, 'email_schedule': email_schedule})


def delete_email(request, email_id):
    email_schedule = get_object_or_404(EmailSchedule, id=email_id)
    
    if email_schedule.status == 'Sent' and not email_schedule.recurring:
        return HttpResponse("Canceling is not allowed for emails that have already been sent.", status=403)
    
    if request.method == 'POST':
        email_schedule.status = 'Canceled' 
        email_schedule.save()
        return redirect('email_dashboard')

    return render(request, 'confirm_delete.html', {'email': email_schedule})



def template_list(request):
    templates = EmailTemplate.objects.all()
    return render(request, 'template_list.html', {'templates': templates})

def create_template(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('template_list')
    else:
        form = EmailTemplateForm()
    return render(request, 'create_template.html', {'form': form})

    
def edit_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect('template_list')
    else:
        form = EmailTemplateForm(instance=template)
    return render(request, 'edit_template.html', {'form': form, 'template': template})


def preview_email(request, email_id):
    email = get_object_or_404(EmailSchedule, id=email_id)
    return JsonResponse({
        'subject': email.subject,
        'message': email.message,
    })


def delete_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    

    if request.method == 'POST':
        template.delete()
        return redirect('template_list') 
    
    return render(request, 'email_template_confirm_delete.html', {'template': template})


def fetch_email_statuses(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        emails = EmailSchedule.objects.values('id', 'status')
        return JsonResponse(list(emails), safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)
