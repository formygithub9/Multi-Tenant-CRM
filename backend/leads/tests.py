from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User
from rbac.models import Membership, Role

from common.models import Sequence
from contacts.models import Contact
from customers.models import Customer
from leads.models import Lead
from leads.services import LeadService
from tenants.models import Tenant
from core.exceptions import BadRequestException, NotFoundException


class LeadConversionTest(TestCase):

    databases = {"default", "shared_db"}

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Company",
            company_mobile="9999999999",
            company_email="test@company.com",
            database_alias="default",
        )

        Sequence.objects.create(
            tenant_id=self.tenant.id,
            sequence_type=Sequence.SequenceType.CUSTOMER,
            next_number=1,
        )

        self.lead = Lead.objects.create(
            tenant_id=self.tenant.id,
            lead_code="LEAD000001",
            contact_name="Rahul Sharma",
            company_name="ABC Technologies",
            email="rahul@abc.com",
            mobile="9976543210",
            source=Lead.LeadSource.WEBSITE,
            status=Lead.LeadStatus.QUALIFIED,
            notes="Interested in CRM solution",
        )

    def test_convert_qualified_lead(self):
        customer, contact = LeadService.convert_lead(
            tenant_id=self.tenant.id,
            lead_id=self.lead.id,
        )

        self.lead.refresh_from_db()

        self.assertEqual(
            self.lead.status,
            Lead.LeadStatus.CONVERTED,
        )

        self.assertEqual(
            customer.tenant_id,
            self.tenant.id,
        )

        self.assertEqual(
            customer.contact_name,
            "Rahul Sharma",
        )

        self.assertEqual(
            customer.company_name,
            "ABC Technologies",
        )

        self.assertEqual(
            contact.tenant_id,
            self.tenant.id,
        )

        self.assertEqual(
            contact.customer_id,
            customer.id,
        )

        self.assertEqual(
            contact.first_name,
            "Rahul",
        )

        self.assertEqual(
            contact.last_name,
            "Sharma",
        )

        self.assertTrue(
            contact.is_primary,
        )

        self.assertTrue(
            Customer.objects.filter(
                id=customer.id,
                tenant_id=self.tenant.id,
            ).exists()
        )

        self.assertTrue(
            Contact.objects.filter(
                id=contact.id,
                tenant_id=self.tenant.id,
                customer_id=customer.id,
            ).exists()
        )

    def test_cannot_convert_lead_twice(self):
        LeadService.convert_lead(
            tenant_id=self.tenant.id,
            lead_id=self.lead.id,
        )

        with self.assertRaises(BadRequestException) as context:
            LeadService.convert_lead(
                tenant_id=self.tenant.id,
                lead_id=self.lead.id,
            )

        self.assertEqual(
            str(context.exception),
            "Lead has already been converted.",
        )

class LeadTenantIsolationTest(TestCase):

    databases = {"default", "shared_db"}

    def setUp(self):
        self.tenant_a = Tenant.objects.create(
            name="Company A",
            company_mobile="9999999991",
            company_email="a@company.com",
            database_alias="default",
        )

        self.tenant_b = Tenant.objects.create(
            name="Company B",
            company_mobile="9999999992",
            company_email="b@company.com",
            database_alias="default",
        )

        self.lead_a = Lead.objects.create(
            tenant_id=self.tenant_a.id,
            lead_code="LEAD000001",
            contact_name="Rahul Sharma",
            company_name="Company A",
            email="rahul@a.com",
            status=Lead.LeadStatus.QUALIFIED,
        )

        self.lead_b = Lead.objects.create(
            tenant_id=self.tenant_b.id,
            lead_code="LEAD000001",
            contact_name="Amit Verma",
            company_name="Company B",
            email="amit@b.com",
            status=Lead.LeadStatus.QUALIFIED,
        )

    def test_tenant_cannot_access_other_tenant_lead(self):
        with self.assertRaises(NotFoundException) as context:
            LeadService.get_lead_by_id(
                tenant_id=self.tenant_a.id,
                lead_id=self.lead_b.id,
            )

        self.assertEqual(
            str(context.exception),
            "Lead not found.",
        )

    def test_tenant_only_gets_own_leads(self):
        leads = LeadService.get_leads(
            tenant_id=self.tenant_a.id,
        )

        lead_ids = list(
            leads.values_list("id", flat=True)
        )

        self.assertIn(
            self.lead_a.id,
            lead_ids,
        )

        self.assertNotIn(
            self.lead_b.id,
            lead_ids,
        )

    def test_tenant_cannot_convert_other_tenant_lead(self):
        with self.assertRaises(NotFoundException) as context:
            LeadService.convert_lead(
                tenant_id=self.tenant_a.id,
                lead_id=self.lead_b.id,
            )

        self.assertEqual(
            str(context.exception),
            "Lead not found.",
        )

        self.lead_b.refresh_from_db()

        self.assertEqual(
            self.lead_b.status,
            Lead.LeadStatus.QUALIFIED,
        )

    def test_inactive_lead_cannot_be_accessed(self):
        self.lead_a.is_active = False

        self.lead_a.save(
            update_fields=["is_active"]
        )

        with self.assertRaises(NotFoundException):
            LeadService.get_lead_by_id(
                tenant_id=self.tenant_a.id,
                lead_id=self.lead_a.id,
            )

