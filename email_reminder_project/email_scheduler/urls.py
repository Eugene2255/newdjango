from django.urls import path
from .views import schedule_email, success_view

urlpatterns = [
    path('', schedule_email, name='schedule_email'),
    path('success/', success_view, name='success'),
]
