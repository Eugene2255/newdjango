from django.urls import path
from .views import schedule_email, success_view
from . import views

urlpatterns = [
    path('', schedule_email, name='schedule_email'),
    path('success/', success_view, name='success'),
    path('dashboard/', views.email_dashboard, name='email_dashboard'),
    path('edit/<int:email_id>/', views.edit_email, name='edit_email'),
    path('delete/<int:email_id>/', views.delete_email, name='delete_email'),
]

