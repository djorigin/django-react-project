"""
Aviation Admin Configuration

GeoDjango-powered admin interface for Australian airspace
and aerodrome management with spatial data visualization.
"""

from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Aerodrome, AirspaceClass, RPASOperationalZone

# =============================================================================
# AIRSPACE ADMINISTRATION
# =============================================================================


@admin.register(AirspaceClass)
class AirspaceClassAdmin(GISModelAdmin):
    """GeoDjango admin for airspace classification with map interface."""

    list_display = [
        "name",
        "class_type_display",
        "altitude_range_display",
        "rpas_access_display",
        "authorization_display",
        "status_display",
    ]

    list_filter = [
        "class_type",
        "rpas_access_level",
        "authorization_required",
        "is_active",
        "effective_date",
    ]

    search_fields = ["name", "icao_designator", "controlling_authority"]

    readonly_fields = [
        "is_current",
        "altitude_range_ft",
        "requires_rpas_authorization",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Airspace Identification",
            {"fields": ("name", "class_type", "icao_designator")},
        ),
        (
            "Altitude Definition",
            {
                "fields": (
                    "floor_altitude_ft",
                    "ceiling_altitude_ft",
                    "altitude_range_ft",
                )
            },
        ),
        ("Geographic Boundary", {"fields": ("boundary",), "classes": ("collapse",)}),
        (
            "RPAS Restrictions",
            {
                "fields": (
                    "rpas_access_level",
                    "max_rpas_altitude_agl",
                    "authorization_required",
                    "requires_rpas_authorization",
                )
            },
        ),
        (
            "Operational Details",
            {"fields": ("controlling_authority", "primary_frequency", "notes")},
        ),
        (
            "Validity Period",
            {"fields": ("effective_date", "expiry_date", "is_active", "is_current")},
        ),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    # GeoDjango map settings
    default_zoom = 6
    default_lat = -25.0  # Center of Australia
    default_lon = 135.0
    map_width = 800
    map_height = 500

    def class_type_display(self, obj):
        """Display airspace class with color coding."""
        colors = {
            "A": "#000080",  # Navy
            "C": "#FF0000",  # Red
            "D": "#0066CC",  # Blue
            "E": "#FF6600",  # Orange
            "G": "#008000",  # Green
            "R": "#800080",  # Purple
            "P": "#DC143C",  # Crimson
        }

        color = colors.get(obj.class_type, "#666666")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_class_type_display(),
        )

    class_type_display.short_description = "Class"

    def altitude_range_display(self, obj):
        """Display altitude range with formatting."""
        return obj.altitude_range_ft

    altitude_range_display.short_description = "Altitude Range"

    def rpas_access_display(self, obj):
        """Display RPAS access level with indicators."""
        colors = {
            "prohibited": "red",
            "restricted": "orange",
            "controlled": "blue",
            "unrestricted": "green",
        }

        color = colors.get(obj.rpas_access_level, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_rpas_access_level_display(),
        )

    rpas_access_display.short_description = "RPAS Access"

    def authorization_display(self, obj):
        """Display authorization requirement."""
        if obj.authorization_required:
            return format_html(
                '<span style="color: red; font-weight: bold;">✓ Required</span>'
            )
        return format_html('<span style="color: green;">Not Required</span>')

    authorization_display.short_description = "Authorization"

    def status_display(self, obj):
        """Display current status."""
        if obj.is_current:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html('<span style="color: red;">Inactive</span>')

    status_display.short_description = "Status"


