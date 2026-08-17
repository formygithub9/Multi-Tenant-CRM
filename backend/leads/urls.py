from django.urls import path

from leads.views import LeadAPIView


urlpatterns = [
    path("",LeadAPIView.as_view(),name="leads",),
]