"""
Core models for Django React Project

This module contains the foundational models that other apps depend on.
All relationships should point TO core models, not FROM core models.
This ensures loose coupling and maintainability.

Design Principles:
- Data normalization: Each piece of data stored only once
- Core models are referenced by other apps, never reference other apps
- Email-based authentication
- Profile hierarchy for different user types
"""

import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser model"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password"""
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with email and password"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique identifier

    This is the base user model that all profile types extend.
    Contains only essential authentication and basic information.
    """

    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Authentication fields
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email address used for login",
    )

    # Basic user information
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # User status fields
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active",
    )
    is_staff = models.BooleanField(
        default=False, help_text="Designates whether the user can log into admin site"
    )

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # Email verification
    email_verified = models.BooleanField(
        default=False, help_text="Whether the user's email has been verified"
    )
    email_verification_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Token used for email verification",
    )

    # User manager
    objects = CustomUserManager()

    # Authentication settings
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "core_user"

    def __str__(self):
        return f"{self.email}"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between"""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user"""
        return self.first_name

    def clean(self):
        """Custom validation for the model"""
        super().clean()
        # Normalize email
        self.email = self.email.lower() if self.email else ""


# Profile type choices - normalized reference data
class ProfileType(models.Model):
    """
    Normalized profile types

    This ensures profile types are stored once and referenced by profiles.
    Makes it easy to add/modify profile types without touching multiple places.
    """

    PROFILE_TYPES = [
        ("general", "General User"),
        ("staff", "Staff Member"),
        ("pilot", "Pilot"),
        ("client", "Client"),
        ("customer", "Customer"),
    ]

    code = models.CharField(
        max_length=20,
        choices=PROFILE_TYPES,
        unique=True,
        help_text="Unique code for profile type",
    )
    name = models.CharField(max_length=100, help_text="Display name for profile type")
    description = models.TextField(
        blank=True, help_text="Description of this profile type"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this profile type is currently available"
    )

    # Permissions and features
    requires_image = models.BooleanField(
        default=False, help_text="Whether this profile type requires an image"
    )
    has_admin_access = models.BooleanField(
        default=False,
        help_text="Whether users with this profile can access admin features",
    )

    class Meta:
        verbose_name = "Profile Type"
        verbose_name_plural = "Profile Types"
        db_table = "core_profile_type"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =============================================================================
# GEOGRAPHICAL MODELS - For chained selection and mapping integration
# =============================================================================


class Country(models.Model):
    """
    Country model for normalized geographical data

    Supports chained selection and mapping features.
    Integrates with PostGIS for spatial queries.
    """

    # ISO codes for standardization
    iso_code_2 = models.CharField(
        max_length=2,
        unique=True,
        help_text="ISO 3166-1 alpha-2 country code (e.g., 'AU', 'US')",
    )
    iso_code_3 = models.CharField(
        max_length=3,
        unique=True,
        help_text="ISO 3166-1 alpha-3 country code (e.g., 'AUS', 'USA')",
    )

    # Display names
    name = models.CharField(max_length=100, unique=True, help_text="Full country name")
    official_name = models.CharField(
        max_length=200, blank=True, help_text="Official country name"
    )

    # Geographic data
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Country center latitude for mapping",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Country center longitude for mapping",
    )

    # Status and metadata
    is_active = models.BooleanField(
        default=True, help_text="Whether this country is available for selection"
    )
    phone_code = models.CharField(
        max_length=10, blank=True, help_text="International phone code (e.g., '+61')"
    )

    # Additional useful fields
    region = models.CharField(
        max_length=50,
        blank=True,
        help_text="Geographic region (e.g., 'Europe', 'Asia')",
    )
    subregion = models.CharField(
        max_length=50,
        blank=True,
        help_text="Geographic subregion (e.g., 'Western Europe')",
    )
    population = models.BigIntegerField(
        null=True, blank=True, help_text="Country population (for reference)"
    )
    area = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Country area in square kilometers",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        db_table = "core_country"
        ordering = ["name"]

    def __str__(self):
        return self.name


class State(models.Model):
    """
    State/Province model for chained geographical selection
    """

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="states",
        help_text="Parent country",
    )

    # State identifiers
    code = models.CharField(
        max_length=10, help_text="State/province code (e.g., 'NSW', 'CA', 'TX')"
    )
    name = models.CharField(max_length=100, help_text="State/province name")

    # Administrative division type (flexible for different countries)
    division_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of division (e.g., 'State', 'Province', 'Territory', 'Region')",
    )

    # Additional identifiers
    iso_code = models.CharField(
        max_length=10,
        blank=True,
        help_text="ISO 3166-2 subdivision code (if available)",
    )

    # Geographic data
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="State center latitude",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="State center longitude",
    )

    # Metadata
    population = models.BigIntegerField(
        null=True, blank=True, help_text="State/province population"
    )
    area = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="State/province area in square kilometers",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this state is available for selection"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "State/Province"
        verbose_name_plural = "States/Provinces"
        db_table = "core_state"
        unique_together = ["country", "code"]
        ordering = ["country__name", "name"]

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class City(models.Model):
    """
    City/Town model for chained geographical selection
    """

    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="cities",
        help_text="Parent state/province",
    )

    name = models.CharField(max_length=100, help_text="City/town name")

    # Geographic data with PostGIS support
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="City center latitude",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="City center longitude",
    )

    # Optional: PostGIS point field for advanced spatial queries
    # Uncomment when ready for full PostGIS integration
    # from django.contrib.gis.db import models as gis_models
    # location = gis_models.PointField(null=True, blank=True, srid=4326)

    # Population and classification
    population = models.IntegerField(
        null=True, blank=True, help_text="City population (for sorting/filtering)"
    )
    is_major_city = models.BooleanField(
        default=False, help_text="Whether this is considered a major city"
    )

    # City classification and importance
    city_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of city (e.g., 'Capital', 'Major City', 'Town', 'Borough')",
    )
    is_state_capital = models.BooleanField(
        default=False, help_text="Whether this is a state/province capital"
    )
    is_national_capital = models.BooleanField(
        default=False, help_text="Whether this is a national capital"
    )

    # Additional identifiers and data
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="City area in square kilometers",
    )
    elevation = models.IntegerField(
        null=True, blank=True, help_text="City elevation in meters above sea level"
    )
    timezone = models.CharField(
        max_length=50, blank=True, help_text="City timezone (e.g., 'America/New_York')"
    )

    # Data source and quality indicators
    data_source = models.CharField(
        max_length=50,
        blank=True,
        default="manual",
        help_text="Source of city data (e.g., 'geonames', 'manual', 'census')",
    )
    data_quality = models.CharField(
        max_length=20,
        blank=True,
        default="good",
        help_text="Quality of city data (high, good, fair, low)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this city is available for selection"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "City/Town"
        verbose_name_plural = "Cities/Towns"
        db_table = "core_city"
        unique_together = ["state", "name"]
        ordering = ["state__name", "name"]

    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.state.country.name}"

    @property
    def country(self):
        """Convenience property to get country"""
        return self.state.country


class PostalCode(models.Model):
    """
    Postal/ZIP code model linked to cities

    Supports multiple postal codes per city and precise location mapping.
    """

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="postal_codes",
        help_text="Parent city",
    )

    code = models.CharField(max_length=20, help_text="Postal/ZIP code")

    # More precise location data
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Postal code area center latitude",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Postal code area center longitude",
    )

    # Area classification
    area_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of area (urban, suburban, rural, etc.)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this postal code is available for selection"
    )

    class Meta:
        verbose_name = "Postal Code"
        verbose_name_plural = "Postal Codes"
        db_table = "core_postal_code"
        unique_together = ["city", "code"]
        ordering = ["city__name", "code"]

    def __str__(self):
        return f"{self.code} - {self.city.name}"

    @property
    def state(self):
        """Convenience property to get state"""
        return self.city.state

    @property
    def country(self):
        """Convenience property to get country"""
        return self.city.state.country


def profile_image_upload_path(instance, filename):
    """Generate upload path for profile images"""
    # Organize by profile type and user ID
    profile_type = instance.profile_type.code if instance.profile_type else "unknown"
    return f"profiles/{profile_type}/{instance.user.id}/{filename}"


class BaseProfile(models.Model):
    """
    Base profile model that all specific profiles inherit from

    Contains common fields for all profile types. Specific profile types
    can extend this with additional fields as needed.
    """

    # Primary relationships
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
        help_text="Associated user account",
    )
    profile_type = models.ForeignKey(
        ProfileType, on_delete=models.PROTECT, help_text="Type of profile"
    )

    # Profile image (conditional based on profile type)
    image = models.ImageField(
        upload_to=profile_image_upload_path,
        blank=True,
        null=True,
        help_text="Profile image (required for staff and pilot profiles)",
    )

    # Contact information
    phone = models.CharField(
        max_length=20, blank=True, help_text="Primary phone number"
    )

    # Compliance and Legal Information
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Date of birth (required for staff and pilot profiles)",
    )
    tax_file_number = models.CharField(
        max_length=11,  # Australian TFN format: 123 456 789
        blank=True,
        help_text="Tax File Number (required for staff and pilot profiles)",
    )

    # Aviation-specific fields (for pilot profiles)
    arn_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Aviation Reference Number (required for pilot profiles only)",
    )

    # Address information (using chained geographical models)
    address_line_1 = models.CharField(
        max_length=255, blank=True, help_text="Street address line 1"
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address line 2 (apartment, suite, etc.)",
    )

    # Geographical foreign keys for chained selection
    postal_code = models.ForeignKey(
        PostalCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
        help_text="Postal/ZIP code (automatically provides city, state, country)",
    )

    # Optional: Direct geographical references for flexibility
    # These can be used when postal_code is not available
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles_direct",
        help_text="City (fallback if postal code not available)",
    )

    # Manual postal code for cases where our database doesn't have the code
    postal_code_manual = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Manual postal/ZIP code entry (when not in database)",
    )

    # Precise location for mapping (Leaflet integration)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Precise latitude for mapping (Leaflet)",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Precise longitude for mapping (Leaflet)",
    )

    # Profile metadata
    bio = models.TextField(blank=True, help_text="Brief biography or description")
    website = models.URLField(blank=True, help_text="Personal or company website")

    # Status and tracking
    is_verified = models.BooleanField(
        default=False, help_text="Whether this profile has been verified by staff"
    )
    is_public = models.BooleanField(
        default=True, help_text="Whether this profile is publicly visible"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        db_table = "core_profile"
        unique_together = ["user", "profile_type"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.profile_type.name})"

    # Geographical helper methods
    @property
    def get_city(self):
        """Get city from postal_code or direct city reference"""
        if self.postal_code:
            return self.postal_code.city
        return self.city

    @property
    def get_state(self):
        """Get state from postal_code or city"""
        city = self.get_city
        return city.state if city else None

    @property
    def get_country(self):
        """Get country from postal_code or city"""
        state = self.get_state
        return state.country if state else None

    @property
    def full_address(self):
        """Get complete formatted address"""
        address_parts = []

        if self.address_line_1:
            address_parts.append(self.address_line_1)
        if self.address_line_2:
            address_parts.append(self.address_line_2)

        city = self.get_city
        if city:
            address_parts.append(str(city))

        # Add postal code (database or manual)
        if self.postal_code:
            address_parts.append(self.postal_code.code)
        elif self.postal_code_manual:
            address_parts.append(self.postal_code_manual)

        return ", ".join(address_parts) if address_parts else ""

    @property
    def coordinates(self):
        """Get coordinates as tuple (lat, lng) for Leaflet"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))

        # Fallback to postal code coordinates
        if (
            self.postal_code
            and self.postal_code.latitude
            and self.postal_code.longitude
        ):
            return (float(self.postal_code.latitude), float(self.postal_code.longitude))

        # Fallback to city coordinates
        city = self.get_city
        if city and city.latitude and city.longitude:
            return (float(city.latitude), float(city.longitude))

        return None

    def clean(self):
        """Custom validation"""
        super().clean()

        # Validate image requirement
        if self.profile_type and self.profile_type.requires_image and not self.image:
            raise ValidationError(
                {"image": f"Image is required for {self.profile_type.name} profiles"}
            )

        # Validate compliance fields for staff and pilot profiles
        if self.profile_type and self.profile_type.name in ["Staff", "Pilot"]:
            errors = {}

            # Date of birth required for staff and pilots
            if not self.date_of_birth:
                errors["date_of_birth"] = (
                    f"Date of birth is required for {self.profile_type.name} profiles"
                )

            # Tax File Number required for staff and pilots
            if not self.tax_file_number:
                errors["tax_file_number"] = (
                    f"Tax File Number is required for {self.profile_type.name} profiles"
                )

            # ARN number required for pilots only
            if self.profile_type.name == "Pilot" and not self.arn_number:
                errors["arn_number"] = (
                    "Aviation Reference Number (ARN) is required for pilot profiles"
                )

            if errors:
                raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.clean()
        super().save(*args, **kwargs)