@admin.register(Aerodrome)
class AerodromeAdmin(GISModelAdmin):
    """GeoDjango admin for aerodrome management with map interface."""

    list_display = [
        "name_display",
        "codes_display",
        "aerodrome_type",
        "city",
        "elevation_display",
        "no_fly_zone_display",
        "status_display",
    ]

    list_filter = ["aerodrome_type", "is_active", "city__state", "city__state__country"]

    search_fields = ["name", "icao_code", "iata_code", "city__name"]

    readonly_fields = [
        "latitude",
        "longitude",
        "no_fly_zone_boundary",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Aerodrome Identification",
            {"fields": ("name", "icao_code", "iata_code", "aerodrome_type")},
        ),
        (
            "Geographic Location",
            {"fields": ("location", "latitude", "longitude", "elevation_ft", "city")},
        ),
        (
            "RPAS Restrictions",
            {"fields": ("rpas_no_fly_radius_m", "no_fly_zone_boundary")},
        ),
        (
            "Operational Details",
            {"fields": ("tower_frequency", "is_active", "remarks")},
        ),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    # GeoDjango map settings
    default_zoom = 10
    map_width = 800
    map_height = 500

    def name_display(self, obj):
        """Display aerodrome name with type indicator."""
        icons = {
            "controlled": "🏢",
            "uncontrolled": "🛩️",
            "private": "🏠",
            "heliport": "🚁",
            "emergency": "🚨",
        }

        icon = icons.get(obj.aerodrome_type, "✈️")
        return f"{icon} {obj.name}"

    name_display.short_description = "Name"

    def codes_display(self, obj):
        """Display ICAO and IATA codes."""
        codes = []
        if obj.icao_code:
            codes.append(f"ICAO: {obj.icao_code}")
        if obj.iata_code:
            codes.append(f"IATA: {obj.iata_code}")
        return " | ".join(codes) if codes else "No codes"

    codes_display.short_description = "Codes"

    def elevation_display(self, obj):
        """Display elevation with formatting."""
        return f"{obj.elevation_ft:,} ft AMSL"

    elevation_display.short_description = "Elevation"

    def no_fly_zone_display(self, obj):
        """Display no-fly zone radius."""
        radius_km = obj.rpas_no_fly_radius_m / 1000
        return f"{radius_km:.1f} km radius"

    no_fly_zone_display.short_description = "No-Fly Zone"

    def status_display(self, obj):
        """Display operational status."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Operational</span>'
            )
        return format_html('<span style="color: red;">Closed</span>')

    status_display.short_description = "Status"


@admin.register(RPASOperationalZone)
class RPASOperationalZoneAdmin(GISModelAdmin):
    """GeoDjango admin for RPAS operational zone management."""

    list_display = [
        "name",
        "operator",
        "zone_type",
        "max_altitude_display",
        "approval_status_display",
        "area_display",
        "status_display",
    ]

    list_filter = ["zone_type", "is_active", "operator"]

    search_fields = ["name", "operator__trading_name", "casa_approval_reference"]

    readonly_fields = [
        "zone_area_km2",
        "is_approval_current",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("Zone Identification", {"fields": ("name", "zone_type", "operator")}),
        ("Geographic Definition", {"fields": ("boundary", "zone_area_km2")}),
        ("Operational Restrictions", {"fields": ("max_altitude_agl_ft",)}),
        (
            "Airspace Integration",
            {
                "fields": ("intersecting_airspace", "nearby_aerodromes"),
                "classes": ("collapse",),
            },
        ),
        (
            "CASA Approval",
            {
                "fields": (
                    "casa_approval_reference",
                    "approval_expiry_date",
                    "is_approval_current",
                )
            },
        ),
        (
            "Zone Details",
            {"fields": ("description", "hazards_identified", "is_active")},
        ),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    filter_horizontal = ["intersecting_airspace", "nearby_aerodromes"]

    # GeoDjango map settings
    default_zoom = 12
    map_width = 800
    map_height = 500

    def max_altitude_display(self, obj):
        """Display maximum altitude with formatting."""
        return f"{obj.max_altitude_agl_ft} ft AGL"

    max_altitude_display.short_description = "Max Altitude"

    def approval_status_display(self, obj):
        """Display CASA approval status."""
        if not obj.casa_approval_reference:
            return format_html('<span style="color: gray;">No approval</span>')

        if obj.is_approval_current:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Current</span>'
            )

        return format_html(
            '<span style="color: red; font-weight: bold;">⚠️ Expired</span>'
        )

    approval_status_display.short_description = "CASA Approval"

    def area_display(self, obj):
        """Display zone area."""
        return f"{obj.zone_area_km2} km²"

    area_display.short_description = "Area"

    def status_display(self, obj):
        """Display zone status."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html('<span style="color: red;">Inactive</span>')

    status_display.short_description = "Status"
