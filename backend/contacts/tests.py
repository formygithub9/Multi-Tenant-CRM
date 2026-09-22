from django.test import TestCase
from django.db import transaction
from contacts.models import Contact
from contacts.services import ContactService
from core.db_context import get_current_database
from core.exceptions import NotFoundException

from customers.models import Customer

from tenants.models import Tenant


class ContactTenantIsolationTest(TestCase):

    databases = {"default", "shared_db"}

    def setUp(self):
        self.tenant_a = Tenant.objects.using("default").create(
            name="Company A",
            company_mobile="7777777771",
            company_email="a@company.com",
            database_alias="shared_db",
        )

        self.tenant_b = Tenant.objects.using("default").create(
            name="Company B",
            company_mobile="7777777772",
            company_email="b@company.com",
            database_alias="shared_db",
        )

        self.customer_a = Customer.objects.using("shared_db").create(
            tenant_id=self.tenant_a.id,
            customer_code="CUST000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Rahul Sharma",
            company_name="Company A",
            email="rahul@a.com",
            mobile="9999999991",
        )

        self.customer_b = Customer.objects.using("shared_db").create(
            tenant_id=self.tenant_b.id,
            customer_code="CUST000001",
            customer_type=Customer.CustomerType.BUSINESS,
            contact_name="Amit Verma",
            company_name="Company B",
            email="amit@b.com",
            mobile="9999999992",
        )

    def test_create_contact_for_same_tenant_customer(self):
        contact = ContactService.create_contact(
            {
                "tenant_id": self.tenant_a.id,
                "customer_id": self.customer_a.id,
                "first_name": "Rahul",
                "last_name": "Sharma",
                "email": "rahul@a.com",
                "mobile": "9999999991",
                "is_primary": True,
            }
        )

        self.assertEqual(
            contact.tenant_id,
            self.tenant_a.id,
        )

        self.assertEqual(
            contact.customer_id,
            self.customer_a.id,
        )

        self.assertTrue(
            Contact.objects.using("shared_db").filter(
                id=contact.id,
                tenant_id=self.tenant_a.id,
                customer_id=self.customer_a.id,
            ).exists()
        )

    def test_cannot_create_contact_for_other_tenant_customer(self):
        with self.assertRaises(NotFoundException) as context:
            ContactService.create_contact(
                {
                    "tenant_id": self.tenant_a.id,
                    "customer_id": self.customer_b.id,
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@test.com",
                    "mobile": "9999999999",
                    "is_primary": False,
                }
            )

        self.assertEqual(
            str(context.exception),
            "Customer not found.",
        )

        self.assertFalse(
            Contact.objects.using("shared_db").filter(
                tenant_id=self.tenant_a.id,
                customer_id=self.customer_b.id,
            ).exists()
        )

    def test_cannot_create_contact_for_inactive_customer(self):
        self.customer_a.is_active = False

        self.customer_a.save(
            using="shared_db",
            update_fields=["is_active"],
        )

        with self.assertRaises(NotFoundException) as context:
            ContactService.create_contact(
                {
                    "tenant_id": self.tenant_a.id,
                    "customer_id": self.customer_a.id,
                    "first_name": "Rahul",
                    "last_name": "Sharma",
                    "email": "rahul@a.com",
                    "mobile": "9999999991",
                    "is_primary": False,
                }
            )

        self.assertEqual(
            str(context.exception),
            "Customer not found.",
        )


    @classmethod
    def create_contact(cls, validated_data):
        database = get_current_database()

        with transaction.atomic(using=database):
            tenant_id = validated_data["tenant_id"]
            customer_id = validated_data["customer_id"]

            customer_exists = (
                Customer.objects
                .using(database)
                .filter(
                    id=customer_id,
                    tenant_id=tenant_id,
                    is_active=True,
                )
                .exists()
            )

            if not customer_exists:
                raise NotFoundException(
                    "Customer not found."
                )

            contact = Contact.objects.using(database).create(
                **validated_data
            )

        return contact