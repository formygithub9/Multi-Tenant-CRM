from django.urls import path

from leads.views import LeadAPIView

urlpatterns = [
    path("",LeadAPIView.as_view(),name="leads",),
    path("<int:lead_id>/",LeadAPIView.as_view(),name="lead-detail",),
]