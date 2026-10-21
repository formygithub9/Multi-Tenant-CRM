from django.urls import path

from invoices.views import InvoiceAPIView, InvoiceStatusAPIView

urlpatterns = [
    path("", InvoiceAPIView.as_view(), name="invoices"),
    path("<int:invoice_id>/", InvoiceAPIView.as_view(), name="invoice-detail"),
    path("<int:invoice_id>/<str:new_status>/", InvoiceStatusAPIView.as_view(), name="invoice-status"),
]