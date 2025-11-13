"""
Django management command to populate comprehensive Australian city data

This command focuses heavily on South Australia and Victoria with comprehensive
coverage including regional centers, towns, and business hubs. Other states
maintain basic major city coverage.

Special focus areas:
- South Australia: Complete coverage from Adelaide metro to regional towns
- Victoria: Complete coverage from Melbourne metro to regional centers
- Other states: Major cities and capitals only

Usage:
    python manage.py populate_au_cities [--update-existing]
"""

from decimal import Decimal
from typing import Any, Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import City, Country, State


class Command(BaseCommand):
    help = "Populate comprehensive Australian city data with SA/VIC focus"

    def add_arguments(self, parser):
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

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE: No changes will be made")
            )

        try:
            self.populate_australian_cities()
        except Exception as e:
            raise CommandError(f"Error populating Australian cities: {str(e)}")

    def get_comprehensive_au_cities(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Comprehensive Australian city data with special focus on SA and VIC

        Categories included:
        - State capitals
        - Major metropolitan areas
        - Regional cities (10k+ population)
        - Important towns and business centers
        - Tourist destinations
        - Mining and agricultural centers
        """
        return {
            "SA": [  # SOUTH AUSTRALIA - COMPREHENSIVE COVERAGE
                # Adelaide Metropolitan Area
                {
                    "name": "Adelaide",
                    "pop": 1402393,
                    "lat": -34.9285,
                    "lng": 138.6007,
                    "type": "State Capital",
                    "capital": True,
                },
                {
                    "name": "Salisbury",
                    "pop": 147263,
                    "lat": -34.7581,
                    "lng": 138.6424,
                    "type": "Metropolitan",
                },
                {
                    "name": "Onkaparinga",
                    "pop": 176001,
                    "lat": -35.1311,
                    "lng": 138.5242,
                    "type": "Metropolitan",
                },
                {
                    "name": "Tea Tree Gully",
                    "pop": 108227,
                    "lat": -34.8328,
                    "lng": 138.7342,
                    "type": "Metropolitan",
                },
                {
                    "name": "Port Adelaide Enfield",
                    "pop": 119216,
                    "lat": -34.8476,
                    "lng": 138.5084,
                    "type": "Metropolitan",
                },
                {
                    "name": "Marion",
                    "pop": 93598,
                    "lat": -35.0167,
                    "lng": 138.5500,
                    "type": "Metropolitan",
                },
                {
                    "name": "Charles Sturt",
                    "pop": 118956,
                    "lat": -34.9167,
                    "lng": 138.5167,
                    "type": "Metropolitan",
                },
                # Major Regional Cities
                {
                    "name": "Mount Gambier",
                    "pop": 29639,
                    "lat": -37.8297,
                    "lng": 140.7832,
                    "type": "Regional City",
                },
                {
                    "name": "Whyalla",
                    "pop": 21742,
                    "lat": -33.0333,
                    "lng": 137.5833,
                    "type": "Regional City",
                },
                {
                    "name": "Murray Bridge",
                    "pop": 21485,
                    "lat": -35.1190,
                    "lng": 139.2757,
                    "type": "Regional City",
                },
                {
                    "name": "Port Lincoln",
                    "pop": 16467,
                    "lat": -34.7289,
                    "lng": 135.8655,
                    "type": "Regional City",
                },
                {
                    "name": "Port Augusta",
                    "pop": 14235,
                    "lat": -32.4911,
                    "lng": 137.7669,
                    "type": "Regional City",
                },
                {
                    "name": "Victor Harbor",
                    "pop": 14708,
                    "lat": -35.5522,
                    "lng": 138.6211,
                    "type": "Regional City",
                },
                {
                    "name": "Gawler",
                    "pop": 26484,
                    "lat": -34.6042,
                    "lng": 138.7442,
                    "type": "Regional City",
                },
                {
                    "name": "Port Pirie",
                    "pop": 14188,
                    "lat": -33.1906,
                    "lng": 138.0170,
                    "type": "Regional City",
                },
                # Important Towns and Centers
                {
                    "name": "Kadina",
                    "pop": 4652,
                    "lat": -33.9598,
                    "lng": 137.7167,
                    "type": "Town",
                },
                {
                    "name": "Naracoorte",
                    "pop": 5043,
                    "lat": -36.9581,
                    "lng": 140.7395,
                    "type": "Town",
                },
                {
                    "name": "Berri",
                    "pop": 4400,
                    "lat": -34.2833,
                    "lng": 140.6000,
                    "type": "Town",
                },
                {
                    "name": "Renmark",
                    "pop": 7491,
                    "lat": -34.1739,
                    "lng": 140.7481,
                    "type": "Town",
                },
                {
                    "name": "Loxton",
                    "pop": 4781,
                    "lat": -34.4500,
                    "lng": 140.5667,
                    "type": "Town",
                },
                {
                    "name": "Millicent",
                    "pop": 4908,
                    "lat": -37.5981,
                    "lng": 140.3517,
                    "type": "Town",
                },
                {
                    "name": "Ceduna",
                    "pop": 2289,
                    "lat": -32.1281,
                    "lng": 133.6811,
                    "type": "Town",
                },
                {
                    "name": "Clare",
                    "pop": 3930,
                    "lat": -33.8314,
                    "lng": 138.6081,
                    "type": "Town",
                },
                {
                    "name": "Tanunda",
                    "pop": 4404,
                    "lat": -34.5236,
                    "lng": 138.9597,
                    "type": "Town",
                },
                {
                    "name": "Nuriootpa",
                    "pop": 4564,
                    "lat": -34.4681,
                    "lng": 138.9914,
                    "type": "Town",
                },
                {
                    "name": "Angaston",
                    "pop": 2137,
                    "lat": -34.5058,
                    "lng": 139.0472,
                    "type": "Town",
                },
                {
                    "name": "Wallaroo",
                    "pop": 4032,
                    "lat": -33.9339,
                    "lng": 137.6367,
                    "type": "Town",
                },
                {
                    "name": "Moonta",
                    "pop": 4498,
                    "lat": -34.0622,
                    "lng": 137.5892,
                    "type": "Town",
                },
                {
                    "name": "Yorketown",
                    "pop": 676,
                    "lat": -35.0142,
                    "lng": 137.6092,
                    "type": "Town",
                },
                {
                    "name": "Kingscote",
                    "pop": 1790,
                    "lat": -35.6542,
                    "lng": 137.6367,
                    "type": "Town",
                },
                {
                    "name": "Penola",
                    "pop": 1317,
                    "lat": -37.3750,
                    "lng": 140.8347,
                    "type": "Town",
                },
                {
                    "name": "Keith",
                    "pop": 1203,
                    "lat": -36.1000,
                    "lng": 140.3500,
                    "type": "Town",
                },
                {
                    "name": "Bordertown",
                    "pop": 2800,
                    "lat": -36.3167,
                    "lng": 140.7667,
                    "type": "Town",
                },
                {
                    "name": "Tailem Bend",
                    "pop": 1681,
                    "lat": -35.2500,
                    "lng": 139.4500,
                    "type": "Town",
                },
                {
                    "name": "Meningie",
                    "pop": 940,
                    "lat": -35.7000,
                    "lng": 139.3500,
                    "type": "Town",
                },
                {
                    "name": "Wudinna",
                    "pop": 599,
                    "lat": -33.0500,
                    "lng": 135.4500,
                    "type": "Town",
                },
                {
                    "name": "Streaky Bay",
                    "pop": 1278,
                    "lat": -32.7978,
                    "lng": 134.2092,
                    "type": "Town",
                },
                {
                    "name": "Coober Pedy",
                    "pop": 1695,
                    "lat": -29.0139,
                    "lng": 134.7567,
                    "type": "Town",
                },
                {
                    "name": "Roxby Downs",
                    "pop": 4055,
                    "lat": -30.5547,
                    "lng": 136.8839,
                    "type": "Mining Town",
                },
            ],
            "VIC": [  # VICTORIA - COMPREHENSIVE COVERAGE
                # Melbourne Metropolitan Area
                {
                    "name": "Melbourne",
                    "pop": 5078193,
                    "lat": -37.8136,
                    "lng": 144.9631,
                    "type": "State Capital",
                    "capital": True,
                },
                {
                    "name": "Casey",
                    "pop": 340419,
                    "lat": -38.0667,
                    "lng": 145.2500,
                    "type": "Metropolitan",
                },
                {
                    "name": "Hume",
                    "pop": 224394,
                    "lat": -37.6500,
                    "lng": 144.9167,
                    "type": "Metropolitan",
                },
                {
                    "name": "Wyndham",
                    "pop": 270487,
                    "lat": -37.9000,
                    "lng": 144.6667,
                    "type": "Metropolitan",
                },
                {
                    "name": "Monash",
                    "pop": 200077,
                    "lat": -37.8833,
                    "lng": 145.1333,
                    "type": "Metropolitan",
                },
                {
                    "name": "Knox",
                    "pop": 164385,
                    "lat": -37.8500,
                    "lng": 145.2333,
                    "type": "Metropolitan",
                },
                {
                    "name": "Moreland",
                    "pop": 181725,
                    "lat": -37.7500,
                    "lng": 144.9667,
                    "type": "Metropolitan",
                },
                {
                    "name": "Frankston",
                    "pop": 141845,
                    "lat": -38.1500,
                    "lng": 145.1167,
                    "type": "Metropolitan",
                },
                # Major Regional Cities
                {
                    "name": "Geelong",
                    "pop": 253269,
                    "lat": -38.1499,
                    "lng": 144.3617,
                    "type": "Regional City",
                },
                {
                    "name": "Ballarat",
                    "pop": 109533,
                    "lat": -37.5622,
                    "lng": 143.8503,
                    "type": "Regional City",
                },
                {
                    "name": "Bendigo",
                    "pop": 95587,
                    "lat": -36.7570,
                    "lng": 144.2794,
                    "type": "Regional City",
                },
                {
                    "name": "Latrobe",
                    "pop": 75211,
                    "lat": -38.2167,
                    "lng": 146.4167,
                    "type": "Regional City",
                },
                {
                    "name": "Shepparton",
                    "pop": 51631,
                    "lat": -36.3817,
                    "lng": 145.3967,
                    "type": "Regional City",
                },
                {
                    "name": "Wodonga",
                    "pop": 40651,
                    "lat": -36.1217,
                    "lng": 146.8892,
                    "type": "Regional City",
                },
                {
                    "name": "Warrnambool",
                    "pop": 35743,
                    "lat": -38.3839,
                    "lng": 142.4819,
                    "type": "Regional City",
                },
                {
                    "name": "Mildura",
                    "pop": 34565,
                    "lat": -34.2089,
                    "lng": 142.1406,
                    "type": "Regional City",
                },
                {
                    "name": "Horsham",
                    "pop": 16514,
                    "lat": -36.7083,
                    "lng": 142.1975,
                    "type": "Regional City",
                },
                {
                    "name": "Sale",
                    "pop": 13673,
                    "lat": -38.1042,
                    "lng": 147.0681,
                    "type": "Regional City",
                },
                {
                    "name": "Wangaratta",
                    "pop": 19847,
                    "lat": -36.3608,
                    "lng": 146.3156,
                    "type": "Regional City",
                },
                {
                    "name": "Ararat",
                    "pop": 8297,
                    "lat": -37.2833,
                    "lng": 142.9333,
                    "type": "Regional City",
                },
                # Regional Towns and Centers
                {
                    "name": "Colac",
                    "pop": 12547,
                    "lat": -38.3406,
                    "lng": 143.5839,
                    "type": "Town",
                },
                {
                    "name": "Hamilton",
                    "pop": 10281,
                    "lat": -37.7430,
                    "lng": 142.0156,
                    "type": "Town",
                },
                {
                    "name": "Portland",
                    "pop": 9712,
                    "lat": -38.3425,
                    "lng": 141.6036,
                    "type": "Town",
                },
                {
                    "name": "Castlemaine",
                    "pop": 7506,
                    "lat": -37.0667,
                    "lng": 144.2167,
                    "type": "Town",
                },
                {
                    "name": "Kyneton",
                    "pop": 6951,
                    "lat": -37.2500,
                    "lng": 144.4500,
                    "type": "Town",
                },
                {
                    "name": "Echuca",
                    "pop": 14934,
                    "lat": -36.1394,
                    "lng": 144.7489,
                    "type": "Town",
                },
                {
                    "name": "Swan Hill",
                    "pop": 11103,
                    "lat": -35.3375,
                    "lng": 143.5544,
                    "type": "Town",
                },
                {
                    "name": "Stawell",
                    "pop": 6032,
                    "lat": -37.0583,
                    "lng": 142.7789,
                    "type": "Town",
                },
                {
                    "name": "Benalla",
                    "pop": 9328,
                    "lat": -36.5514,
                    "lng": 145.9831,
                    "type": "Town",
                },
                {
                    "name": "Seymour",
                    "pop": 6327,
                    "lat": -37.0264,
                    "lng": 145.1411,
                    "type": "Town",
                },
                {
                    "name": "Kyabram",
                    "pop": 7331,
                    "lat": -36.3167,
                    "lng": 145.0500,
                    "type": "Town",
                },
                {
                    "name": "Kerang",
                    "pop": 3893,
                    "lat": -35.7367,
                    "lng": 143.9194,
                    "type": "Town",
                },
                {
                    "name": "Cohuna",
                    "pop": 2471,
                    "lat": -35.7889,
                    "lng": 144.2111,
                    "type": "Town",
                },
                {
                    "name": "Robinvale",
                    "pop": 2905,
                    "lat": -34.5833,
                    "lng": 142.7833,
                    "type": "Town",
                },
                {
                    "name": "Ouyen",
                    "pop": 1061,
                    "lat": -35.0667,
                    "lng": 142.3167,
                    "type": "Town",
                },
                {
                    "name": "Sea Lake",
                    "pop": 600,
                    "lat": -35.5000,
                    "lng": 142.8667,
                    "type": "Town",
                },
                {
                    "name": "Warracknabeal",
                    "pop": 2340,
                    "lat": -36.2539,
                    "lng": 142.3939,
                    "type": "Town",
                },
                {
                    "name": "Dimboola",
                    "pop": 1435,
                    "lat": -36.4583,
                    "lng": 141.6139,
                    "type": "Town",
                },
                {
                    "name": "Nhill",
                    "pop": 1749,
                    "lat": -36.3319,
                    "lng": 141.6486,
                    "type": "Town",
                },
                {
                    "name": "Edenhope",
                    "pop": 819,
                    "lat": -37.0381,
                    "lng": 141.2978,
                    "type": "Town",
                },
                {
                    "name": "Heywood",
                    "pop": 1392,
                    "lat": -38.1333,
                    "lng": 141.6333,
                    "type": "Town",
                },
                {
                    "name": "Camperdown",
                    "pop": 3369,
                    "lat": -38.2333,
                    "lng": 143.1500,
                    "type": "Town",
                },
                {
                    "name": "Terang",
                    "pop": 2348,
                    "lat": -38.2400,
                    "lng": 142.9017,
                    "type": "Town",
                },
                {
                    "name": "Mortlake",
                    "pop": 1082,
                    "lat": -38.0739,
                    "lng": 142.8111,
                    "type": "Town",
                },
                {
                    "name": "Koroit",
                    "pop": 1941,
                    "lat": -38.2917,
                    "lng": 142.3650,
                    "type": "Town",
                },
                {
                    "name": "Port Fairy",
                    "pop": 3340,
                    "lat": -38.3878,
                    "lng": 142.2347,
                    "type": "Town",
                },
                {
                    "name": "Coleraine",
                    "pop": 1018,
                    "lat": -37.5833,
                    "lng": 141.7000,
                    "type": "Town",
                },
                {
                    "name": "Dunkeld",
                    "pop": 374,
                    "lat": -37.3500,
                    "lng": 142.3500,
                    "type": "Town",
                },
                {
                    "name": "Halls Gap",
                    "pop": 430,
                    "lat": -37.1372,
                    "lng": 142.5181,
                    "type": "Tourist Town",
                },
                {
                    "name": "Lorne",
                    "pop": 1114,
                    "lat": -38.5428,
                    "lng": 143.9789,
                    "type": "Tourist Town",
                },
                {
                    "name": "Apollo Bay",
                    "pop": 1494,
                    "lat": -38.7556,
                    "lng": 143.6700,
                    "type": "Tourist Town",
                },
                {
                    "name": "Torquay",
                    "pop": 18534,
                    "lat": -38.3306,
                    "lng": 144.3267,
                    "type": "Tourist Town",
                },
                {
                    "name": "Anglesea",
                    "pop": 3001,
                    "lat": -38.4075,
                    "lng": 144.1856,
                    "type": "Tourist Town",
                },
                {
                    "name": "Daylesford",
                    "pop": 2548,
                    "lat": -37.3481,
                    "lng": 144.1411,
                    "type": "Tourist Town",
                },
                {
                    "name": "Hepburn Springs",
                    "pop": 601,
                    "lat": -37.3000,
                    "lng": 144.1333,
                    "type": "Tourist Town",
                },
                {
                    "name": "Bright",
                    "pop": 2282,
                    "lat": -36.7275,
                    "lng": 146.9597,
                    "type": "Tourist Town",
                },
                {
                    "name": "Mount Beauty",
                    "pop": 1822,
                    "lat": -36.7417,
                    "lng": 147.1661,
                    "type": "Tourist Town",
                },
                {
                    "name": "Falls Creek",
                    "pop": 243,
                    "lat": -36.8667,
                    "lng": 147.2833,
                    "type": "Tourist Town",
                },
                {
                    "name": "Mount Hotham",
                    "pop": 158,
                    "lat": -36.9833,
                    "lng": 147.1333,
                    "type": "Tourist Town",
                },
                {
                    "name": "Lakes Entrance",
                    "pop": 6810,
                    "lat": -37.8811,
                    "lng": 147.9819,
                    "type": "Tourist Town",
                },
                {
                    "name": "Bairnsdale",
                    "pop": 15411,
                    "lat": -37.8275,
                    "lng": 147.6117,
                    "type": "Regional Town",
                },
                {
                    "name": "Orbost",
                    "pop": 2456,
                    "lat": -37.7031,
                    "lng": 148.4608,
                    "type": "Town",
                },
                {
                    "name": "Mallacoota",
                    "pop": 1021,
                    "lat": -37.5647,
                    "lng": 149.7539,
                    "type": "Tourist Town",
                },
            ],
            # Other states maintain basic coverage
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
        }

    def normalize_city_data(
        self, city_data: Dict[str, Any], state: State
    ) -> Dict[str, Any]:
        """Normalize city data for our model"""

        is_state_capital = city_data.get("capital", False)
        is_national_capital = city_data.get("national_capital", False)
        population = city_data.get("pop", 0)
        is_major_city = population >= 50000

        # Determine city type based on population and classification
        if "Tourist" in city_data.get("type", ""):
            city_type = "Tourist Destination"
        elif "Mining" in city_data.get("type", ""):
            city_type = "Mining Center"
        elif population >= 100000:
            city_type = "Major City"
        elif population >= 10000:
            city_type = "Regional City"
        else:
            city_type = "Town"

        normalized = {
            "state": state,
            "name": city_data["name"],
            "population": population if population > 0 else None,
            "latitude": (
                Decimal(str(city_data["lat"])) if city_data.get("lat") else None
            ),
            "longitude": (
                Decimal(str(city_data["lng"])) if city_data.get("lng") else None
            ),
            "city_type": city_type,
            "is_state_capital": is_state_capital,
            "is_national_capital": is_national_capital,
            "is_major_city": is_major_city,
            "data_source": "manual_comprehensive",
            "data_quality": "high",
        }

        return normalized

    @transaction.atomic
    def populate_australian_cities(self):
        """Populate comprehensive Australian city data"""

        try:
            australia = Country.objects.get(iso_code_2="AU")
        except Country.DoesNotExist:
            raise CommandError("Australia not found in database")

        cities_data = self.get_comprehensive_au_cities()

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors_count = 0

        if self.verbosity >= 1:
            self.stdout.write("Processing comprehensive Australian city data...")

        for state_code, city_list in cities_data.items():
            try:
                state = State.objects.get(country=australia, code=state_code)
            except State.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"State not found: {state_code} in Australia")
                )
                errors_count += 1
                continue

            if self.verbosity >= 2:
                focus_states = ["SA", "VIC"]
                focus_indicator = (
                    " (COMPREHENSIVE FOCUS)" if state_code in focus_states else ""
                )
                self.stdout.write(
                    f"Processing {state.name}{focus_indicator}: {len(city_list)} cities"
                )

            for city_data in city_list:
                try:
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
                                    f"Created: {city.name}, {city.state.name} ({city.city_type})"
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
                                    f"Updated: {city.name}, {city.state.name} ({city.city_type})"
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
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("COMPREHENSIVE AUSTRALIAN CITIES SUMMARY"))
        self.stdout.write("=" * 60)

        if not self.dry_run:
            self.stdout.write(f"Created: {created_count} cities")
            if self.update_existing:
                self.stdout.write(f"Updated: {updated_count} cities")
            self.stdout.write(f"Skipped: {skipped_count} cities")
            if errors_count > 0:
                self.stdout.write(self.style.ERROR(f"Errors: {errors_count} cities"))

            # Show breakdown by state with special emphasis on SA/VIC
            self.stdout.write("\nState-by-State Coverage:")
            focus_states = {"SA": "South Australia", "VIC": "Victoria"}

            for state_code, city_list in cities_data.items():
                try:
                    state = State.objects.get(country=australia, code=state_code)
                    state_city_count = City.objects.filter(state=state).count()

                    if state_code in focus_states:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  🎯 {focus_states[state_code]}: {state_city_count} cities (COMPREHENSIVE)"
                            )
                        )
                    else:
                        self.stdout.write(f"  {state.name}: {state_city_count} cities")

                except State.DoesNotExist:
                    pass

            total_au_cities = City.objects.filter(state__country=australia).count()
            self.stdout.write(f"\nTotal Australian cities: {total_au_cities}")

        else:
            total_would_process = sum(
                len(city_list) for city_list in cities_data.values()
            )
            self.stdout.write(f"Would process: {total_would_process} Australian cities")
            sa_count = len(cities_data.get("SA", []))
            vic_count = len(cities_data.get("VIC", []))
            self.stdout.write(
                self.style.SUCCESS(
                    f"  🎯 South Australia: {sa_count} cities (COMPREHENSIVE)"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(f"  🎯 Victoria: {vic_count} cities (COMPREHENSIVE)")
            )

        self.stdout.write("=" * 60)

        if errors_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Completed with {errors_count} errors. Check the output above for details."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Comprehensive Australian city population completed!"
                )
            )
