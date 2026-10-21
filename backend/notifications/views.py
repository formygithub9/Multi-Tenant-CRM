from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.pagination import StandardPagination
from core.responses import APIResponse
from notifications.serializers import NotificationReadSerializer
from notifications.services import NotificationService
from rbac.permissions import HasPermission


class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permission(self, request, *args, **kwargs):
        return {
            "GET": "notifications.view",
            "HEAD": "notifications.view",
            "PATCH": "notifications.update",
            "DELETE": "notifications.delete",
        }.get(request.method)

    def get(self, request, notification_id=None):
        tenant_id = request.tenant_id
        user_id = request.user.id

        if notification_id is not None:
            notification = NotificationService.mark_read(
                tenant_id, user_id, notification_id
            )
            return APIResponse.success(NotificationReadSerializer(notification).data)

        unread_only = request.query_params.get("unread") == "true"
        queryset = NotificationService.get_queryset(
            tenant_id, user_id, unread_only
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(
            NotificationReadSerializer(page, many=True).data
        )

    def patch(self, request):
        # self.required_permission = "notifications.update"
        updated_count = NotificationService.mark_all_read(
            request.tenant_id, request.user.id
        )
        return APIResponse.success(
            {"updated_count": updated_count},
            message="Notifications marked as read.",
        )

    def delete(self, request, notification_id):
        # self.required_permission = "notifications.delete"
        notification = NotificationService.delete(
            request.tenant_id, request.user.id, notification_id
        )
        return APIResponse.success(
            {"id": notification.id},
            message="Notification deleted successfully.",
        )