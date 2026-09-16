from django.urls import path

from leads.views import *

urlpatterns = [
    path("",LeadAPIView.as_view(),name="leads",),
    path("<int:lead_id>/convert/",LeadConvertAPIView.as_view(),name="lead-convert",),
    path("<int:lead_id>/",LeadAPIView.as_view(),name="lead-detail",),
]