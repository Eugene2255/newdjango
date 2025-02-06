from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
import logging
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from operator import attrgetter
from .forms import EmailScheduleForm, EmailTemplateForm
from .models import EmailSchedule, EmailTemplate
from .tasks import send_email_task

logger = logging.getLogger(__name__)

def dynamic_template_preview(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    return JsonResponse({'subject': template.subject, 'message': template.message})

def email_dashboard(request):
    params = request.GET
    status = params.get('status', '')
    start_date = params.get('start_date', '')
    end_date = params.get('end_date', '')
    sort_by = params.get('sort_by', 'send_date')
    sort_order = params.get('sort_order', 'desc')
    page = params.get('page', '1')

    emails = list(EmailSchedule.objects.all())

    if status:
        emails = [e for e in emails if e.status == status]
    
    def parse_date(date_str):
        try:
            return timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    start = parse_date(start_date)
    end = parse_date(end_date)

    if start:
        emails = [e for e in emails if e.send_date and e.send_date.date() >= start]
    if end:
        emails = [e for e in emails if e.send_date and e.send_date.date() <= end]


    emails.sort(
        key=lambda x: getattr(x, sort_by) or '', 
        reverse=(sort_order == 'desc')
    )

    try:
        paginator = Paginator(emails, 10)
        page_obj = paginator.get_page(page) 
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        page_obj = []

    return render(request, 'email_dashboard.html', {
        'page_obj': page_obj,
        'status': status,
        'start_date': start,
        'end_date': end,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'total_emails': len(emails),
        'page_range': paginator.page_range if 'paginator' in locals() else range(1),
    })

def edit_email(request, email_id): 
    email_schedule = get_object_or_404(EmailSchedule, id=email_id)
    if email_schedule.status == 'Sent':
        return JsonResponse({"error": "Editing is not allowed for emails that have already been sent."}, status=403)

    if request.method == 'POST':
        form = EmailScheduleForm(request.POST, instance=email_schedule)
        if form.is_valid():
            updated_email = form.save(commit=False)
            template = form.cleaned_data.get('template')
            if template:
                updated_email.subject = template.subject
                updated_email.message = template.message
            if email_schedule.recurring != updated_email.recurring and updated_email.recurring:
                updated_email.send_date = updated_email.calculate_next_send_date()
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
            template = get_object_or_404(EmailTemplate, id=template_id)
            return JsonResponse({'subject': template.subject, 'message': template.message})
    return render(request, 'edit_email.html', {'form': form, 'email_schedule': email_schedule})

def delete_email(request, email_id):
    email_schedule = get_object_or_404(EmailSchedule, id=email_id)
    if email_schedule.status == 'Sent' and not email_schedule.recurring:
        return JsonResponse({"error": "Canceling is not allowed for emails that have already been sent."}, status=403)
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
            return redirect ('template_list')
    else:
        form = EmailTemplateForm()
    return render(request, 'create_template.html', {'form': form})

def edit_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect ('template_list')
    else:
        form = EmailTemplateForm(instance=template)
    return render(request, 'edit_template.html', {'form': form, 'template': template})

def preview_email(request, email_id):
    email = get_object_or_404(EmailSchedule, id=email_id)
    return JsonResponse({'subject': email.subject, 'message': email.message})

def delete_email_template(request, template_id):
    template = get_object_or_404(EmailTemplate, id=template_id)
    if request.method == 'POST':
        template.delete()
        return redirect ('template_list')
    return render(request, 'email_template_confirm_delete.html', {'template': template})

def fetch_email_statuses(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        emails = EmailSchedule.objects.values('id', 'status')
        return JsonResponse(list(emails), safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def schedule_email(request):
    if request.method == 'POST':
        form = EmailScheduleForm(request.POST)
        if form.is_valid():
            email_schedule = form.save(commit=False)
            template = form.cleaned_data.get('template')
            if template:
                email_schedule.subject = template.subject
                email_schedule.message = template.message
            email_schedule.status = 'Pending'
            email_schedule.save()
            send_email_task.apply_async((email_schedule.id,), eta=email_schedule.send_date)
            logger.info(f"Email scheduled: {email_schedule}")
            return redirect(reverse('email_dashboard'))
    else:
        cached_form = cache.get('schedule_email_form')
        if cached_form is None:
            form = EmailScheduleForm()
            cache.set('schedule_email_form', form, 60 * 10)  # Cache for 10 minutes
        else:
            form = cached_form
    return render(request, 'schedule_email.html', {'form': form})



