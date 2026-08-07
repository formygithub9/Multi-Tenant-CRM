from django.urls import path

from customers.views import *

urlpatterns = [
    path("", CustomerAPIView.as_view(), name="customers"),
    path("<int:customer_id>/", CustomerAPIView.as_view(), name="customer-detail"),
]