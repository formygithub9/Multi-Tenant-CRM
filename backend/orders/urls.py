from django.urls import path

from orders.views import OrderAPIView, OrderStatusAPIView


urlpatterns = [
    path("", OrderAPIView.as_view(), name="orders"),
    path("<int:order_id>/", OrderAPIView.as_view(), name="order-detail"),
    path("<int:order_id>/<str:new_status>/",OrderStatusAPIView.as_view(),name="order-status",),
]