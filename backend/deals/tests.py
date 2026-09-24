from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from authorization.models import Permission
from common.models import Sequence
from customers.models import Customer
from deals.models import Deal
from rbac.models import Membership, Role, RolePermission
from tenants.models import Tenant


class DealAPITest(TestCase):

    databases = {"default", "shared_db"}

    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.using("default").create(
            name="Deal Tenant A",
            company_email="deala@tenant.com",
            company_mobile="9100000101",
            database_alias="shared_db",
        )

        cls.tenant_b = Tenant.objects.using("default").create(
            name="Deal Tenant B",
            company_email="dealb@tenant.com",
            company_mobile="9100000102",
            database_alias="shared_db",
        )

        cls.user_a = User.objects.create_user(
            username="deal_user_a",
            email="deala@example.com",
            password="TestPass123!",
        )

        cls.role_a = Role.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            name="Admin",
        )

        deal_permissions = Permission.objects.using(
            "shared_db"
        ).filter(
            code__in=[
                "deals.view",
                "deals.create",
                "deals.update",
                "deals.delete",
                "deals.approve",
            ],
            is_active=True,
        )

        RolePermission.objects.using(
            "shared_db"
        ).bulk_create(
            [
                RolePermission(
                    role=cls.role_a,
                    permission=permission,
                )
                for permission in deal_permissions
            ]
        )

        Membership.objects.using("shared_db").create(
            user=cls.user_a,
            tenant_id=cls.tenant_a.id,
            role=cls.role_a,
        )

        Sequence.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            sequence_type=Sequence.SequenceType.DEAL,
            next_number=2,
        )

        cls.customer_a = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_a.id,
            customer_code="CUS000001",
            customer_type="BUSINESS",
            contact_name="Rahul Sharma",
            company_name="ABC Technologies",
            email="rahul@abc.com",
            mobile="9999999999",
        )

        cls.customer_b = Customer.objects.using(
            "shared_db"
        ).create(
            tenant_id=cls.tenant_b.id,
            customer_code="CUS000001",
            customer_type="BUSINESS",
            contact_name="Amit Verma",
            company_name="XYZ Technologies",
            email="amit@xyz.com",
            mobile="8888888888",
        )

        cls.deal_a = Deal.objects.using("shared_db").create(
            tenant_id=cls.tenant_a.id,
            deal_code="DEAL000001",
            customer_id=cls.customer_a.id,
            title="CRM Implementation",
            description="CRM implementation project",
            stage=Deal.DealStage.PROPOSAL,
            status=Deal.DealStatus.OPEN,
            amount=500000,
            probability=60,
        )

        cls.deal_b = Deal.objects.using("shared_db").create(
            tenant_id=cls.tenant_b.id,
            deal_code="DEAL000001",
            customer_id=cls.customer_b.id,
            title="Another CRM Deal",
            description="Tenant B deal",
            stage=Deal.DealStage.QUALIFICATION,
            status=Deal.DealStatus.OPEN,
            amount=300000,
            probability=30,
        )

    def setUp(self):
        self.client = APIClient()

        self.client.force_authenticate(
            user=self.user_a,
        )

        self.client.defaults[
            "HTTP_X_COMPANY_MOBILE"
        ] = self.tenant_a.company_mobile

    def test_list_deals(self):
        response = self.client.get(
            "/api/deals/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(response.data["results"][0]["deal_code"],"DEAL000001",)

    def test_get_deal(self):
        response = self.client.get(
            f"/api/deals/{self.deal_a.id}/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["title"],"CRM Implementation",)

    def test_cross_tenant_deal_not_visible(self):
        response = self.client.get(
            f"/api/deals/{self.deal_b.id}/",
        )

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND,)

    def test_create_deal(self):
        response = self.client.post(
            "/api/deals/",
            {
                "customer_id": self.customer_a.id,
                "title": "New CRM Deal",
                "description": "New opportunity",
                "stage": "QUALIFICATION",
                "amount": "250000",
                "probability": "40",
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)
        self.assertEqual(response.data["data"]["deal_code"],"DEAL000002",)
        self.assertEqual(response.data["data"]["title"],"New CRM Deal",)

    def test_create_deal_with_other_tenant_customer_fails(self):
        response = self.client.post(
            "/api/deals/",
            {
                "customer_id": self.customer_b.id,
                "title": "Invalid Deal",
                "amount": "100000",
                "probability": "50",
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND,)

    def test_update_deal(self):
        response = self.client.patch(
            f"/api/deals/{self.deal_a.id}/",
            {
                "title": "Updated CRM Deal",
                "amount": "750000",
                "probability": "80",
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["title"],"Updated CRM Deal",)
        self.assertEqual(response.data["data"]["amount"],"750000.00",)

    def test_delete_deal(self):
        response = self.client.delete(
            f"/api/deals/{self.deal_a.id}/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

        self.deal_a.refresh_from_db()

        self.assertFalse(self.deal_a.is_active,)

    def test_search_deals(self):
        response = self.client.get(
            "/api/deals/?search=Implementation",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(response.data["results"][0]["title"],"CRM Implementation",)

    def test_filter_deals_by_stage(self):
        response = self.client.get(
            "/api/deals/?stage=PROPOSAL",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(response.data["results"][0]["stage"],"PROPOSAL",)

    def test_filter_deals_by_customer(self):
        response = self.client.get(
            f"/api/deals/?customer_id={self.customer_a.id}",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(len(response.data["results"]),1,)
        self.assertEqual(
            response.data["results"][0]["customer_id"],
            self.customer_a.id,
        )

    def test_negative_amount_rejected(self):
        response = self.client.post(
            "/api/deals/",
            {
                "customer_id": self.customer_a.id,
                "title": "Invalid Amount",
                "amount": "-100",
                "probability": "50",
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)
        self.assertIn("amount",response.data["errors"],)

    def test_invalid_probability_rejected(self):
        response = self.client.post(
            "/api/deals/",
            {
                "customer_id": self.customer_a.id,
                "title": "Invalid Probability",
                "amount": "100000",
                "probability": "150",
            },
            format="json",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)
        self.assertIn("probability",response.data["errors"],)

    def test_mark_deal_as_won(self):
        response = self.client.post(
            f"/api/deals/{self.deal_a.id}/won/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["status"],"WON",)
        self.assertEqual(response.data["data"]["stage"],"WON",)
        self.assertEqual(response.data["data"]["probability"],"100.00",)

    def test_mark_deal_as_lost(self):
        response = self.client.post(
            f"/api/deals/{self.deal_a.id}/lost/",
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["data"]["status"],"LOST",)
        self.assertEqual(response.data["data"]["stage"],"LOST",)
        self.assertEqual(response.data["data"]["probability"],"0.00",)

    def test_won_deal_cannot_be_marked_as_lost(self):
        self.client.post(
            f"/api/deals/{self.deal_a.id}/won/",
        )

        response = self.client.post(
            f"/api/deals/{self.deal_a.id}/lost/",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_lost_deal_cannot_be_marked_as_won(self):
        self.client.post(
            f"/api/deals/{self.deal_a.id}/lost/",
        )

        response = self.client.post(
            f"/api/deals/{self.deal_a.id}/won/",
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_unauthenticated_user_cannot_access_deals(self):
        self.client.force_authenticate(user=None,)

        response = self.client.get(
            "/api/deals/",
        )

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,)