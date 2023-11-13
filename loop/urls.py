# loop/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('trigger_report/', trigger_report_view, name='trigger_report'),
    path('get_report/<str:report_id>/', get_report, name='get_report'),
]
