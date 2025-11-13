"""
Management command to populate ProfileType data with business rules

This command creates the foundational profile types with appropriate
business rules for permissions, requirements, and access control.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ProfileType


class Command(BaseCommand):
    help = "Populate ProfileType data with business rules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating it",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Define profile types with business rules
        profile_types_data = [
            {
                "code": "general",
                "name": "General User",
                "description": "Default profile type for new users. Basic access with no special privileges.",
                "is_active": True,
                "requires_image": False,
                "has_admin_access": False,
            },
            {
                "code": "staff",
                "name": "Staff Member",
                "description": "Internal staff member with administrative capabilities. Requires compliance documentation.",
                "is_active": True,
                "requires_image": True,  # Staff need profile images for identification
                "has_admin_access": True,
            },
            {
                "code": "pilot",
                "name": "Pilot",
                "description": "Licensed pilot with aviation credentials. Must have ARN number and compliance docs.",
                "is_active": True,
                "requires_image": True,  # Pilots need profile images for identification
                "has_admin_access": False,
            },
            {
                "code": "client",
                "name": "Client",
                "description": "Business client with enhanced access to services and features.",
                "is_active": True,
                "requires_image": False,
                "has_admin_access": False,
            },
            {
                "code": "customer",
                "name": "Customer",
                "description": "Paying customer with access to premium features and services.",
                "is_active": True,
                "requires_image": False,
                "has_admin_access": False,
            },
        ]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No data will be created")
            )
            self.stdout.write("")

        self.stdout.write("Processing ProfileType data...")
        self.stdout.write("")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for data in profile_types_data:
                code = data["code"]

                if dry_run:
                    # Check if it would be created or updated
                    existing = ProfileType.objects.filter(code=code).first()
                    if existing:
                        self.stdout.write(f"  📝 Would UPDATE: {data['name']} ({code})")
                    else:
                        self.stdout.write(f"  ✨ Would CREATE: {data['name']} ({code})")
                    continue

                # Get or create profile type
                profile_type, created = ProfileType.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": data["name"],
                        "description": data["description"],
                        "is_active": data["is_active"],
                        "requires_image": data["requires_image"],
                        "has_admin_access": data["has_admin_access"],
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ Created: {profile_type.name}")
                    )
                    created_count += 1
                else:
                    # Update existing profile type with new data
                    updated = False
                    fields_to_update = [
                        "name",
                        "description",
                        "is_active",
                        "requires_image",
                        "has_admin_access",
                    ]

                    for field in fields_to_update:
                        if getattr(profile_type, field) != data[field]:
                            setattr(profile_type, field, data[field])
                            updated = True

                    if updated:
                        profile_type.save()
                        self.stdout.write(
                            self.style.WARNING(f"  📝 Updated: {profile_type.name}")
                        )
                        updated_count += 1
                    else:
                        self.stdout.write(
                            f"  ⏭️  Skipped: {profile_type.name} (no changes)"
                        )
                        skipped_count += 1

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("PROFILE TYPES SUMMARY")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write("DRY RUN COMPLETED - No actual changes made")
        else:
            self.stdout.write(f"Created: {created_count} profile types")
            self.stdout.write(f"Updated: {updated_count} profile types")
            self.stdout.write(f"Skipped: {skipped_count} profile types")

            # Show business rules summary
            self.stdout.write("")
            self.stdout.write("BUSINESS RULES APPLIED:")
            self.stdout.write("🔒 Only staff/superusers can assign profile types")
            self.stdout.write("👤 Staff & Pilot profiles require images")
            self.stdout.write("🏢 Only Staff profiles have admin access")
            self.stdout.write("📋 Default profile type: General User")

        self.stdout.write("=" * 60)
        self.stdout.write("Profile type population completed!")