class LeadAPITest(APITestCase):

    databases = {"default", "shared_db"}

    def setUp(self):
        self.tenant_a = Tenant.objects.create(
            name="Company A",
            company_mobile="8888888881",
            company_email="api_a@company.com",
            database_alias="default",
        )

        self.tenant_b = Tenant.objects.create(
            name="Company B",
            company_mobile="8888888882",
            company_email="api_b@company.com",
            database_alias="default",
        )

        self.role = Role.objects.create(
            name="Admin",
            tenant_id=self.tenant_a.id,
        )

        self.user = User.objects.create_user(
            username="rahul",
            email="rahul@test.com",
            password="TestPassword123",
        )

        Membership.objects.create(
            user=self.user,
            tenant_id=self.tenant_a.id,
            role=self.role,
        )

        self.client.force_authenticate(
            user=self.user,
        )

    def test_create_lead(self):
        response = self.client.post(
            "/api/leads/",
            {
                "contact_name": "Amit Sharma",
                "company_name": "ABC Pvt Ltd",
                "email": "amit@abc.com",
                "mobile": "9999999999",
                "source": "WEBSITE",
                "status": "QUALIFIED",
                "notes": "Interested in CRM",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            response.data["success"],
        )

        self.assertEqual(
            response.data["data"]["contact_name"],
            "Amit Sharma",
        )

        self.assertEqual(
            response.data["data"]["lead_code"],
            "LEAD000001",
        )

    def test_get_lead_list_only_returns_user_tenant_leads(self):
        Lead.objects.create(
            tenant_id=self.tenant_a.id,
            lead_code="LEAD000001",
            contact_name="Rahul Sharma",
            company_name="Company A",
            status=Lead.LeadStatus.NEW,
        )

        Lead.objects.create(
            tenant_id=self.tenant_b.id,
            lead_code="LEAD000001",
            contact_name="Amit Verma",
            company_name="Company B",
            status=Lead.LeadStatus.NEW,
        )

        response = self.client.get(
            "/api/leads/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response_data = response.data["data"]

        returned_names = [
            lead["contact_name"]
            for lead in response_data
        ]

        self.assertIn(
            "Rahul Sharma",
            returned_names,
        )

        self.assertNotIn(
            "Amit Verma",
            returned_names,
        )

    def test_get_other_tenant_lead_returns_not_found(self):
        lead_b = Lead.objects.create(
            tenant_id=self.tenant_b.id,
            lead_code="LEAD000001",
            contact_name="Amit Verma",
            company_name="Company B",
            status=Lead.LeadStatus.NEW,
        )

        response = self.client.get(
            f"/api/leads/{lead_b.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unauthenticated_user_cannot_access_leads(self):
        self.client.force_authenticate(
            user=None,
        )

        response = self.client.get(
            "/api/leads/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )