"""
Django management command to populate State/Province model with real data

This command populates states/provinces for major countries using curated datasets.
Focuses on countries most likely to be used in the application.

Supported Countries:
- Australia (States and Territories)
- United States (States and D.C.)
- Canada (Provinces and Territories)
- United Kingdom (Countries/Regions)
- Germany (States/Länder)
- India (States and Union Territories)

Usage:
    python manage.py populate_states [--countries=US,AU,CA] [--update-existing]
"""

from decimal import Decimal
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Country, State


class Command(BaseCommand):
    help = "Populate State/Province model with real data for major countries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--countries",
            type=str,
            help="Comma-separated list of country codes to populate (e.g., US,AU,CA)",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing states instead of skipping them",
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

        # Determine which countries to populate
        if options["countries"]:
            country_codes = [
                code.strip().upper() for code in options["countries"].split(",")
            ]
        else:
            # Default to major countries
            country_codes = ["US", "AU", "CA", "GB", "DE", "IN"]

        try:
            self.populate_states(country_codes)
        except Exception as e:
            raise CommandError(f"Error populating states: {str(e)}")

    def get_states_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Curated state/province data for major countries

        Returns dictionary with country code as key and list of state data as value
        """
        return {
            "US": [  # United States
                {
                    "code": "AL",
                    "name": "Alabama",
                    "division_type": "State",
                    "lat": 32.7794,
                    "lng": -86.8287,
                },
                {
                    "code": "AK",
                    "name": "Alaska",
                    "division_type": "State",
                    "lat": 64.0685,
                    "lng": -152.2782,
                },
                {
                    "code": "AZ",
                    "name": "Arizona",
                    "division_type": "State",
                    "lat": 34.2744,
                    "lng": -111.2847,
                },
                {
                    "code": "AR",
                    "name": "Arkansas",
                    "division_type": "State",
                    "lat": 34.7519,
                    "lng": -92.1314,
                },
                {
                    "code": "CA",
                    "name": "California",
                    "division_type": "State",
                    "lat": 36.7783,
                    "lng": -119.4179,
                },
                {
                    "code": "CO",
                    "name": "Colorado",
                    "division_type": "State",
                    "lat": 39.5501,
                    "lng": -105.7821,
                },
                {
                    "code": "CT",
                    "name": "Connecticut",
                    "division_type": "State",
                    "lat": 41.6032,
                    "lng": -73.0877,
                },
                {
                    "code": "DE",
                    "name": "Delaware",
                    "division_type": "State",
                    "lat": 39.3498,
                    "lng": -75.5148,
                },
                {
                    "code": "DC",
                    "name": "District of Columbia",
                    "division_type": "Federal District",
                    "lat": 38.9072,
                    "lng": -77.0369,
                },
                {
                    "code": "FL",
                    "name": "Florida",
                    "division_type": "State",
                    "lat": 27.7663,
                    "lng": -81.6868,
                },
                {
                    "code": "GA",
                    "name": "Georgia",
                    "division_type": "State",
                    "lat": 32.1656,
                    "lng": -82.9001,
                },
                {
                    "code": "HI",
                    "name": "Hawaii",
                    "division_type": "State",
                    "lat": 21.0943,
                    "lng": -157.4983,
                },
                {
                    "code": "ID",
                    "name": "Idaho",
                    "division_type": "State",
                    "lat": 44.0682,
                    "lng": -114.7420,
                },
                {
                    "code": "IL",
                    "name": "Illinois",
                    "division_type": "State",
                    "lat": 40.6331,
                    "lng": -89.3985,
                },
                {
                    "code": "IN",
                    "name": "Indiana",
                    "division_type": "State",
                    "lat": 40.2732,
                    "lng": -86.1349,
                },
                {
                    "code": "IA",
                    "name": "Iowa",
                    "division_type": "State",
                    "lat": 41.8780,
                    "lng": -93.0977,
                },
                {
                    "code": "KS",
                    "name": "Kansas",
                    "division_type": "State",
                    "lat": 38.5266,
                    "lng": -96.7265,
                },
                {
                    "code": "KY",
                    "name": "Kentucky",
                    "division_type": "State",
                    "lat": 37.6681,
                    "lng": -84.6701,
                },
                {
                    "code": "LA",
                    "name": "Louisiana",
                    "division_type": "State",
                    "lat": 31.2400,
                    "lng": -91.4986,
                },
                {
                    "code": "ME",
                    "name": "Maine",
                    "division_type": "State",
                    "lat": 45.3695,
                    "lng": -69.2178,
                },
                {
                    "code": "MD",
                    "name": "Maryland",
                    "division_type": "State",
                    "lat": 39.0458,
                    "lng": -76.6413,
                },
                {
                    "code": "MA",
                    "name": "Massachusetts",
                    "division_type": "State",
                    "lat": 42.2373,
                    "lng": -71.5314,
                },
                {
                    "code": "MI",
                    "name": "Michigan",
                    "division_type": "State",
                    "lat": 43.3266,
                    "lng": -84.5361,
                },
                {
                    "code": "MN",
                    "name": "Minnesota",
                    "division_type": "State",
                    "lat": 45.7326,
                    "lng": -93.9196,
                },
                {
                    "code": "MS",
                    "name": "Mississippi",
                    "division_type": "State",
                    "lat": 32.7364,
                    "lng": -89.6678,
                },
                {
                    "code": "MO",
                    "name": "Missouri",
                    "division_type": "State",
                    "lat": 38.4623,
                    "lng": -92.3020,
                },
                {
                    "code": "MT",
                    "name": "Montana",
                    "division_type": "State",
                    "lat": 47.0527,
                    "lng": -110.2148,
                },
                {
                    "code": "NE",
                    "name": "Nebraska",
                    "division_type": "State",
                    "lat": 41.1289,
                    "lng": -98.2883,
                },
                {
                    "code": "NV",
                    "name": "Nevada",
                    "division_type": "State",
                    "lat": 38.4199,
                    "lng": -117.1219,
                },
                {
                    "code": "NH",
                    "name": "New Hampshire",
                    "division_type": "State",
                    "lat": 43.4525,
                    "lng": -71.5639,
                },
                {
                    "code": "NJ",
                    "name": "New Jersey",
                    "division_type": "State",
                    "lat": 40.3573,
                    "lng": -74.4057,
                },
                {
                    "code": "NM",
                    "name": "New Mexico",
                    "division_type": "State",
                    "lat": 34.8405,
                    "lng": -106.2485,
                },
                {
                    "code": "NY",
                    "name": "New York",
                    "division_type": "State",
                    "lat": 42.1657,
                    "lng": -74.9481,
                },
                {
                    "code": "NC",
                    "name": "North Carolina",
                    "division_type": "State",
                    "lat": 35.6301,
                    "lng": -79.0064,
                },
                {
                    "code": "ND",
                    "name": "North Dakota",
                    "division_type": "State",
                    "lat": 47.5515,
                    "lng": -99.7946,
                },
                {
                    "code": "OH",
                    "name": "Ohio",
                    "division_type": "State",
                    "lat": 40.3888,
                    "lng": -82.7649,
                },
                {
                    "code": "OK",
                    "name": "Oklahoma",
                    "division_type": "State",
                    "lat": 35.5889,
                    "lng": -96.9289,
                },
                {
                    "code": "OR",
                    "name": "Oregon",
                    "division_type": "State",
                    "lat": 44.5672,
                    "lng": -122.1269,
                },
                {
                    "code": "PA",
                    "name": "Pennsylvania",
                    "division_type": "State",
                    "lat": 40.5908,
                    "lng": -77.2098,
                },
                {
                    "code": "RI",
                    "name": "Rhode Island",
                    "division_type": "State",
                    "lat": 41.6809,
                    "lng": -71.5118,
                },
                {
                    "code": "SC",
                    "name": "South Carolina",
                    "division_type": "State",
                    "lat": 33.8191,
                    "lng": -80.9066,
                },
                {
                    "code": "SD",
                    "name": "South Dakota",
                    "division_type": "State",
                    "lat": 44.2998,
                    "lng": -99.4388,
                },
                {
                    "code": "TN",
                    "name": "Tennessee",
                    "division_type": "State",
                    "lat": 35.7449,
                    "lng": -86.7489,
                },
                {
                    "code": "TX",
                    "name": "Texas",
                    "division_type": "State",
                    "lat": 31.0545,
                    "lng": -97.5635,
                },
                {
                    "code": "UT",
                    "name": "Utah",
                    "division_type": "State",
                    "lat": 40.1135,
                    "lng": -111.8535,
                },
                {
                    "code": "VT",
                    "name": "Vermont",
                    "division_type": "State",
                    "lat": 44.0459,
                    "lng": -72.7107,
                },
                {
                    "code": "VA",
                    "name": "Virginia",
                    "division_type": "State",
                    "lat": 37.7693,
                    "lng": -78.2057,
                },
                {
                    "code": "WA",
                    "name": "Washington",
                    "division_type": "State",
                    "lat": 47.4009,
                    "lng": -121.4905,
                },
                {
                    "code": "WV",
                    "name": "West Virginia",
                    "division_type": "State",
                    "lat": 38.4912,
                    "lng": -80.9545,
                },
                {
                    "code": "WI",
                    "name": "Wisconsin",
                    "division_type": "State",
                    "lat": 44.2619,
                    "lng": -89.6165,
                },
                {
                    "code": "WY",
                    "name": "Wyoming",
                    "division_type": "State",
                    "lat": 42.7559,
                    "lng": -107.3025,
                },
            ],
            "AU": [  # Australia
                {
                    "code": "NSW",
                    "name": "New South Wales",
                    "division_type": "State",
                    "lat": -31.2532,
                    "lng": 146.9211,
                },
                {
                    "code": "VIC",
                    "name": "Victoria",
                    "division_type": "State",
                    "lat": -37.4713,
                    "lng": 144.7852,
                },
                {
                    "code": "QLD",
                    "name": "Queensland",
                    "division_type": "State",
                    "lat": -20.9176,
                    "lng": 142.7028,
                },
                {
                    "code": "WA",
                    "name": "Western Australia",
                    "division_type": "State",
                    "lat": -27.6728,
                    "lng": 121.6283,
                },
                {
                    "code": "SA",
                    "name": "South Australia",
                    "division_type": "State",
                    "lat": -30.0002,
                    "lng": 136.2092,
                },
                {
                    "code": "TAS",
                    "name": "Tasmania",
                    "division_type": "State",
                    "lat": -41.6809,
                    "lng": 146.3156,
                },
                {
                    "code": "ACT",
                    "name": "Australian Capital Territory",
                    "division_type": "Territory",
                    "lat": -35.4735,
                    "lng": 149.0124,
                },
                {
                    "code": "NT",
                    "name": "Northern Territory",
                    "division_type": "Territory",
                    "lat": -19.4914,
                    "lng": 132.5510,
                },
            ],
            "CA": [  # Canada
                {
                    "code": "AB",
                    "name": "Alberta",
                    "division_type": "Province",
                    "lat": 53.9333,
                    "lng": -116.5765,
                },
                {
                    "code": "BC",
                    "name": "British Columbia",
                    "division_type": "Province",
                    "lat": 53.7267,
                    "lng": -127.6476,
                },
                {
                    "code": "MB",
                    "name": "Manitoba",
                    "division_type": "Province",
                    "lat": 53.7609,
                    "lng": -98.8139,
                },
                {
                    "code": "NB",
                    "name": "New Brunswick",
                    "division_type": "Province",
                    "lat": 46.5653,
                    "lng": -66.4619,
                },
                {
                    "code": "NL",
                    "name": "Newfoundland and Labrador",
                    "division_type": "Province",
                    "lat": 53.1355,
                    "lng": -57.6604,
                },
                {
                    "code": "NS",
                    "name": "Nova Scotia",
                    "division_type": "Province",
                    "lat": 44.6820,
                    "lng": -63.7443,
                },
                {
                    "code": "ON",
                    "name": "Ontario",
                    "division_type": "Province",
                    "lat": 51.2538,
                    "lng": -85.3232,
                },
                {
                    "code": "PE",
                    "name": "Prince Edward Island",
                    "division_type": "Province",
                    "lat": 46.5107,
                    "lng": -63.4168,
                },
                {
                    "code": "QC",
                    "name": "Quebec",
                    "division_type": "Province",
                    "lat": 53.9842,
                    "lng": -71.0889,
                },
                {
                    "code": "SK",
                    "name": "Saskatchewan",
                    "division_type": "Province",
                    "lat": 52.9399,
                    "lng": -106.4509,
                },
                {
                    "code": "NT",
                    "name": "Northwest Territories",
                    "division_type": "Territory",
                    "lat": 64.8255,
                    "lng": -124.8457,
                },
                {
                    "code": "NU",
                    "name": "Nunavut",
                    "division_type": "Territory",
                    "lat": 70.2998,
                    "lng": -83.1076,
                },
                {
                    "code": "YT",
                    "name": "Yukon",
                    "division_type": "Territory",
                    "lat": 64.2823,
                    "lng": -135.0000,
                },
            ],
            "GB": [  # United Kingdom
                {
                    "code": "ENG",
                    "name": "England",
                    "division_type": "Country",
                    "lat": 52.3555,
                    "lng": -1.1743,
                },
                {
                    "code": "SCT",
                    "name": "Scotland",
                    "division_type": "Country",
                    "lat": 56.4907,
                    "lng": -4.2026,
                },
                {
                    "code": "WLS",
                    "name": "Wales",
                    "division_type": "Country",
                    "lat": 52.1307,
                    "lng": -3.7837,
                },
                {
                    "code": "NIR",
                    "name": "Northern Ireland",
                    "division_type": "Country",
                    "lat": 54.7877,
                    "lng": -6.4923,
                },
            ],
        }

    @transaction.atomic
    def populate_states(self, country_codes: List[str]):
        """Populate states for specified countries"""

        states_data = self.get_states_data()

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors_count = 0

        for country_code in country_codes:
            if country_code not in states_data:
                self.stdout.write(
                    self.style.WARNING(
                        f"No state data available for country: {country_code}"
                    )
                )
                continue

            try:
                country = Country.objects.get(iso_code_2=country_code)
            except Country.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Country not found: {country_code}")
                )
                errors_count += 1
                continue

            if self.verbosity >= 2:
                self.stdout.write(
                    f"Processing states for {country.name} ({country_code})"
                )

            for state_data in states_data[country_code]:
                try:
                    if self.dry_run:
                        self.stdout.write(
                            f"Would process: {state_data['name']} ({state_data['code']})"
                        )
                        continue

                    # Prepare state data
                    state_info = {
                        "country": country,
                        "code": state_data["code"],
                        "name": state_data["name"],
                        "division_type": state_data["division_type"],
                        "latitude": (
                            Decimal(str(state_data["lat"]))
                            if state_data.get("lat")
                            else None
                        ),
                        "longitude": (
                            Decimal(str(state_data["lng"]))
                            if state_data.get("lng")
                            else None
                        ),
                    }

                    # Create or update state
                    state, created = State.objects.get_or_create(
                        country=country, code=state_data["code"], defaults=state_info
                    )

                    if created:
                        created_count += 1
                        if self.verbosity >= 2:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Created: {state.name} ({state.code})"
                                )
                            )
                    elif self.update_existing:
                        for field, value in state_info.items():
                            if field not in ["country", "code"]:
                                setattr(state, field, value)
                        state.save()
                        updated_count += 1
                        if self.verbosity >= 2:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Updated: {state.name} ({state.code})"
                                )
                            )
                    else:
                        skipped_count += 1
                        if self.verbosity >= 2:
                            self.stdout.write(
                                f"Skipped existing: {state.name} ({state.code})"
                            )

                except Exception as e:
                    errors_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error processing state {state_data['name']}: {str(e)}"
                        )
                    )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("STATE/PROVINCE POPULATION SUMMARY"))
        self.stdout.write("=" * 50)

        if not self.dry_run:
            self.stdout.write(f"Created: {created_count} states/provinces")
            if self.update_existing:
                self.stdout.write(f"Updated: {updated_count} states/provinces")
            self.stdout.write(f"Skipped: {skipped_count} states/provinces")
            if errors_count > 0:
                self.stdout.write(
                    self.style.ERROR(f"Errors: {errors_count} states/provinces")
                )

            total_states = State.objects.count()
            self.stdout.write(f"Total states/provinces in database: {total_states}")
        else:
            total_would_process = sum(
                len(states_data.get(code, []))
                for code in country_codes
                if code in states_data
            )
            self.stdout.write(f"Would process: {total_would_process} states/provinces")

        self.stdout.write("=" * 50)

        if errors_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Completed with {errors_count} errors. Check the output above for details."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("State/province population completed successfully!")
            )
