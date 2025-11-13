"""
Admin configuration for core models
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    BaseProfile,
    City,
    Country,
    CustomUser,
    PostalCode,
    ProfileType,
    State,
)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Custom admin for CustomUser model"""

    # Fields to display in the list view
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "email_verified",
        "date_joined",
    ]

    # Fields to filter by
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
        "date_joined",
    ]

    # Fields to search
    search_fields = ["email", "first_name", "last_name"]

    # Ordering
    ordering = ["-date_joined"]

    # Fields for editing existing users
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Email Verification",
            {
                "fields": ("email_verified", "email_verification_token"),
                "classes": ("collapse",),
            },
        ),
        (
            "Important Dates",
            {"fields": ("last_login", "date_joined"), "classes": ("collapse",)},
        ),
    )

    # Fields for adding new users
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = ["date_joined", "last_login"]


@admin.register(ProfileType)
class ProfileTypeAdmin(admin.ModelAdmin):
    """Admin for ProfileType model"""

    list_display = ["name", "code", "is_active", "requires_image", "has_admin_access"]
    list_filter = ["is_active", "requires_image", "has_admin_access"]
    search_fields = ["name", "code", "description"]
    ordering = ["name"]

    fieldsets = (
        (None, {"fields": ("code", "name", "description", "is_active")}),
        ("Features", {"fields": ("requires_image", "has_admin_access")}),
    )


@admin.register(BaseProfile)
class BaseProfileAdmin(admin.ModelAdmin):
    """Admin for BaseProfile model"""

    list_display = [
        "user_email",
        "user_full_name",
        "profile_type",
        "is_verified",
        "is_public",
        "created_at",
    ]
    list_filter = [
        "profile_type",
        "is_verified",
        "is_public",
        "created_at",
        "postal_code__city__state__country",
    ]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone",
        "tax_file_number",
        "arn_number",
        "postal_code__city__name",
        "city__name",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        ("User & Type", {"fields": ("user", "profile_type")}),
        ("Profile Image", {"fields": ("image",)}),
        ("Contact Information", {"fields": ("phone",)}),
        (
            "Compliance Information",
            {
                "fields": ("date_of_birth", "tax_file_number", "arn_number"),
                "description": "Required fields for staff/pilot compliance and aviation records",
                "classes": ("collapse",),
            },
        ),
        (
            "Address",
            {
                "fields": ("address_line_1", "address_line_2", "postal_code", "city"),
                "classes": ("collapse",),
            },
        ),
        (
            "Precise Location",
            {
                "fields": ("latitude", "longitude"),
                "description": "Precise coordinates for mapping (Leaflet)",
                "classes": ("collapse",),
            },
        ),
        ("Profile Details", {"fields": ("bio", "website")}),
        ("Status", {"fields": ("is_verified", "is_public")}),
    )

    readonly_fields = ["created_at", "updated_at"]

    # Custom methods for list display
    def user_email(self, obj):
        """Display user email with link to user admin"""
        if obj.user:
            url = reverse("admin:core_customuser_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return "-"

    user_email.short_description = "User Email"
    user_email.admin_order_field = "user__email"

    def user_full_name(self, obj):
        """Display user full name"""
        return obj.user.get_full_name() if obj.user else "-"

    user_full_name.short_description = "Full Name"
    user_full_name.admin_order_field = "user__first_name"

    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related("user", "profile_type")


# =============================================================================
# GEOGRAPHICAL MODEL ADMINS - For chained selection
# =============================================================================


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Admin for Country model"""

    list_display = ["name", "iso_code_2", "iso_code_3", "phone_code", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "official_name", "iso_code_2", "iso_code_3"]
    ordering = ["name"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "official_name")}),
        ("ISO Codes", {"fields": ("iso_code_2", "iso_code_3")}),
        ("Contact & Location", {"fields": ("phone_code", "latitude", "longitude")}),
        ("Status", {"fields": ("is_active",)}),
    )


class StateInline(admin.TabularInline):
    """Inline admin for states within country"""

    model = State
    extra = 0
    fields = ["code", "name", "is_active"]


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    """Admin for State model with chained selection"""

    list_display = ["name", "code", "country", "is_active"]
    list_filter = ["country", "is_active"]
    search_fields = ["name", "code", "country__name"]
    ordering = ["country__name", "name"]

    fieldsets = (
        ("Basic Information", {"fields": ("country", "name", "code")}),
        ("Location", {"fields": ("latitude", "longitude")}),
        ("Status", {"fields": ("is_active",)}),
    )

    # Enable chained selection in admin
    autocomplete_fields = ["country"]


class CityInline(admin.TabularInline):
    """Inline admin for cities within state"""

    model = City
    extra = 0
    fields = ["name", "is_major_city", "is_active"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin for City model with chained selection"""

    list_display = [
        "name",
        "state",
        "country_name",
        "population",
        "is_major_city",
        "is_active",
    ]
    list_filter = ["state__country", "state", "is_major_city", "is_active"]
    search_fields = ["name", "state__name", "state__country__name"]
    ordering = ["state__country__name", "state__name", "name"]

    fieldsets = (
        ("Basic Information", {"fields": ("state", "name")}),
        ("Classification", {"fields": ("population", "is_major_city")}),
        ("Location", {"fields": ("latitude", "longitude")}),
        ("Status", {"fields": ("is_active",)}),
    )

    # Enable chained selection
    autocomplete_fields = ["state"]

    def country_name(self, obj):
        """Display country name"""
        return obj.state.country.name if obj.state else "-"

    country_name.short_description = "Country"
    country_name.admin_order_field = "state__country__name"


class PostalCodeInline(admin.TabularInline):
    """Inline admin for postal codes within city"""

    model = PostalCode
    extra = 0
    fields = ["code", "area_type", "is_active"]


@admin.register(PostalCode)
class PostalCodeAdmin(admin.ModelAdmin):
    """Admin for PostalCode model with chained selection"""

    list_display = [
        "code",
        "city",
        "state_name",
        "country_name",
        "area_type",
        "is_active",
    ]
    list_filter = ["city__state__country", "city__state", "area_type", "is_active"]
    search_fields = [
        "code",
        "city__name",
        "city__state__name",
        "city__state__country__name",
    ]
    ordering = ["city__state__country__name", "city__state__name", "city__name", "code"]

    fieldsets = (
        ("Basic Information", {"fields": ("city", "code", "area_type")}),
        (
            "Precise Location",
            {
                "fields": ("latitude", "longitude"),
                "description": "Precise coordinates for this postal code area",
            },
        ),
        ("Status", {"fields": ("is_active",)}),
    )

    # Enable chained selection
    autocomplete_fields = ["city"]

    def state_name(self, obj):
        """Display state name"""
        return obj.city.state.name if obj.city else "-"

    state_name.short_description = "State"
    state_name.admin_order_field = "city__state__name"

    def country_name(self, obj):
        """Display country name"""
        return obj.city.state.country.name if obj.city else "-"

    country_name.short_description = "Country"
    country_name.admin_order_field = "city__state__country__name"


# Add inlines to parent models
CountryAdmin.inlines = [StateInline]
StateAdmin.inlines = [CityInline]
CityAdmin.inlines = [PostalCodeInline]


# Customize admin site headers
admin.site.site_header = "Django React Project Admin"
admin.site.site_title = "Django React Project"
admin.site.index_title = "Administration"