# =============================================================================
# THREE-COLOR COMPLIANCE SYSTEM - REVOLUTIONARY CASA INTELLIGENCE
# =============================================================================


class ComplianceStatus(models.TextChoices):
    """Three-color compliance status system for CASA regulatory compliance"""

    GREEN = "green", "Compliant"
    YELLOW = "yellow", "Warning"
    RED = "red", "Non-Compliant"


class ComplianceRule(models.Model):
    """
    Central repository of all CASA compliance rules and regulations.

    This model stores individual compliance requirements that can be checked
    against any model in the system using the ComplianceMixin.
    """

    rule_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for this compliance rule (e.g., 'MOS_101_4_02')",
    )

    rule_name = models.CharField(
        max_length=200, help_text="Human-readable name of the compliance rule"
    )

    description = models.TextField(
        help_text="Detailed description of what this rule checks"
    )

    casa_reference = models.CharField(
        max_length=100,
        help_text="Official CASA reference (e.g., 'CASA MOS Part 101 Section 4.02')",
    )

    severity = models.CharField(
        max_length=10,
        choices=ComplianceStatus.choices,
        default=ComplianceStatus.RED,
        help_text="Default severity level if this rule fails",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this rule is currently enforced"
    )

    check_frequency_hours = models.PositiveIntegerField(
        default=24, help_text="How often this rule should be checked (in hours)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rule_code"]
        verbose_name = "Compliance Rule"
        verbose_name_plural = "Compliance Rules"

    def __str__(self):
        return f"{self.rule_code}: {self.rule_name}"

    @property
    def severity_display(self):
        """Return color-coded severity display"""
        color_map = {
            ComplianceStatus.GREEN: "🟢",
            ComplianceStatus.YELLOW: "🟡",
            ComplianceStatus.RED: "🔴",
        }
        return f"{color_map.get(self.severity, '⚫')} {self.get_severity_display()}"


