from django.urls import path

from leads.views import LeadAPIView

urlpatterns = [
    path("",LeadAPIView.as_view(),name="leads",),
<<<<<<< HEAD
    path("<int:lead_id>/convert/",LeadAPIView.as_view(),name="lead-convert",),
=======
    path("<int:lead_id>/",LeadAPIView.as_view(),name="lead-detail",),
>>>>>>> ec8d21eaf1fe99d8d99c002e56ff16552feaee86
]