"""
Django management command to populate Country model with real data

This command fetches comprehensive country data from the REST Countries API
and populates the Country model with accurate information including:
- ISO codes (2-letter and 3-letter)
- Official and common names
- Geographic coordinates
- Phone codes
- Region and subregion information
- Population and area data

Usage:
    python manage.py populate_countries [--update-existing]
"""

import json
import urllib.request
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Country


class Command(BaseCommand):
    help = "Populate Country model with real data from REST Countries API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing countries instead of skipping them",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        self.update_existing = options["update_existing"]
        self.dry_run = options["dry_run"]

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE: No changes will be made")
            )

        try:
            countries_data = self.fetch_countries_data()
            self.populate_countries(countries_data)
        except Exception as e:
            raise CommandError(f"Error populating countries: {str(e)}")

    def fetch_countries_data(self) -> List[Dict[str, Any]]:
        """Fetch country data from REST Countries API"""

        # Fields we need from the API
        fields = [
            "name",  # Common and official names
            "cca2",  # ISO 2-letter code
            "cca3",  # ISO 3-letter code
            "idd",  # International dialing codes
            "latlng",  # Latitude and longitude
            "region",  # Geographic region
            "subregion",  # Geographic subregion
            "population",  # Population
            "area",  # Area in km²
        ]

        api_url = f"https://restcountries.com/v3.1/all?fields={','.join(fields)}"

        if self.verbosity >= 2:
            self.stdout.write(f"Fetching data from: {api_url}")

        try:
            with urllib.request.urlopen(api_url, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            if self.verbosity >= 2:
                self.stdout.write(
                    f"Successfully fetched data for {len(data)} countries"
                )

            return data

        except urllib.error.URLError as e:
            raise CommandError(f"Failed to fetch country data: {str(e)}")
        except json.JSONDecodeError as e:
            raise CommandError(f"Failed to parse country data: {str(e)}")

    def extract_phone_code(self, idd_data: Dict[str, Any]) -> str:
        """Extract phone code from IDD data"""
        if not idd_data:
            return ""

        root = idd_data.get("root", "")
        suffixes = idd_data.get("suffixes", [])

        if root and suffixes:
            # Use the first suffix for the primary phone code
            return f"{root}{suffixes[0]}"
        elif root:
            return root
        else:
            return ""

    def normalize_country_data(self, country_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize country data for our model"""

        name_data = country_data.get("name", {})
        latlng = country_data.get("latlng", [])

        # Extract coordinates
        latitude = Decimal(str(latlng[0])) if len(latlng) >= 1 else None
        longitude = Decimal(str(latlng[1])) if len(latlng) >= 2 else None

        # Extract phone code
        phone_code = self.extract_phone_code(country_data.get("idd", {}))

        normalized = {
            "iso_code_2": country_data.get("cca2", ""),
            "iso_code_3": country_data.get("cca3", ""),
            "name": name_data.get("common", ""),
            "official_name": name_data.get("official", ""),
            "latitude": latitude,
            "longitude": longitude,
            "phone_code": phone_code,
            "region": country_data.get("region", ""),
            "subregion": country_data.get("subregion", ""),
            "population": country_data.get("population"),
            "area": (
                Decimal(str(country_data["area"])) if country_data.get("area") else None
            ),
        }

        return normalized

    @transaction.atomic
    def populate_countries(self, countries_data: List[Dict[str, Any]]):
        """Populate Country model with normalized data"""

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors_count = 0

        for country_data in countries_data:
            try:
                normalized_data = self.normalize_country_data(country_data)

                # Skip if missing critical data
                if not normalized_data["iso_code_2"] or not normalized_data["name"]:
                    if self.verbosity >= 2:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping country with missing critical data: {country_data}"
                            )
                        )
                    skipped_count += 1
                    continue

                if self.dry_run:
                    self.stdout.write(
                        f"Would process: {normalized_data['name']} ({normalized_data['iso_code_2']})"
                    )
                    continue

                # Check if country already exists
                country, created = Country.objects.get_or_create(
                    iso_code_2=normalized_data["iso_code_2"], defaults=normalized_data
                )

                if created:
                    created_count += 1
                    if self.verbosity >= 2:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created: {country.name} ({country.iso_code_2})"
                            )
                        )
                elif self.update_existing:
                    # Update existing country
                    for field, value in normalized_data.items():
                        if field != "iso_code_2":  # Don't update the lookup field
                            setattr(country, field, value)
                    country.save()
                    updated_count += 1
                    if self.verbosity >= 2:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated: {country.name} ({country.iso_code_2})"
                            )
                        )
                else:
                    skipped_count += 1
                    if self.verbosity >= 2:
                        self.stdout.write(
                            f"Skipped existing: {country.name} ({country.iso_code_2})"
                        )

            except Exception as e:
                errors_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Error processing country {country_data.get('name', {}).get('common', 'Unknown')}: {str(e)}"
                    )
                )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("COUNTRY POPULATION SUMMARY"))
        self.stdout.write("=" * 50)

        if not self.dry_run:
            self.stdout.write(f"Created: {created_count} countries")
            if self.update_existing:
                self.stdout.write(f"Updated: {updated_count} countries")
            self.stdout.write(f"Skipped: {skipped_count} countries")
            if errors_count > 0:
                self.stdout.write(self.style.ERROR(f"Errors: {errors_count} countries"))

            total_countries = Country.objects.count()
            self.stdout.write(f"Total countries in database: {total_countries}")
        else:
            self.stdout.write(f"Would process: {len(countries_data)} countries")

        self.stdout.write("=" * 50)

        if errors_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Completed with {errors_count} errors. Check the output above for details."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Country population completed successfully!")
            )
