from django.urls import path

from customers.views import CustomerCreateAPIView

urlpatterns = [
    path("",CustomerCreateAPIView.as_view(),name="customer-create",),
]