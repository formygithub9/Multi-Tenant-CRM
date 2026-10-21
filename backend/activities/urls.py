
from django.urls import path

from activities.views import ActivityAPIView, ActivityStatusAPIView

urlpatterns = [
    path("", ActivityAPIView.as_view(), name="activity-list-create"),
    path("<int:activity_id>/", ActivityAPIView.as_view(), name="activity-detail"),
    path("<int:activity_id>/status/", ActivityStatusAPIView.as_view(), name="activity-status"),
]
