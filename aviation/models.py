"""
Aviation Models - Australian Airspace and Regulatory Data

GeoDjango-powered models for CASA-compliant airspace management,
aerodrome data, and regulatory zones for RPAS operations.
"""

import uuid
from datetime import date

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, Polygon
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from core.models import ComplianceMixin

# =============================================================================
# AUSTRALIAN AIRSPACE CLASSIFICATION
# =============================================================================


class AirspaceClass(ComplianceMixin, models.Model):
    """
    Australian Airspace Classification System

    Implements CASA airspace classes with GeoDjango boundaries
    for precise RPAS operational planning and compliance.
    """

    AIRSPACE_TYPES = [
        ("A", "Class A - Above 18,000ft (IFR only)"),
        ("C", "Class C - Major Airport Control Zone"),
        ("D", "Class D - Regional Airport Control Zone"),
        ("E", "Class E - Controlled Airspace"),
        ("G", "Class G - Uncontrolled Airspace"),
        ("R", "Restricted Area - Military/Special Use"),
        ("P", "Prohibited Area - No Entry"),
    ]

    RPAS_ACCESS_LEVELS = [
        ("prohibited", "Prohibited - No RPAS access"),
        ("restricted", "Restricted - Authorization required"),
        ("controlled", "Controlled - ATC coordination required"),
        ("unrestricted", "Unrestricted - Standard operations"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Airspace identification
    name = models.CharField(
        max_length=200, help_text="Official airspace name/identifier"
    )

    class_type = models.CharField(
        max_length=1,
        choices=AIRSPACE_TYPES,
        help_text="Australian airspace classification",
    )

    icao_designator = models.CharField(
        max_length=10,
        blank=True,
        help_text="ICAO airport/facility designator if applicable",
    )

    # Altitude boundaries
    floor_altitude_ft = models.IntegerField(help_text="Airspace floor in feet AMSL")

    ceiling_altitude_ft = models.IntegerField(
        null=True,
        blank=True,
        help_text="Airspace ceiling in feet AMSL (null = unlimited)",
    )

    # GeoDjango boundary definition
    boundary = models.PolygonField(
        srid=4326, help_text="Airspace boundary geometry"  # WGS84 coordinate system
    )

    # RPAS operational restrictions
    rpas_access_level = models.CharField(
        max_length=20,
        choices=RPAS_ACCESS_LEVELS,
        default="unrestricted",
        help_text="RPAS access restrictions",
    )

    max_rpas_altitude_agl = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(400)],
        help_text="Maximum RPAS altitude in feet AGL (if restricted)",
    )

    authorization_required = models.BooleanField(
        default=False, help_text="Is CASA authorization required for RPAS operations?"
    )

    # Operational details
    controlling_authority = models.CharField(
        max_length=100, blank=True, help_text="ATC facility or controlling authority"
    )

    primary_frequency = models.CharField(
        max_length=10, blank=True, help_text="Primary radio frequency (MHz)"
    )

    # Validity and status
    effective_date = models.DateField(
        default=date.today, help_text="Date airspace becomes effective"
    )

    expiry_date = models.DateField(
        null=True, blank=True, help_text="Date airspace expires (null = permanent)"
    )

    is_active = models.BooleanField(
        default=True, help_text="Is this airspace currently active?"
    )

    # Metadata
    notes = models.TextField(
        blank=True, help_text="Additional operational notes and restrictions"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Airspace Class"
        verbose_name_plural = "Airspace Classes"
        ordering = ["class_type", "name"]
        indexes = [
            models.Index(fields=["class_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["effective_date"]),
        ]

    def __str__(self):
        return f"{self.get_class_type_display()}: {self.name}"

    @property
    def is_current(self):
        """Check if airspace is currently effective."""
        today = date.today()
        if today < self.effective_date:
            return False
        if self.expiry_date and today > self.expiry_date:
            return False
        return self.is_active

    @property
    def altitude_range_ft(self):
        """Get altitude range as formatted string."""
        if self.ceiling_altitude_ft:
            return f"{self.floor_altitude_ft:,} - {self.ceiling_altitude_ft:,} ft AMSL"
        else:
            return f"{self.floor_altitude_ft:,} ft AMSL and above"

    @property
    def requires_rpas_authorization(self):
        """Check if RPAS operations require authorization."""
        return self.authorization_required or self.rpas_access_level in [
            "prohibited",
            "restricted",
        ]

    def check_rpas_operation_permitted(self, altitude_agl_ft):
        """
        Check if RPAS operation is permitted at given altitude.

        Args:
            altitude_agl_ft (int): Planned altitude in feet AGL

        Returns:
            tuple: (permitted: bool, reason: str)
        """
        if self.rpas_access_level == "prohibited":
            return False, "RPAS operations prohibited in this airspace"

        if not self.is_current:
            return False, "Airspace is not currently effective"

        if self.max_rpas_altitude_agl and altitude_agl_ft > self.max_rpas_altitude_agl:
            return (
                False,
                f"Altitude {altitude_agl_ft}ft AGL exceeds maximum {self.max_rpas_altitude_agl}ft AGL",
            )

        if self.authorization_required:
            return True, "Authorization required - contact controlling authority"

        return True, "Operation permitted"

    def get_compliance_summary(self):
        """
        ComplianceMixin implementation for AirspaceClass.

        Evaluates airspace compliance status based on:
        - Current effectiveness dates
        - RPAS access restrictions
        - Authorization requirements
        """
        total_checks = 2  # Effectiveness + access level
        failed_checks = 0

        # Check if airspace is currently effective
        if not self.is_current:
            failed_checks += 1

        # Check RPAS access level
        if self.rpas_access_level == "prohibited":
            failed_checks += 1
        elif self.rpas_access_level in ["restricted", "controlled"]:
            # Warning state for restricted airspace
            if not self.authorization_required:
                total_checks += 1
                failed_checks += 1

        # Determine overall status
        if failed_checks == 0:
            overall_status = "green"
        elif failed_checks == 1:
            overall_status = "yellow"
        else:
            overall_status = "red"

        return {
            "overall_status": overall_status,
            "total_checks": total_checks,
            "failed_checks": failed_checks,
            "last_checked": timezone.now(),
        }


class Aerodrome(ComplianceMixin, models.Model):
    """
    Australian Aerodromes and Airports

    CASA-registered aerodromes with RPAS operational restrictions
    and no-fly zone calculations.
    """

    AERODROME_TYPES = [
        ("controlled", "Controlled Airport - Tower Operations"),
        ("uncontrolled", "Uncontrolled Aerodrome"),
        ("private", "Private Airstrip"),
        ("heliport", "Heliport"),
        ("emergency", "Emergency Landing Area"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Aerodrome identification
    name = models.CharField(max_length=200, help_text="Official aerodrome name")

    icao_code = models.CharField(
        max_length=4,
        unique=True,
        blank=True,
        help_text="4-letter ICAO airport code (if assigned)",
    )

    iata_code = models.CharField(
        max_length=3, blank=True, help_text="3-letter IATA airport code (if assigned)"
    )

    aerodrome_type = models.CharField(
        max_length=20, choices=AERODROME_TYPES, help_text="Type of aerodrome facility"
    )

    # Geographic location
    location = models.PointField(
        srid=4326, help_text="Aerodrome reference point (ARP)"  # WGS84
    )

    elevation_ft = models.IntegerField(help_text="Aerodrome elevation in feet AMSL")

    # Address information
    city = models.ForeignKey(
        "core.City",
        on_delete=models.PROTECT,
        related_name="aerodromes",
        help_text="Nearest city",
    )

    # RPAS restrictions
    rpas_no_fly_radius_m = models.IntegerField(
        default=5500, help_text="RPAS no-fly radius in meters"  # CASA default 5.5km
    )

    tower_frequency = models.CharField(
        max_length=10, blank=True, help_text="Tower/CTAF frequency (MHz)"
    )

    # Operational status
    is_active = models.BooleanField(
        default=True, help_text="Is aerodrome currently operational?"
    )

    # Additional information
    remarks = models.TextField(blank=True, help_text="Operational remarks and notes")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aerodrome"
        verbose_name_plural = "Aerodromes"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["aerodrome_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["icao_code"]),
        ]

    def __str__(self):
        if self.icao_code:
            return f"{self.icao_code}: {self.name}"
        return self.name

    @property
    def latitude(self):
        """Get latitude in decimal degrees."""
        return self.location.y

    @property
    def longitude(self):
        """Get longitude in decimal degrees."""
        return self.location.x

    @property
    def no_fly_zone_boundary(self):
        """Calculate no-fly zone boundary as circular polygon."""
        # Create circular boundary around aerodrome
        # Using approximate conversion: 1 degree ≈ 111,111 meters
        radius_degrees = self.rpas_no_fly_radius_m / 111111.0

        # Create circular polygon with 36 points (10-degree intervals)
        points = []
        import math

        for i in range(36):
            angle = math.radians(i * 10)
            lat = self.latitude + (radius_degrees * math.cos(angle))
            lng = self.longitude + (radius_degrees * math.sin(angle))
            points.append((lng, lat))
        points.append(points[0])  # Close the polygon

        return Polygon(points)

    def check_rpas_proximity(self, point, altitude_agl_ft):
        """
        Check if RPAS operation conflicts with aerodrome.

        Args:
            point (Point): RPAS operation location
            altitude_agl_ft (int): Planned altitude in feet AGL

        Returns:
            tuple: (conflict: bool, distance_m: float, reason: str)
        """
        # Calculate distance from aerodrome
        distance_m = (
            self.location.distance(point) * 111111.0
        )  # Rough conversion to meters

        if distance_m <= self.rpas_no_fly_radius_m:
            return (
                True,
                distance_m,
                f"Within {self.rpas_no_fly_radius_m / 1000:.1f}km no-fly zone",
            )

        return False, distance_m, "Outside no-fly zone"


class RPASOperationalZone(ComplianceMixin, models.Model):
    """
    RPAS Operational Zone Definitions

    Predefined operational areas with known characteristics
    for efficient flight planning and risk assessment.
    """

    ZONE_TYPES = [
        ("approved", "Pre-approved Operational Area"),
        ("standard", "Standard Operations Zone"),
        ("restricted", "Restricted Operations Zone"),
        ("training", "Training Area"),
        ("emergency", "Emergency Response Zone"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Zone identification
    name = models.CharField(max_length=200, help_text="Operational zone name")

    zone_type = models.CharField(
        max_length=20, choices=ZONE_TYPES, help_text="Type of operational zone"
    )

    operator = models.ForeignKey(
        "rpas.RPASOperator",
        on_delete=models.CASCADE,
        related_name="operational_zones",
        help_text="RPAS operator this zone belongs to",
    )

    # Geographic definition
    boundary = models.PolygonField(
        srid=4326, help_text="Operational zone boundary"  # WGS84
    )

    # Operational restrictions
    max_altitude_agl_ft = models.IntegerField(
        default=400,
        validators=[MinValueValidator(0), MaxValueValidator(400)],
        help_text="Maximum altitude in feet AGL",
    )

    # Associated airspace
    intersecting_airspace = models.ManyToManyField(
        AirspaceClass,
        blank=True,
        related_name="operational_zones",
        help_text="Airspace classes this zone intersects",
    )

    nearby_aerodromes = models.ManyToManyField(
        Aerodrome,
        blank=True,
        related_name="nearby_operational_zones",
        help_text="Aerodromes within proximity",
    )

    # Approval and authorization
    casa_approval_reference = models.CharField(
        max_length=50, blank=True, help_text="CASA approval reference number"
    )

    approval_expiry_date = models.DateField(
        null=True, blank=True, help_text="Date approval expires"
    )

    # Zone characteristics
    description = models.TextField(help_text="Zone description and operational notes")

    hazards_identified = models.TextField(
        blank=True, help_text="Known hazards in this operational zone"
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Is zone currently available for operations?"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RPAS Operational Zone"
        verbose_name_plural = "RPAS Operational Zones"
        ordering = ["operator", "name"]

    def __str__(self):
        return f"{self.operator.trading_name}: {self.name}"

    @property
    def is_approval_current(self):
        """Check if CASA approval is current."""
        if not self.casa_approval_reference:
            return False
        if not self.approval_expiry_date:
            return True  # Permanent approval
        return date.today() <= self.approval_expiry_date

    @property
    def zone_area_km2(self):
        """Calculate zone area in square kilometers."""
        # Convert to projected coordinate system for accurate area calculation
        # This is a simplified calculation - should use proper projection
        area_deg2 = self.boundary.area
        area_km2 = area_deg2 * 111.111 * 111.111  # Rough conversion
        return round(area_km2, 2)

    def check_flight_compliance(self, planned_altitude_agl_ft):
        """
        Check if planned flight complies with zone restrictions.

        Args:
            planned_altitude_agl_ft (int): Planned altitude in feet AGL

        Returns:
            tuple: (compliant: bool, issues: list)
        """
        issues = []

        if not self.is_active:
            issues.append("Operational zone is not active")

        if not self.is_approval_current:
            issues.append("CASA approval has expired")

        if planned_altitude_agl_ft > self.max_altitude_agl_ft:
            issues.append(
                f"Altitude {planned_altitude_agl_ft}ft exceeds zone limit {self.max_altitude_agl_ft}ft"
            )

        return len(issues) == 0, issues
