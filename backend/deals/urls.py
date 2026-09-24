from django.urls import path

from deals.views import DealAPIView, DealActionAPIView


urlpatterns = [
    path("", DealAPIView.as_view(), name="deals"),
    path("<int:deal_id>/",DealAPIView.as_view(),name="deal-detail",),
    path("<int:deal_id>/<str:action>/",DealActionAPIView.as_view(),name="deal-action",),
]