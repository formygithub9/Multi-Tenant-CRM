
from django.urls import path

from payments.views import PaymentAPIView, PaymentStatusAPIView

urlpatterns = [
    path("", PaymentAPIView.as_view(), name="payment-list-create"),
    path("<int:payment_id>/", PaymentAPIView.as_view(), name="payment-detail"),
    path("<int:payment_id>/status/", PaymentStatusAPIView.as_view(), name="payment-status"),
]
