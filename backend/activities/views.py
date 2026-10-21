
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rbac.permissions import HasPermission
from core.responses import APIResponse
from core.pagination import StandardPagination

from activities.models import Activity
from activities.serializers import (
    ActivityCreateSerializer,
    ActivityReadSerializer,
    ActivityStatusSerializer,
    ActivityUpdateSerializer,
)
from activities.services import ActivityService


class ActivityAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permission(self, request, *args, **kwargs):
        return {
            "GET": "activities.view",
            "HEAD": "activities.view",
            "POST": "activities.create",
            "PUT": "activities.update",
            "DELETE": "activities.delete",
        }.get(request.method)

    def get(self, request, activity_id=None):
        tenant_id = request.tenant_id

        if activity_id is not None:
            activity = ActivityService.get_by_id(tenant_id, activity_id)
            return APIResponse.success(ActivityReadSerializer(activity).data)

        filters = {
            "status": request.query_params.get("status"),
            "priority": request.query_params.get("priority"),
            "activity_type": request.query_params.get("activity_type"),
            "assigned_to_id": request.query_params.get("assigned_to_id"),
            "related_type": request.query_params.get("related_type"),
            "related_id": request.query_params.get("related_id"),
        }
        queryset = ActivityService.get_queryset(tenant_id, filters)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(ActivityReadSerializer(page, many=True).data)

    def post(self, request):
        # self.required_permission = "activities.create"
        serializer = ActivityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activity = ActivityService.create(
            request.tenant_id,
            request.user.id,
            serializer.validated_data,
        )
        return APIResponse.success(
            ActivityReadSerializer(activity).data,
            message="Activity created successfully.",
            status_code=201,
        )

    def put(self, request, activity_id):
        # self.required_permission = "activities.update"
        serializer = ActivityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activity = ActivityService.update(
            request.tenant_id,
            activity_id,
            serializer.validated_data,
        )
        return APIResponse.success(
            ActivityReadSerializer(activity).data,
            message="Activity updated successfully.",
        )

    def delete(self, request, activity_id):
        # self.required_permission = "activities.delete"
        activity = ActivityService.delete(request.tenant_id, activity_id)
        return APIResponse.success(
            {"id": activity.id},
            message="Activity deleted successfully.",
        )


class ActivityStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "activities.update"

    def patch(self, request, activity_id):
        serializer = ActivityStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activity = ActivityService.change_status(
            request.tenant_id,
            activity_id,
            serializer.validated_data["status"],
        )
        return APIResponse.success(
            ActivityReadSerializer(activity).data,
            message="Activity status updated successfully.",
        )
