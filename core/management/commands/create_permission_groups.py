"""
Management command to create CASA-compliant aviation permission groups.

This command creates permission groups that align with the ProfileType system
for proper RPAS operations access control.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ProfileType


class Command(BaseCommand):
    help = "Create CASA-compliant permission groups for RPAS operations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreation of groups (delete existing)",
        )

    def handle(self, *args, **options):
        """Create permission groups for CASA compliance."""
        force = options.get("force", False)

        self.stdout.write("Creating CASA-compliant permission groups...")

        # Define permission groups based on ProfileType choices
        group_definitions = {
            "Pilots": {
                "description": "CASA certified remote pilots with ReOC authority",
                "permissions": [
                    # Core permissions
                    "view_aircraft",
                    "operate_aircraft",
                    "create_flight_log",
                    "view_flight_log",
                    "change_own_flight_log",
                    # Aviation specific
                    "view_operations_manual",
                    "submit_incident_report",
                    "access_safety_management_system",
                ],
            },
            "Staff": {
                "description": "Operations managers, safety officers, maintenance personnel",
                "permissions": [
                    # Management permissions
                    "view_all_aircraft",
                    "change_aircraft",
                    "add_aircraft",
                    "view_all_flight_logs",
                    "change_flight_log",
                    "view_all_pilots",
                    "manage_maintenance_records",
                    # Administrative
                    "view_operations_manual",
                    "change_operations_manual",
                    "view_incident_reports",
                    "manage_safety_management_system",
                    "generate_compliance_reports",
                ],
            },
            "Clients": {
                "description": "Commercial customers requiring drone services",
                "permissions": [
                    # Client-specific permissions
                    "view_own_projects",
                    "create_service_request",
                    "view_project_flight_logs",
                    "view_project_reports",
                    "access_client_portal",
                ],
            },
            "Customers": {
                "description": "End users of drone services and operations",
                "permissions": [
                    # Customer permissions
                    "view_own_services",
                    "view_service_status",
                    "request_service_updates",
                    "access_customer_portal",
                ],
            },
            "General": {
                "description": "Non-operational system users with limited access",
                "permissions": [
                    # Basic permissions
                    "view_public_information",
                    "access_help_documentation",
                ],
            },
        }

        with transaction.atomic():
            for group_name, group_data in group_definitions.items():
                # Handle existing groups
                if Group.objects.filter(name=group_name).exists():
                    if force:
                        Group.objects.filter(name=group_name).delete()
                        self.stdout.write(
                            self.style.WARNING(f"Deleted existing group: {group_name}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Group '{group_name}' already exists. Use --force to recreate."
                            )
                        )
                        continue

                # Create group
                Group.objects.create(name=group_name)
                self.stdout.write(self.style.SUCCESS(f"Created group: {group_name}"))

                # Note: Permissions will be assigned when actual models are created
                # This establishes the group structure for now
                self.stdout.write(f"  Description: {group_data['description']}")
                self.stdout.write(
                    f"  Planned permissions: {len(group_data['permissions'])}"
                )

        # Verify ProfileType alignment
        self.stdout.write("\nVerifying ProfileType alignment...")
        profile_types = [choice[0] for choice in ProfileType.PROFILE_TYPES]
        created_groups = list(group_definitions.keys())

        for profile_type in profile_types:
            # Convert profile_type to title case to match group names
            group_name = profile_type.title()
            if group_name == "General":
                group_name = "General"  # Already correct
            elif group_name == "Pilot":
                group_name = "Pilots"  # Plural for group
            elif group_name == "Client":
                group_name = "Clients"  # Plural for group
            elif group_name == "Customer":
                group_name = "Customers"  # Plural for group
            elif group_name == "Staff":
                group_name = "Staff"  # Already correct

            if group_name in created_groups:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ {profile_type} -> {group_name}: Aligned")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ {profile_type} -> {group_name}: Missing group"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created {len(group_definitions)} permission groups"
            )
        )
        self.stdout.write(
            "Next: Create aviation models and assign object-level permissions"
        )
