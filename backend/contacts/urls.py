from django.urls import path

from contacts.views import ContactAPIView


urlpatterns = [
    path("",ContactAPIView.as_view(),name="contact-list",),
    path("<int:contact_id>/",ContactAPIView.as_view(),name="contact-detail",),
]