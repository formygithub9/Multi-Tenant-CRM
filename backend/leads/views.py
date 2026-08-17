from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rbac.models import Membership
from core.responses import APIResponse

from leads.serializers import LeadCreateSerializer


class LeadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        membership = Membership.objects.get(
            user=request.user,
        )

        data = request.data.copy()

        data["tenant_id"] = membership.tenant_id

        serializer = LeadCreateSerializer(
            data=data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        lead = serializer.save()

        return APIResponse.success(
            message="Lead created successfully.",
            data=LeadCreateSerializer(lead).data,
            status_code=status.HTTP_201_CREATED,
        )