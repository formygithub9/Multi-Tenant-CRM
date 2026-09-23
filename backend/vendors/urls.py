from django.urls import path

from vendors.views import VendorAPIView


urlpatterns = [
    path("",VendorAPIView.as_view(),name="vendors",),
    path("<int:vendor_id>/",VendorAPIView.as_view(),name="vendor-detail",),
]