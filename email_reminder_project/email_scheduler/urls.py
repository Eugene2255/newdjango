from django.urls import path
from .views import schedule_email, preview_email, delete_email_template
from . import views

urlpatterns = [
    path('', views.email_dashboard, name='email_dashboard'),
    path('schedule/', schedule_email, name='schedule_email'),
    path('edit/<int:email_id>/', views.edit_email, name='edit_email'),
    path('delete/<int:email_id>/', views.delete_email, name='delete_email'),
    path('preview_email/<int:email_id>/', views.preview_email, name='preview_email'),
    path('dynamic_template_preview/<int:template_id>/', views.dynamic_template_preview, name='dynamic_template_preview'),
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/edit/<int:template_id>/', views.edit_template, name='edit_template'),
    path('delete_template/<int:template_id>/', delete_email_template, name='delete_email_template'),
    path('fetch_statuses/', views.fetch_email_statuses, name='fetch_statuses'),

]

