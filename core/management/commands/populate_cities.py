"""
Django management command to populate City model with strategic city data

This command populates cities using a strategic approach:
1. National capitals
2. State/province capitals
3. Major cities (population > 100k)
4. Important economic/tourist centers

The goal is comprehensive coverage without database bloat.

Supported Countries: US, AU, CA, GB (matching our State data)

Usage:
    python manage.py populate_cities [--countries=US,AU] [--min-population=50000]
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import City, Country, State


class Command(BaseCommand):
    help = "Populate City model with strategic city data for major countries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--countries",
            type=str,
            help="Comma-separated list of country codes (e.g., US,AU,CA,GB)",
        )
        parser.add_argument(
            "--min-population",
            type=int,
            default=50000,
            help="Minimum population for cities to include (default: 50000)",
        )
        parser.add_argument(
            "--include-capitals",
            action="store_true",
            default=True,
            help="Include all state/province capitals regardless of population",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing cities instead of skipping them",
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
        self.min_population = options["min_population"]
        self.include_capitals = options["include_capitals"]

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
            # Default to countries we have state data for
            country_codes = ["US", "AU", "CA", "GB"]

        try:
            self.populate_cities(country_codes)
        except Exception as e:
            raise CommandError(f"Error populating cities: {str(e)}")

    def get_cities_data(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Curated city data organized by country and state

        Focus on:
        1. National capitals
        2. State/province capitals
        3. Major cities (100k+ population)
        4. Important economic centers

        Returns: {country_code: {state_code: [city_data_list]}}
        """
        return {
            "US": {
                # Major US cities by state
                "CA": [
                    {
                        "name": "Los Angeles",
                        "pop": 3971883,
                        "lat": 34.0522,
                        "lng": -118.2437,
                        "type": "Major City",
                    },
                    {
                        "name": "San Diego",
                        "pop": 1423851,
                        "lat": 32.7157,
                        "lng": -117.1611,
                        "type": "Major City",
                    },
                    {
                        "name": "San Jose",
                        "pop": 1013240,
                        "lat": 37.3382,
                        "lng": -121.8863,
                        "type": "Major City",
                    },
                    {
                        "name": "San Francisco",
                        "pop": 873965,
                        "lat": 37.7749,
                        "lng": -122.4194,
                        "type": "Major City",
                    },
                    {
                        "name": "Fresno",
                        "pop": 542107,
                        "lat": 36.7378,
                        "lng": -119.7871,
                        "type": "Major City",
                    },
                    {
                        "name": "Sacramento",
                        "pop": 513624,
                        "lat": 38.5816,
                        "lng": -121.4944,
                        "type": "State Capital",
                        "capital": True,
                    },
                ],
                "TX": [
                    {
                        "name": "Houston",
                        "pop": 2304580,
                        "lat": 29.7604,
                        "lng": -95.3698,
                        "type": "Major City",
                    },
                    {
                        "name": "San Antonio",
                        "pop": 1547253,
                        "lat": 29.4241,
                        "lng": -98.4936,
                        "type": "Major City",
                    },
                    {
                        "name": "Dallas",
                        "pop": 1304379,
                        "lat": 32.7767,
                        "lng": -96.7970,
                        "type": "Major City",
                    },
                    {
                        "name": "Austin",
                        "pop": 965872,
                        "lat": 30.2672,
                        "lng": -97.7431,
                        "type": "State Capital",
                        "capital": True,
                    },
                    {
                        "name": "Fort Worth",
                        "pop": 918915,
                        "lat": 32.7555,
                        "lng": -97.3308,
                        "type": "Major City",
                    },
                ],
                "FL": [
                    {
                        "name": "Jacksonville",
                        "pop": 911507,
                        "lat": 32.0835,
                        "lng": -81.6934,
                        "type": "Major City",
                    },
                    {
                        "name": "Miami",
                        "pop": 442241,
                        "lat": 25.7617,
                        "lng": -80.1918,
                        "type": "Major City",
                    },
                    {
                        "name": "Tampa",
                        "pop": 387050,
                        "lat": 27.9506,
                        "lng": -82.4572,
                        "type": "Major City",
                    },
                    {
                        "name": "Orlando",
                        "pop": 307573,
                        "lat": 28.5383,
                        "lng": -81.3792,
                        "type": "Major City",
                    },
                    {
                        "name": "Tallahassee",
                        "pop": 194500,
                        "lat": 30.4518,
                        "lng": -84.27277,
                        "type": "State Capital",
                        "capital": True,
                    },
                ],
                "NY": [
                    {
                        "name": "New York City",
                        "pop": 8336817,
                        "lat": 40.7128,
                        "lng": -74.0060,
                        "type": "Major City",
                    },
                    {
                        "name": "Buffalo",
                        "pop": 278349,
                        "lat": 42.8864,
                        "lng": -78.8784,
                        "type": "Major City",
                    },
                    {
                        "name": "Rochester",
                        "pop": 211328,
                        "lat": 43.1566,
                        "lng": -77.6088,
                        "type": "Major City",
                    },
                    {
                        "name": "Albany",
                        "pop": 97856,
                        "lat": 42.6526,
                        "lng": -73.7562,
                        "type": "State Capital",
                        "capital": True,
                    },
                ],
                "IL": [
                    {
                        "name": "Chicago",
                        "pop": 2746388,
                        "lat": 41.8781,
                        "lng": -87.6298,
                        "type": "Major City",
                    },
                    {
                        "name": "Aurora",
                        "pop": 180542,
                        "lat": 41.7606,
                        "lng": -88.3201,
                        "type": "Major City",
                    },
                    {
                        "name": "Springfield",
                        "pop": 114394,
                        "lat": 39.7817,
                        "lng": -89.6501,
                        "type": "State Capital",
                        "capital": True,
                    },
                ],
                "DC": [
                    {
                        "name": "Washington",
                        "pop": 705749,
                        "lat": 38.9072,
                        "lng": -77.0369,
                        "type": "National Capital",
                        "capital": True,
                        "national_capital": True,
                    },
                ],
            },
            "AU": {
                # Major Australian cities by state
                "NSW": [
                    {
                        "name": "Sydney",
                        "pop": 5312163,
                        "lat": -33.8688,
                        "lng": 151.2093,
                        "type": "State Capital",
                        "capital": True,
                    },
                    {
                        "name": "Newcastle",
                        "pop": 322278,
                        "lat": -32.9283,
                        "lng": 151.7817,
                        "type": "Major City",
                    },
                    {
                        "name": "Wollongong",
                        "pop": 302739,
                        "lat": -34.4278,
                        "lng": 150.8931,
                        "type": "Major City",
                    },
                ],
                "VIC": [
                    {
                        "name": "Melbourne",
                        "pop": 5078193,
                        "lat": -37.8136,
                        "lng": 144.9631,
                        "type": "State Capital",
                        "capital": True,
                    },
                    {
                        "name": "Geelong",
                        "pop": 253269,
                        "lat": -38.1499,
                        "lng": 144.3617,
                        "type": "Major City",
                    },
                ],
                "QLD": [
                    {
                        "name": "Brisbane",
                        "pop": 2560720,
                        "lat": -27.4698,
                        "lng": 153.0251,
                        "type": "State Capital",
                        "capital": True,
                    },
                    {
                        "name": "Gold Coast",
                        "pop": 679127,
                        "lat": -28.0167,
                        "lng": 153.4000,
                        "type": "Major City",
                    },
                    {
                        "name": "Townsville",
                        "pop": 180820,
                        "lat": -19.2590,
                        "lng": 146.8169,
                        "type": "Major City",
                    },
                ],
                "WA": [
                    {
                        "name": "Perth",
                        "pop": 2125114,
                        "lat": -31.9505,
                        "lng": 115.8605,
                        "type": "State Capital",
                        "capital": True,
                    },
                ],
                "SA": [
                    {
                        "name": "Adelaide",
                        "pop": 1402393,
                        "lat": -34.9285,
                        "lng": 138.6007,
                        "type": "State Capital",
                        "capital": True,
                    },
                ],
                "TAS": [
                    {
                        "name": "Hobart",
                        "pop": 253691,
                        "lat": -42.8821,
                        "lng": 147.3272,
                        "type": "State Capital",
                        "capital": True,
                    },
                ],
                "ACT": [
                    {
                        "name": "Canberra",
                        "pop": 453558,
                        "lat": -35.2809,
                        "lng": 149.1300,
                        "type": "National Capital",
                        "capital": True,
                        "national_capital": True,
                    },
                ],
                "NT": [
                    {
                        "name": "Darwin",
                        "pop": 148564,
                        "lat": -12.4634,
                        "lng": 130.8456,
                        "type": "Territory Capital",
                        "capital": True,
                    },
                ],
            },
            "CA": {
                # Major Canadian cities by province
                "ON": [
                    {
                        "name": "Toronto",
                        "pop": 2930000,
                        "lat": 43.6532,
                        "lng": -79.3832,
                        "type": "Major City",
                    },
                    {
                        "name": "Ottawa",
                        "pop": 994837,
                        "lat": 45.4215,
                        "lng": -75.6972,
                        "type": "National Capital",
                        "capital": True,
                        "national_capital": True,
                    },
                    {
                        "name": "Hamilton",
                        "pop": 536917,
                        "lat": 43.2557,
                        "lng": -79.8711,
                        "type": "Major City",
                    },
                ],
                "QC": [
                    {
                        "name": "Montreal",
                        "pop": 1762949,
                        "lat": 45.5017,
                        "lng": -73.5673,
                        "type": "Major City",
                    },
                    {
                        "name": "Quebec City",
                        "pop": 542298,
                        "lat": 46.8139,
                        "lng": -71.2080,
                        "type": "Provincial Capital",
                        "capital": True,
                    },
                ],
                "BC": [
                    {
                        "name": "Vancouver",
                        "pop": 675218,
                        "lat": 49.2827,
                        "lng": -123.1207,
                        "type": "Major City",
                    },
                    {
                        "name": "Victoria",
                        "pop": 91867,
                        "lat": 48.4284,
                        "lng": -123.3656,
                        "type": "Provincial Capital",
                        "capital": True,
                    },
                ],
                "AB": [
                    {
                        "name": "Calgary",
                        "pop": 1336000,
                        "lat": 51.0447,
                        "lng": -114.0719,
                        "type": "Major City",
                    },
                    {
                        "name": "Edmonton",
                        "pop": 1010899,
                        "lat": 53.5461,
                        "lng": -113.4938,
                        "type": "Provincial Capital",
                        "capital": True,
                    },
                ],
            },
            "GB": {
                # Major UK cities by country/region
                "ENG": [
                    {
                        "name": "London",
                        "pop": 9648110,
                        "lat": 51.5074,
                        "lng": -0.1278,
                        "type": "National Capital",
                        "capital": True,
                        "national_capital": True,
                    },
                    {
                        "name": "Birmingham",
                        "pop": 1141816,
                        "lat": 52.4862,
                        "lng": -1.8904,
                        "type": "Major City",
                    },
                    {
                        "name": "Manchester",
                        "pop": 547000,
                        "lat": 53.4808,
                        "lng": -2.2426,
                        "type": "Major City",
                    },
                    {
                        "name": "Liverpool",
                        "pop": 498042,
                        "lat": 53.4084,
                        "lng": -2.9916,
                        "type": "Major City",
                    },
                    {
                        "name": "Leeds",
                        "pop": 474632,
                        "lat": 53.8008,
                        "lng": -1.5491,
                        "type": "Major City",
                    },
                ],
                "SCT": [
                    {
                        "name": "Glasgow",
                        "pop": 635640,
                        "lat": 55.8642,
                        "lng": -4.2518,
                        "type": "Major City",
                    },
                    {
                        "name": "Edinburgh",
                        "pop": 527620,
                        "lat": 55.9533,
                        "lng": -3.1883,
                        "type": "Country Capital",
                        "capital": True,
                    },
                ],
                "WLS": [
                    {
                        "name": "Cardiff",
                        "pop": 362756,
                        "lat": 51.4816,
                        "lng": -3.1791,
                        "type": "Country Capital",
                        "capital": True,
                    },
                    {
                        "name": "Swansea",
                        "pop": 246563,
                        "lat": 51.6214,
                        "lng": -3.9436,
                        "type": "Major City",
                    },
                ],
                "NIR": [
                    {
                        "name": "Belfast",
                        "pop": 343542,
                        "lat": 54.5973,
                        "lng": -5.9301,
                        "type": "Country Capital",
                        "capital": True,
                    },
                ],
            },
        }

    def normalize_city_data(
        self, city_data: Dict[str, Any], state: State
    ) -> Dict[str, Any]:
        """Normalize city data for our model"""

        # Determine city classification
        is_state_capital = city_data.get("capital", False)
        is_national_capital = city_data.get("national_capital", False)
        is_major_city = city_data.get("pop", 0) >= self.min_population

        normalized = {
            "state": state,
            "name": city_data["name"],
            "population": city_data.get("pop"),
            "latitude": (
                Decimal(str(city_data["lat"])) if city_data.get("lat") else None
            ),
            "longitude": (
                Decimal(str(city_data["lng"])) if city_data.get("lng") else None
            ),
            "city_type": city_data.get("type", "City"),
            "is_state_capital": is_state_capital,
            "is_national_capital": is_national_capital,
            "is_major_city": is_major_city,
            "data_source": "manual",
            "data_quality": "high",
        }

        return normalized

    @transaction.atomic
    def populate_cities(self, country_codes: List[str]):
        """Populate cities for specified countries"""

        cities_data = self.get_cities_data()

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors_count = 0

        for country_code in country_codes:
            if country_code not in cities_data:
                self.stdout.write(
                    self.style.WARNING(
                        f"No city data available for country: {country_code}"
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
                    f"Processing cities for {country.name} ({country_code})"
                )

            country_cities = cities_data[country_code]

            for state_code, city_list in country_cities.items():
                try:
                    state = State.objects.get(country=country, code=state_code)
                except State.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"State not found: {state_code} in {country_code}"
                        )
                    )
                    errors_count += 1
                    continue

                for city_data in city_list:
                    try:
                        # Apply population filter unless it's a capital
                        if not self.include_capitals or not city_data.get(
                            "capital", False
                        ):
                            if city_data.get("pop", 0) < self.min_population:
                                if self.verbosity >= 2:
                                    self.stdout.write(
                                        f"Skipping {city_data['name']} (pop: {city_data.get('pop', 0)} < {self.min_population})"
                                    )
                                skipped_count += 1
                                continue

                        if self.dry_run:
                            self.stdout.write(
                                f"Would process: {city_data['name']}, {state.name} (pop: {city_data.get('pop', 'N/A')})"
                            )
                            continue

                        # Prepare city data
                        city_info = self.normalize_city_data(city_data, state)

                        # Create or update city
                        city, created = City.objects.get_or_create(
                            state=state, name=city_data["name"], defaults=city_info
                        )

                        if created:
                            created_count += 1
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Created: {city.name}, {city.state.name}"
                                    )
                                )
                        elif self.update_existing:
                            for field, value in city_info.items():
                                if field not in ["state", "name"]:
                                    setattr(city, field, value)
                            city.save()
                            updated_count += 1
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Updated: {city.name}, {city.state.name}"
                                    )
                                )
                        else:
                            skipped_count += 1
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    f"Skipped existing: {city.name}, {city.state.name}"
                                )

                    except Exception as e:
                        errors_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error processing city {city_data['name']}: {str(e)}"
                            )
                        )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("CITY POPULATION SUMMARY"))
        self.stdout.write("=" * 50)

        if not self.dry_run:
            self.stdout.write(f"Created: {created_count} cities")
            if self.update_existing:
                self.stdout.write(f"Updated: {updated_count} cities")
            self.stdout.write(f"Skipped: {skipped_count} cities")
            if errors_count > 0:
                self.stdout.write(self.style.ERROR(f"Errors: {errors_count} cities"))

            total_cities = City.objects.count()
            self.stdout.write(f"Total cities in database: {total_cities}")

            # Show breakdown by country
            for country_code in country_codes:
                if country_code in cities_data:
                    try:
                        country = Country.objects.get(iso_code_2=country_code)
                        country_city_count = City.objects.filter(
                            state__country=country
                        ).count()
                        self.stdout.write(
                            f"  {country.name}: {country_city_count} cities"
                        )
                    except Country.DoesNotExist:
                        pass
        else:
            total_would_process = 0
            for country_code in country_codes:
                if country_code in cities_data:
                    for state_cities in cities_data[country_code].values():
                        total_would_process += len(state_cities)
            self.stdout.write(f"Would process: {total_would_process} cities")

        self.stdout.write("=" * 50)

        if errors_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Completed with {errors_count} errors. Check the output above for details."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("City population completed successfully!")
            )
