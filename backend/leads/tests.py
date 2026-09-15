from django.test import TestCase

from common.models import Sequence
from contacts.models import Contact
from customers.models import Customer
from leads.models import Lead
from leads.services import LeadService
from tenants.models import Tenant
from core.exceptions import BadRequestException


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