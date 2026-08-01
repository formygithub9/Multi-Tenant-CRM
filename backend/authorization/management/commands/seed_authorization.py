from django.core.management.base import BaseCommand

from authorization.services import AuthorizationService


class Command(BaseCommand):

    help = "Seed default modules, permission types and permissions"

    def handle(self, *args, **kwargs):

        AuthorizationService.create_default_permissions()

        self.stdout.write(
            self.style.SUCCESS(
                "Authorization data seeded successfully."
            )
        )