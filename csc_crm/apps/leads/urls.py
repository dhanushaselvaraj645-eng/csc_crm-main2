from django.urls import path
from .views import *

urlpatterns = [
    path('', lead_capture_list, name='lead_capture_list'),
    path('lead/<int:id>/', lead_capture_details, name='lead_capture_details'),
    path('create/', lead_capture_create, name='lead_capture_create'),
    path('lead/<int:id>/edit',lead_capture_update, name='lead_capture_update'),
    path('lead/<int:id>/delete',lead_capture_delete, name='lead_capture_delete'),
    path('pipeline/',lead_pipeline_view, name='lead_pipeline_view'),
    path('report/', lead_conversion_report, name='lead_conversion_report'),
    path('followup/', followup_shedule, name='followup_shedule'),
    path('call-logs/', call_log_view, name='call_logs'),
    path('delete/<int:id>/', delete_call_log, name='delete_call'),
]