"""
Management command to assign users to permission groups and manage object-level permissions.

This command provides functionality to:
- Assign users to CASA-compliant permission groups
- Create test aircraft and assign pilot permissions
- Demonstrate object-level permission functionality
"""

from guardian.shortcuts import assign_perm, get_users_with_perms

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ProfileType
from rpas.models import Aircraft

User = get_user_model()


class Command(BaseCommand):
    help = "Manage user permission assignments for CASA compliance"

    def add_arguments(self, parser):
        parser.add_argument(
            "--assign-user-to-group",
            nargs=2,
            metavar=("USER_EMAIL", "GROUP_NAME"),
            help="Assign user to permission group",
        )
        parser.add_argument(
            "--create-demo-aircraft",
            action="store_true",
            help="Create demonstration aircraft for testing",
        )
        parser.add_argument(
            "--assign-pilot-to-aircraft",
            nargs=2,
            metavar=("USER_EMAIL", "AIRCRAFT_REGISTRATION"),
            help="Assign pilot permissions to specific aircraft",
        )
        parser.add_argument(
            "--show-aircraft-permissions",
            metavar="AIRCRAFT_REGISTRATION",
            help="Show all permissions for specific aircraft",
        )
        parser.add_argument(
            "--show-user-groups",
            metavar="USER_EMAIL",
            help="Show all groups for specific user",
        )

    def handle(self, *args, **options):
        """Handle permission management operations."""

        if options.get("assign_user_to_group"):
            self._assign_user_to_group(*options["assign_user_to_group"])

        elif options.get("create_demo_aircraft"):
            self._create_demo_aircraft()

        elif options.get("assign_pilot_to_aircraft"):
            self._assign_pilot_to_aircraft(*options["assign_pilot_to_aircraft"])

        elif options.get("show_aircraft_permissions"):
            self._show_aircraft_permissions(options["show_aircraft_permissions"])

        elif options.get("show_user_groups"):
            self._show_user_groups(options["show_user_groups"])

        else:
            self._show_help()

    def _assign_user_to_group(self, user_email, group_name):
        """Assign a user to a permission group."""
        try:
            user = User.objects.get(email=user_email)
            group = Group.objects.get(name=group_name)

            user.groups.add(group)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully assigned {user.email} to group '{group.name}'"
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with email '{user_email}' not found")
            )
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Group '{group_name}' not found"))

    def _create_demo_aircraft(self):
        """Create demonstration aircraft for testing permissions."""
        # Get a superuser as owner
        try:
            owner = User.objects.filter(is_superuser=True).first()
            if not owner:
                self.stdout.write(
                    self.style.ERROR("No superuser found to set as aircraft owner")
                )
                return
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("No users found to set as aircraft owner")
            )
            return

        demo_aircraft = [
            {
                "registration": "VH-DJI001",
                "make": "DJI",
                "model": "Matrice 300 RTK",
                "serial_number": "M3RTK-001-2025",
            },
            {
                "registration": "VH-DJI002",
                "make": "DJI",
                "model": "Air 2S",
                "serial_number": "A2S-002-2025",
            },
            {
                "registration": "FLEET-001",
                "make": "Autel",
                "model": "EVO II Pro",
                "serial_number": "EVO2P-001-2025",
            },
        ]

        with transaction.atomic():
            for aircraft_data in demo_aircraft:
                aircraft, created = Aircraft.objects.get_or_create(
                    registration=aircraft_data["registration"],
                    defaults={
                        "make": aircraft_data["make"],
                        "model": aircraft_data["model"],
                        "serial_number": aircraft_data["serial_number"],
                        "owner": owner,
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created aircraft: {aircraft.registration} ({aircraft.make} {aircraft.model})"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Aircraft {aircraft.registration} already exists"
                        )
                    )

    def _assign_pilot_to_aircraft(self, user_email, aircraft_registration):
        """Assign pilot permissions to specific aircraft."""
        try:
            user = User.objects.get(email=user_email)
            aircraft = Aircraft.objects.get(registration=aircraft_registration)

            # Assign object-level permissions
            aircraft.assign_pilot(user)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Assigned pilot {user.email} to aircraft {aircraft.registration}"
                )
            )

            # Show assigned permissions
            self.stdout.write("Assigned permissions:")
            self.stdout.write("  - operate_aircraft")
            self.stdout.write("  - view_aircraft_logs")

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with email '{user_email}' not found")
            )
        except Aircraft.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Aircraft with registration '{aircraft_registration}' not found"
                )
            )

    def _show_aircraft_permissions(self, aircraft_registration):
        """Show all permissions assigned to specific aircraft."""
        try:
            aircraft = Aircraft.objects.get(registration=aircraft_registration)

            self.stdout.write(f"Permissions for aircraft {aircraft.registration}:")
            self.stdout.write(f"Owner: {aircraft.owner.email}")

            # Get users with permissions
            users_with_perms = get_users_with_perms(aircraft, attach_perms=True)

            if users_with_perms:
                self.stdout.write("\nAuthorized users:")
                for user, perms in users_with_perms.items():
                    self.stdout.write(f"  {user.email}:")
                    for perm in perms:
                        self.stdout.write(f"    - {perm}")
            else:
                self.stdout.write("  No specific permissions assigned")

        except Aircraft.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Aircraft with registration '{aircraft_registration}' not found"
                )
            )

    def _show_user_groups(self, user_email):
        """Show all groups assigned to specific user."""
        try:
            user = User.objects.get(email=user_email)

            self.stdout.write(f"Groups for user {user.email}:")

            groups = user.groups.all()
            if groups:
                for group in groups:
                    self.stdout.write(f"  - {group.name}")
            else:
                self.stdout.write("  No groups assigned")

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with email '{user_email}' not found")
            )

    def _show_help(self):
        """Show available commands and usage examples."""
        self.stdout.write("CASA-Compliant Permission Management Commands")
        self.stdout.write("=" * 50)
        self.stdout.write()
        self.stdout.write("Available commands:")
        self.stdout.write()
        self.stdout.write("1. Assign user to group:")
        self.stdout.write(
            "   python3 manage.py manage_permissions --assign-user-to-group user@example.com Pilots"
        )
        self.stdout.write()
        self.stdout.write("2. Create demo aircraft:")
        self.stdout.write(
            "   python3 manage.py manage_permissions --create-demo-aircraft"
        )
        self.stdout.write()
        self.stdout.write("3. Assign pilot to aircraft:")
        self.stdout.write(
            "   python3 manage.py manage_permissions --assign-pilot-to-aircraft pilot@example.com VH-DJI001"
        )
        self.stdout.write()
        self.stdout.write("4. Show aircraft permissions:")
        self.stdout.write(
            "   python3 manage.py manage_permissions --show-aircraft-permissions VH-DJI001"
        )
        self.stdout.write()
        self.stdout.write("5. Show user groups:")
        self.stdout.write(
            "   python3 manage.py manage_permissions --show-user-groups user@example.com"
        )
        self.stdout.write()
        self.stdout.write(
            "Available groups: Pilots, Staff, Clients, Customers, General"
        )

        # Show existing aircraft
        aircraft_count = Aircraft.objects.count()
        if aircraft_count > 0:
            self.stdout.write(f"\nExisting aircraft ({aircraft_count}):")
            for aircraft in Aircraft.objects.all()[:5]:  # Show first 5
                self.stdout.write(f"  - {aircraft.registration}")
