from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.responses import APIResponse
from dashboard.services import DashboardService
from rbac.permissions import HasPermission


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "dashboard.view"

    def get(self, request):
        summary = DashboardService.get_summary(request.tenant_id)
        return APIResponse.success(summary)