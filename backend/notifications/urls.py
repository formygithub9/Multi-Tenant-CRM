from django.urls import path

from notifications.views import NotificationAPIView

urlpatterns = [
    path("", NotificationAPIView.as_view(), name="notification-list"),
    path("<int:notification_id>/", NotificationAPIView.as_view(), name="notification-detail"),
]