class ComplianceCheck(models.Model):
    """
    Individual compliance check results for any model using ComplianceMixin.

    This model stores the results of compliance rule evaluations and provides
    the foundation for the three-color status system.
    """

    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    rule = models.ForeignKey(
        ComplianceRule,
        on_delete=models.CASCADE,
        help_text="The compliance rule being checked",
    )

    status = models.CharField(
        max_length=10,
        choices=ComplianceStatus.choices,
        help_text="Current compliance status for this check",
    )

    last_checked = models.DateTimeField(
        auto_now=True, help_text="When this compliance check was last performed"
    )

    next_check_due = models.DateTimeField(
        null=True, blank=True, help_text="When the next check is due"
    )

    details = models.JSONField(
        default=dict, help_text="Additional details about the compliance check result"
    )

    checked_by = models.ForeignKey(
        "core.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who performed this compliance check",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_checked"]
        verbose_name = "Compliance Check"
        verbose_name_plural = "Compliance Checks"
        unique_together = ["content_type", "object_id", "rule"]

    def __str__(self):
        return f"{self.content_object} - {self.rule.rule_code}: {self.get_status_display()}"

    @property
    def status_display(self):
        """Return color-coded status display"""
        color_map = {
            ComplianceStatus.GREEN: "🟢",
            ComplianceStatus.YELLOW: "🟡",
            ComplianceStatus.RED: "🔴",
        }
        return f"{color_map.get(self.status, '⚫')} {self.get_status_display()}"

    @property
    def is_overdue(self):
        """Check if this compliance check is overdue"""
        if not self.next_check_due:
            return False
        return timezone.now() > self.next_check_due

    def update_next_check_due(self):
        """Update the next check due date based on rule frequency"""
        if self.rule.check_frequency_hours:
            self.next_check_due = timezone.now() + timezone.timedelta(
                hours=self.rule.check_frequency_hours
            )
            self.save()


class ComplianceMixin(models.Model):
    """
    Abstract mixin for any model requiring CASA compliance checking.

    This mixin provides the foundation for the three-color compliance system
    and should be inherited by all models that need compliance monitoring.
    """

    class Meta:
        abstract = True

    @property
    def compliance_status(self):
        """
        Get the overall compliance status (GREEN/YELLOW/RED) for this object.

        Returns:
            str: The worst case compliance status from all active checks
        """
        checks = ComplianceCheck.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            rule__is_active=True,
        )

        # No checks means GREEN (compliant by default)
        if not checks.exists():
            return ComplianceStatus.GREEN

        # Return worst case status
        if checks.filter(status=ComplianceStatus.RED).exists():
            return ComplianceStatus.RED
        elif checks.filter(status=ComplianceStatus.YELLOW).exists():
            return ComplianceStatus.YELLOW
        else:
            return ComplianceStatus.GREEN

    @property
    def compliance_status_display(self):
        """Return color-coded compliance status display"""
        status = self.compliance_status
        color_map = {
            ComplianceStatus.GREEN: "🟢",
            ComplianceStatus.YELLOW: "🟡",
            ComplianceStatus.RED: "🔴",
        }
        display_map = {
            ComplianceStatus.GREEN: "Compliant",
            ComplianceStatus.YELLOW: "Warning",
            ComplianceStatus.RED: "Non-Compliant",
        }
        return f"{color_map.get(status, '⚫')} {display_map.get(status, 'Unknown')}"

    def get_compliance_color_class(self):
        """
        Return Tailwind CSS class for three-color border styling.

        Returns:
            str: CSS class name for form/element borders
        """
        status = self.compliance_status
        return {
            ComplianceStatus.GREEN: "border-green-500 bg-green-50",
            ComplianceStatus.YELLOW: "border-yellow-500 bg-yellow-50",
            ComplianceStatus.RED: "border-red-500 bg-red-50",
        }.get(status, "border-gray-300 bg-gray-50")

    def get_compliance_checks(self):
        """
        Get all compliance checks for this object.

        Returns:
            QuerySet: All ComplianceCheck objects for this instance
        """
        return ComplianceCheck.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id
        )

    def get_failed_compliance_checks(self):
        """
        Get all failed compliance checks (YELLOW or RED status).

        Returns:
            QuerySet: Failed ComplianceCheck objects for this instance
        """
        return self.get_compliance_checks().exclude(status=ComplianceStatus.GREEN)

    def run_compliance_checks(self, user=None):
        """
        Run all applicable compliance checks for this object.

        This method should be overridden by subclasses to implement
        specific compliance checking logic.

        Args:
            user: User performing the compliance check

        Returns:
            dict: Results of compliance checking
        """
        # Default implementation - to be overridden by subclasses
        return {
            "checks_run": 0,
            "status": self.compliance_status,
            "message": "No specific compliance checks implemented",
        }

    def get_compliance_summary(self):
        """
        Get a summary of compliance status for this object.

        Returns:
            dict: Summary of compliance status and checks
        """
        checks = self.get_compliance_checks()
        failed_checks = self.get_failed_compliance_checks()

        return {
            "overall_status": self.compliance_status,
            "total_checks": checks.count(),
            "failed_checks": failed_checks.count(),
            "last_checked": checks.first().last_checked if checks.exists() else None,
            "overdue_checks": (
                checks.filter(next_check_due__lt=timezone.now()).count()
                if checks.exists()
                else 0
            ),
        }
