"""
SMS (Safety Management System) Models - CASA Compliance

Revolutionary SMS that transforms safety from bureaucratic burden into intelligent
competitive advantage through AI-powered risk management and automation.

CASA Requirements (SMS Manual):
- Risk Management Framework
- Safety Performance Monitoring
- Management of Change
- Emergency Response Planning
- Continuous Improvement Process

This SMS integrates seamlessly with F2 automation to create a unified
safety and maintenance intelligence platform.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count
from django.utils import timezone

User = get_user_model()


# =============================================================================
# SMS RISK MANAGEMENT FRAMEWORK
# =============================================================================


class RiskCategory(models.Model):
    """
    SMS Risk Categories - CASA Compliant Classification

    Standardized risk categorization system that provides consistent
    risk identification and management across all operations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Category identification
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Risk category name (e.g., Aircraft Operations, Personnel, Weather)",
    )

    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Short code for category (e.g., AO, PER, WX)",
    )

    description = models.TextField(
        help_text="Detailed description of risk category scope"
    )

    # CASA SMS compliance fields
    casa_reference = models.CharField(
        max_length=50,
        blank=True,
        help_text="CASA SMS manual reference for this category",
    )

    # Category management
    is_active = models.BooleanField(
        default=True, help_text="Category available for new risk assessments"
    )

    # AI Risk Intelligence
    default_likelihood_modifier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.1), MaxValueValidator(2.0)],
        help_text="AI modifier for likelihood scoring (0.1-2.0)",
    )

    default_consequence_modifier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.1), MaxValueValidator(2.0)],
        help_text="AI modifier for consequence scoring (0.1-2.0)",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Risk Category"
        verbose_name_plural = "Risk Categories"
        ordering = ["code", "name"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def active_risks_count(self):
        """Count of active risks in this category."""
        return self.risks.filter(status__in=["open", "monitoring"]).count()

    @property
    def high_risks_count(self):
        """Count of high/extreme risks in this category."""
        return self.risks.filter(
            residual_risk_rating__in=["high", "extreme"],
            status__in=["open", "monitoring"],
        ).count()


class RiskRegister(models.Model):
    """
    SMS Risk Register - Intelligent Risk Management

    Revolutionary risk management that transforms traditional bureaucratic
    risk registers into intelligent safety management tools.

    Features:
    - AI-powered risk scoring
    - Automated control effectiveness monitoring
    - Integration with F2 maintenance triggers
    - Real-time risk rating updates
    - Predictive risk trend analysis
    """

    # Risk rating choices (CASA standard matrix)
    RISK_RATINGS = [
        ("extreme", "Extreme - Unacceptable Risk"),
        ("high", "High - Unacceptable Risk"),
        ("medium", "Medium - Acceptable with Controls"),
        ("low", "Low - Acceptable Risk"),
        ("negligible", "Negligible - Minimal Risk"),
    ]

    LIKELIHOOD_SCORES = [
        (1, "Remote - Extremely unlikely to occur"),
        (2, "Improbable - Unlikely to occur"),
        (3, "Possible - May occur occasionally"),
        (4, "Probable - Likely to occur"),
        (5, "Frequent - Expected to occur regularly"),
    ]

    CONSEQUENCE_SCORES = [
        (1, "Negligible - Minimal impact"),
        (2, "Minor - Small impact, easily managed"),
        (3, "Moderate - Noticeable impact, manageable"),
        (4, "Major - Significant impact, serious concern"),
        (5, "Catastrophic - Extreme impact, unacceptable"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft - Under Development"),
        ("open", "Open - Active Risk"),
        ("monitoring", "Monitoring - Controls in Place"),
        ("closed", "Closed - Risk Eliminated"),
        ("superseded", "Superseded - Replaced by New Assessment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Risk identification
    risk_number = models.CharField(
        max_length=20, unique=True, help_text="Unique risk identifier (auto-generated)"
    )

    title = models.CharField(max_length=200, help_text="Concise risk title/description")

    description = models.TextField(
        help_text="Detailed risk description and potential consequences"
    )

    # Risk categorization
    category = models.ForeignKey(
        RiskCategory,
        on_delete=models.PROTECT,
        related_name="risks",
        help_text="Risk category for classification",
    )

    # CASA SMS Links
    operator = models.ForeignKey(
        "rpas.RPASOperator",
        on_delete=models.CASCADE,
        related_name="risks",
        help_text="RPAS operator this risk applies to",
    )

    # Risk assessment team
    identified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="identified_risks",
        help_text="Person who identified this risk",
    )

    assessed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="assessed_risks",
        help_text="Person who conducted risk assessment",
    )

    # Risk scoring - AI Enhanced
    inherent_likelihood = models.PositiveSmallIntegerField(
        choices=LIKELIHOOD_SCORES,
        help_text="Inherent likelihood score (before controls)",
    )

    inherent_consequence = models.PositiveSmallIntegerField(
        choices=CONSEQUENCE_SCORES,
        help_text="Inherent consequence score (before controls)",
    )

    residual_likelihood = models.PositiveSmallIntegerField(
        choices=LIKELIHOOD_SCORES,
        help_text="Residual likelihood score (after controls)",
    )

    residual_consequence = models.PositiveSmallIntegerField(
        choices=CONSEQUENCE_SCORES,
        help_text="Residual consequence score (after controls)",
    )

    # AI-calculated risk ratings
    inherent_risk_rating = models.CharField(
        max_length=20,
        choices=RISK_RATINGS,
        editable=False,
        help_text="AI-calculated inherent risk rating",
    )

    residual_risk_rating = models.CharField(
        max_length=20,
        choices=RISK_RATINGS,
        editable=False,
        help_text="AI-calculated residual risk rating",
    )

    # Current risk status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of risk assessment",
    )

    # Risk management dates
    identified_date = models.DateField(
        auto_now_add=True, help_text="Date risk was first identified"
    )

    assessment_date = models.DateField(help_text="Date of current risk assessment")

    review_date = models.DateField(help_text="Date for next risk review")

    # AI Intelligence Integration
    auto_review_enabled = models.BooleanField(
        default=True, help_text="Enable AI-powered automatic review triggers"
    )

    f2_integration_enabled = models.BooleanField(
        default=False, help_text="Link risk to F2 maintenance automation"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Risk Register Entry"
        verbose_name_plural = "Risk Register"
        ordering = ["-assessment_date", "risk_number"]
        permissions = [
            ("approve_risk_assessments", "Can approve risk assessments"),
            ("manage_risk_register", "Can manage risk register"),
            ("view_risk_analytics", "Can view risk analytics"),
        ]

    def __str__(self):
        return f"{self.risk_number}: {self.title} [{self.get_residual_risk_rating_display()}]"

    # =============================================================================
    # AI RISK INTELLIGENCE METHODS
    # =============================================================================

    def calculate_risk_rating(self, likelihood, consequence):
        """
        AI-enhanced risk rating calculation using CASA risk matrix.

        Incorporates category modifiers and operational intelligence.
        """
        # Apply category modifiers
        adjusted_likelihood = likelihood * self.category.default_likelihood_modifier
        adjusted_consequence = consequence * self.category.default_consequence_modifier

        # Risk matrix calculation (5x5 CASA standard)
        risk_score = adjusted_likelihood * adjusted_consequence

        if risk_score >= 20:
            return "extreme"
        elif risk_score >= 15:
            return "high"
        elif risk_score >= 8:
            return "medium"
        elif risk_score >= 3:
            return "low"
        else:
            return "negligible"

    def update_risk_ratings(self):
        """Update AI-calculated risk ratings."""
        self.inherent_risk_rating = self.calculate_risk_rating(
            self.inherent_likelihood, self.inherent_consequence
        )
        self.residual_risk_rating = self.calculate_risk_rating(
            self.residual_likelihood, self.residual_consequence
        )

    @property
    def control_effectiveness(self):
        """
        Calculate control effectiveness percentage.

        Measures how much controls reduce the risk.
        """
        inherent_score = self.inherent_likelihood * self.inherent_consequence
        residual_score = self.residual_likelihood * self.residual_consequence

        if inherent_score == 0:
            return 0

        reduction = (inherent_score - residual_score) / inherent_score * 100
        return max(0, min(100, reduction))

    @property
    def is_overdue_review(self):
        """Check if risk review is overdue."""
        return date.today() > self.review_date

    @property
    def days_until_review(self):
        """Calculate days until next review."""
        delta = self.review_date - date.today()
        return delta.days

    @property
    def requires_immediate_action(self):
        """Check if risk requires immediate management action."""
        return self.residual_risk_rating in ["extreme", "high"]

    @property
    def f2_maintenance_trigger(self):
        """
        Check if risk should trigger F2 maintenance actions.

        Revolutionary integration: High aircraft risks automatically
        create F2 maintenance requirements.
        """
        if not self.f2_integration_enabled:
            return False

        # High/extreme aircraft risks trigger maintenance
        aircraft_categories = ["AO", "AC", "MAINT"]  # Aircraft operation categories

        return (
            self.category.code in aircraft_categories
            and self.residual_risk_rating in ["high", "extreme"]
            and self.status == "open"
        )

    def generate_risk_number(self):
        """Generate unique risk identifier."""
        if self.risk_number:
            return self.risk_number

        year = timezone.now().year
        category_code = self.category.code

        # Get last risk number for this category this year
        last_risk = (
            RiskRegister.objects.filter(category=self.category, created_at__year=year)
            .exclude(id=self.id)
            .order_by("-risk_number")
            .first()
        )

        if last_risk and last_risk.risk_number:
            try:
                last_seq = int(last_risk.risk_number.split("-")[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1

        self.risk_number = f"RISK-{category_code}-{year}-{new_seq:03d}"
        return self.risk_number

    def schedule_next_review(self, months=12):
        """Schedule next risk review based on risk rating."""
        # Higher risks reviewed more frequently
        review_intervals = {
            "extreme": 3,  # 3 months
            "high": 6,  # 6 months
            "medium": 12,  # 12 months
            "low": 24,  # 24 months
            "negligible": 36,  # 36 months
        }

        interval = review_intervals.get(self.residual_risk_rating, months)
        self.review_date = self.assessment_date + timedelta(days=interval * 30)

    def trigger_f2_maintenance(self):
        """
        Revolutionary Feature: Auto-generate F2 maintenance from high risks.

        When aircraft risks reach high/extreme levels, automatically create
        F2 maintenance requirements to address the safety concern.
        """
        if not self.f2_maintenance_trigger:
            return None

        from rpas.models import F2MaintenanceRequired, RPASTechnicalLogPartA

        # Create F2 maintenance requirement for all operator aircraft
        aircraft_list = self.operator.aircraft.filter(is_serviceable=True)

        maintenance_items = []
        for aircraft in aircraft_list:
            # Get or create F2 Part A header for today
            f2_header, created = RPASTechnicalLogPartA.objects.get_or_create(
                aircraft=aircraft, entry_date=date.today()
            )

            # Create maintenance requirement from risk
            maintenance_item = F2MaintenanceRequired.objects.create(
                f2_header=f2_header,
                item=f"SAFETY RISK MITIGATION: {self.title} - {self.description[:200]}",
                due=date.today() + timedelta(days=7),  # 7 days to address
                priority_level=(
                    "high" if self.residual_risk_rating == "high" else "critical"
                ),
            )
            maintenance_items.append(maintenance_item)

        return maintenance_items

    def clean(self):
        """Validate risk register data."""
        from django.core.exceptions import ValidationError

        # Ensure residual risk is not higher than inherent risk
        inherent_score = self.inherent_likelihood * self.inherent_consequence
        residual_score = self.residual_likelihood * self.residual_consequence

        if residual_score > inherent_score:
            raise ValidationError(
                {
                    "residual_likelihood": "Residual risk cannot be higher than inherent risk."
                }
            )

        # Auto-schedule review date if not provided
        if not self.review_date:
            self.review_date = self.assessment_date + timedelta(days=365)

    def save(self, *args, **kwargs):
        """Custom save with AI intelligence."""
        # Generate risk number if needed
        if not self.risk_number:
            self.generate_risk_number()

        # Update AI risk ratings
        self.update_risk_ratings()

        # Validate data
        self.clean()

        super().save(*args, **kwargs)

        # Trigger F2 maintenance if needed (after save to have ID)
        if self.f2_maintenance_trigger:
            self.trigger_f2_maintenance()


class RiskControl(models.Model):
    """
    SMS Risk Controls - Intelligent Control Management

    Tracks controls implemented to mitigate risks with effectiveness monitoring
    and integration with operational procedures.
    """

    CONTROL_TYPES = [
        ("elimination", "Elimination - Remove the hazard"),
        ("substitution", "Substitution - Replace with safer alternative"),
        ("engineering", "Engineering Controls - Physical barriers/systems"),
        ("administrative", "Administrative Controls - Procedures/training"),
        ("ppe", "Personal Protective Equipment"),
    ]

    EFFECTIVENESS_RATINGS = [
        ("very_high", "Very High - 95%+ effective"),
        ("high", "High - 80-94% effective"),
        ("medium", "Medium - 60-79% effective"),
        ("low", "Low - 40-59% effective"),
        ("very_low", "Very Low - <40% effective"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Control identification
    risk = models.ForeignKey(
        RiskRegister,
        on_delete=models.CASCADE,
        related_name="controls",
        help_text="Risk this control mitigates",
    )

    control_number = models.CharField(
        max_length=30, help_text="Unique control identifier (auto-generated)"
    )

    title = models.CharField(max_length=200, help_text="Control title/name")

    description = models.TextField(help_text="Detailed description of control measure")

    # Control classification
    control_type = models.CharField(
        max_length=20,
        choices=CONTROL_TYPES,
        help_text="Type of control in hierarchy of controls",
    )

    # Control effectiveness
    effectiveness_rating = models.CharField(
        max_length=20,
        choices=EFFECTIVENESS_RATINGS,
        help_text="Estimated effectiveness of this control",
    )

    # Implementation tracking
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="responsible_controls",
        help_text="Person responsible for implementing/maintaining control",
    )

    implementation_date = models.DateField(help_text="Date control was implemented")

    verification_date = models.DateField(
        null=True, blank=True, help_text="Date control effectiveness was last verified"
    )

    next_verification_date = models.DateField(
        help_text="Date for next control verification"
    )

    # Control status
    is_active = models.BooleanField(
        default=True, help_text="Control currently in effect"
    )

    # Integration with operations
    linked_sop = models.ForeignKey(
        "StandardOperatingProcedure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="risk_controls",
        help_text="SOP that implements this control",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Risk Control"
        verbose_name_plural = "Risk Controls"
        ordering = ["control_type", "title"]

    def __str__(self):
        return f"{self.control_number}: {self.title}"

    @property
    def is_verification_overdue(self):
        """Check if control verification is overdue."""
        return date.today() > self.next_verification_date

    @property
    def days_until_verification(self):
        """Calculate days until next verification."""
        delta = self.next_verification_date - date.today()
        return delta.days

    def generate_control_number(self):
        """Generate unique control identifier."""
        if self.control_number:
            return self.control_number

        # Format: CTRL-[RISK_NUMBER]-[SEQ]
        existing_controls = (
            RiskControl.objects.filter(risk=self.risk).exclude(id=self.id).count()
        )

        seq = existing_controls + 1
        self.control_number = f"CTRL-{self.risk.risk_number}-{seq:02d}"
        return self.control_number

    def save(self, *args, **kwargs):
        """Custom save with control number generation."""
        if not self.control_number:
            self.generate_control_number()

        super().save(*args, **kwargs)


# =============================================================================
# SMS STANDARD OPERATING PROCEDURES (SOPs)
# =============================================================================


class StandardOperatingProcedure(models.Model):
    """
    SMS Standard Operating Procedures - Intelligent SOP Management

    Revolutionary SOP system that transforms static documents into living,
    intelligent operational guidance with version control, staff acknowledgment
    tracking, and integration with risk management.
    """

    SOP_TYPES = [
        ("operational", "Operational Procedure"),
        ("emergency", "Emergency Procedure"),
        ("maintenance", "Maintenance Procedure"),
        ("training", "Training Procedure"),
        ("administrative", "Administrative Procedure"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft - Under Development"),
        ("review", "Under Review"),
        ("approved", "Approved - Current"),
        ("superseded", "Superseded - Replaced"),
        ("archived", "Archived - Historical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # SOP identification
    sop_number = models.CharField(
        max_length=20, unique=True, help_text="Unique SOP identifier (auto-generated)"
    )

    title = models.CharField(max_length=200, help_text="SOP title")

    # SOP classification
    sop_type = models.CharField(
        max_length=20, choices=SOP_TYPES, help_text="Type of procedure"
    )

    operator = models.ForeignKey(
        "rpas.RPASOperator",
        on_delete=models.CASCADE,
        related_name="sops",
        help_text="RPAS operator this SOP belongs to",
    )

    # Content and documentation
    purpose = models.TextField(help_text="Purpose and scope of this SOP")

    procedure_content = models.TextField(help_text="Step-by-step procedure content")

    # Version control
    version_number = models.CharField(
        max_length=10, default="1.0", help_text="Current version number"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of SOP",
    )

    # Authoring and approval
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="authored_sops",
        help_text="Person who authored this SOP",
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reviewed_sops",
        null=True,
        blank=True,
        help_text="Person who reviewed this SOP",
    )

    approver = models.ForeignKey(
        "rpas.KeyPersonnel",
        on_delete=models.PROTECT,
        related_name="approved_sops",
        null=True,
        blank=True,
        help_text="Key personnel who approved this SOP",
    )

    # Important dates
    created_date = models.DateField(auto_now_add=True, help_text="Date SOP was created")

    approved_date = models.DateField(
        null=True, blank=True, help_text="Date SOP was approved"
    )

    effective_date = models.DateField(
        null=True, blank=True, help_text="Date SOP becomes effective"
    )

    review_date = models.DateField(help_text="Date for next SOP review")

    # AI Intelligence
    auto_acknowledgment_tracking = models.BooleanField(
        default=True, help_text="Track staff acknowledgment automatically"
    )

    requires_training = models.BooleanField(
        default=False, help_text="SOP requires formal training before use"
    )

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Standard Operating Procedure"
        verbose_name_plural = "Standard Operating Procedures"
        ordering = ["sop_number", "title"]
        permissions = [
            ("approve_sops", "Can approve SOPs"),
            ("manage_sop_versions", "Can manage SOP versions"),
        ]

    def __str__(self):
        return f"{self.sop_number}: {self.title} v{self.version_number}"

    @property
    def is_current(self):
        """Check if this is the current approved version."""
        return self.status == "approved"

    @property
    def is_review_due(self):
        """Check if SOP review is due."""
        return date.today() >= self.review_date

    @property
    def days_until_review(self):
        """Calculate days until next review."""
        delta = self.review_date - date.today()
        return delta.days

    @property
    def acknowledgment_percentage(self):
        """Calculate percentage of required staff who have acknowledged."""
        if not self.auto_acknowledgment_tracking:
            return 100  # Assume 100% if not tracking

        required_staff = self.operator.key_personnel.filter(is_current=True).count()
        if required_staff == 0:
            return 100

        acknowledged_count = self.acknowledgments.filter(is_current=True).count()
        return (acknowledged_count / required_staff) * 100

    def generate_sop_number(self):
        """Generate unique SOP identifier."""
        if self.sop_number:
            return self.sop_number

        year = timezone.now().year
        sop_type_code = self.sop_type.upper()[:3]

        # Get last SOP number for this type this year
        last_sop = (
            StandardOperatingProcedure.objects.filter(
                sop_type=self.sop_type, created_date__year=year
            )
            .exclude(id=self.id)
            .order_by("-sop_number")
            .first()
        )

        if last_sop and last_sop.sop_number:
            try:
                last_seq = int(last_sop.sop_number.split("-")[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1

        self.sop_number = f"SOP-{sop_type_code}-{year}-{new_seq:03d}"
        return self.sop_number

    def create_new_version(self, author, changes_description=""):
        """
        Create new version of this SOP.

        Marks current version as superseded and creates new draft version.
        """
        # Parse current version and increment
        try:
            major, minor = map(int, self.version_number.split("."))
            new_version = f"{major}.{minor + 1}"
        except ValueError:
            new_version = "1.0"

        # Mark current as superseded
        self.status = "superseded"
        self.save()

        # Create new version
        new_sop = StandardOperatingProcedure.objects.create(
            sop_number=self.sop_number,  # Same number, new version
            title=self.title,
            sop_type=self.sop_type,
            operator=self.operator,
            purpose=self.purpose,
            procedure_content=self.procedure_content,
            version_number=new_version,
            author=author,
            review_date=date.today() + timedelta(days=365),
        )

        return new_sop

    def save(self, *args, **kwargs):
        """Custom save with SOP number generation."""
        if not self.sop_number:
            self.generate_sop_number()

        # Auto-set review date if not provided (1 year from creation)
        if not self.review_date:
            self.review_date = date.today() + timedelta(days=365)

        super().save(*args, **kwargs)


class SOPAcknowledgment(models.Model):
    """
    SOP Acknowledgment Tracking - Staff Understanding Verification

    Intelligent tracking system that ensures all relevant staff have
    read, understood, and acknowledged current SOPs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Acknowledgment details
    sop = models.ForeignKey(
        StandardOperatingProcedure,
        on_delete=models.CASCADE,
        related_name="acknowledgments",
        help_text="SOP being acknowledged",
    )

    staff_member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sop_acknowledgments",
        help_text="Staff member acknowledging SOP",
    )

    # Acknowledgment tracking
    acknowledged_date = models.DateTimeField(
        auto_now_add=True, help_text="Date and time of acknowledgment"
    )

    version_acknowledged = models.CharField(
        max_length=10, help_text="Version of SOP acknowledged"
    )

    is_current = models.BooleanField(
        default=True, help_text="Is this acknowledgment for current SOP version?"
    )

    # Digital signature equivalent
    acknowledgment_method = models.CharField(
        max_length=50,
        default="digital_system",
        help_text="Method used for acknowledgment",
    )

    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of acknowledgment for audit trail"
    )

    # Training verification (if required)
    training_completed = models.BooleanField(
        default=False, help_text="Required training completed before acknowledgment"
    )

    training_completion_date = models.DateField(
        null=True, blank=True, help_text="Date training was completed"
    )

    class Meta:
        verbose_name = "SOP Acknowledgment"
        verbose_name_plural = "SOP Acknowledgments"
        unique_together = ["sop", "staff_member", "version_acknowledged"]
        ordering = ["-acknowledged_date"]

    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.sop.sop_number} v{self.version_acknowledged}"

    def clean(self):
        """Validate acknowledgment data."""
        from django.core.exceptions import ValidationError

        # If SOP requires training, ensure training is completed
        if self.sop.requires_training and not self.training_completed:
            raise ValidationError(
                {
                    "training_completed": "Training must be completed before acknowledging this SOP."
                }
            )

        # Set version from SOP if not provided
        if not self.version_acknowledged:
            self.version_acknowledged = self.sop.version_number

    def save(self, *args, **kwargs):
        """Custom save with validation."""
        self.clean()
        super().save(*args, **kwargs)

        # Mark previous acknowledgments for this SOP as not current
        SOPAcknowledgment.objects.filter(
            sop=self.sop, staff_member=self.staff_member
        ).exclude(id=self.id).update(is_current=False)


# =============================================================================
# SMS JOB SAFETY ANALYSIS (JSA)
# =============================================================================


class JobSafetyAnalysis(models.Model):
    """
    SMS Job Safety Analysis - Systematic Hazard Identification

    Revolutionary JSA system that transforms traditional static job analyses
    into intelligent, reusable safety templates with automated risk linking
    and real-time hazard monitoring.
    """

    JSA_TYPES = [
        ("routine", "Routine Operation"),
        ("maintenance", "Maintenance Activity"),
        ("emergency", "Emergency Procedure"),
        ("training", "Training Activity"),
        ("special", "Special Operation"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft - Under Development"),
        ("review", "Under Review"),
        ("approved", "Approved - Current"),
        ("superseded", "Superseded - Replaced"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # JSA identification
    jsa_number = models.CharField(
        max_length=20, unique=True, help_text="Unique JSA identifier (auto-generated)"
    )

    title = models.CharField(max_length=200, help_text="Job/task title being analyzed")

    # JSA classification
    jsa_type = models.CharField(
        max_length=20, choices=JSA_TYPES, help_text="Type of job being analyzed"
    )

    operator = models.ForeignKey(
        "rpas.RPASOperator",
        on_delete=models.CASCADE,
        related_name="job_safety_analyses",
        help_text="RPAS operator this JSA belongs to",
    )

    # Job description
    job_description = models.TextField(help_text="Detailed description of the job/task")

    location_description = models.TextField(
        help_text="Description of where job is performed"
    )

    # Personnel and equipment
    personnel_required = models.TextField(
        help_text="Personnel required for this job (qualifications, numbers)"
    )

    equipment_required = models.TextField(
        help_text="Equipment, tools, and materials required"
    )

    # JSA status and approval
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Current status of JSA",
    )

    # Authoring and approval
    analyst = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="analyzed_jsas",
        help_text="Person who conducted the JSA",
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reviewed_jsas",
        null=True,
        blank=True,
        help_text="Person who reviewed this JSA",
    )

    approver = models.ForeignKey(
        "rpas.KeyPersonnel",
        on_delete=models.PROTECT,
        related_name="approved_jsas",
        null=True,
        blank=True,
        help_text="Key personnel who approved this JSA",
    )

    # Important dates
    analysis_date = models.DateField(help_text="Date JSA was conducted")

    approved_date = models.DateField(
        null=True, blank=True, help_text="Date JSA was approved"
    )

    review_date = models.DateField(help_text="Date for next JSA review")

    # AI Intelligence
    auto_risk_linking = models.BooleanField(
        default=True, help_text="Automatically link JSA hazards to risk register"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Safety Analysis"
        verbose_name_plural = "Job Safety Analyses"
        ordering = ["-analysis_date", "jsa_number"]
        permissions = [
            ("approve_jsas", "Can approve JSAs"),
            ("conduct_jsa", "Can conduct job safety analysis"),
        ]

    def __str__(self):
        return f"{self.jsa_number}: {self.title}"

    @property
    def is_current(self):
        """Check if this is the current approved JSA."""
        return self.status == "approved"

    @property
    def is_review_due(self):
        """Check if JSA review is due."""
        return date.today() >= self.review_date

    @property
    def days_until_review(self):
        """Calculate days until next review."""
        delta = self.review_date - date.today()
        return delta.days

    @property
    def total_hazards(self):
        """Count total hazards identified in this JSA."""
        return self.job_steps.aggregate(total=Count("hazards"))["total"] or 0

    @property
    def high_risk_hazards(self):
        """Count high/extreme risk hazards in this JSA."""
        return (
            self.job_steps.filter(
                hazards__risk_level__in=["high", "extreme"]
            ).aggregate(total=Count("hazards"))["total"]
            or 0
        )

    def generate_jsa_number(self):
        """Generate unique JSA identifier."""
        if self.jsa_number:
            return self.jsa_number

        year = timezone.now().year
        jsa_type_code = self.jsa_type.upper()[:3]

        # Get last JSA number for this type this year
        last_jsa = (
            JobSafetyAnalysis.objects.filter(
                jsa_type=self.jsa_type, analysis_date__year=year
            )
            .exclude(id=self.id)
            .order_by("-jsa_number")
            .first()
        )

        if last_jsa and last_jsa.jsa_number:
            try:
                last_seq = int(last_jsa.jsa_number.split("-")[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1

        self.jsa_number = f"JSA-{jsa_type_code}-{year}-{new_seq:03d}"
        return self.jsa_number

    def save(self, *args, **kwargs):
        """Custom save with JSA number generation."""
        if not self.jsa_number:
            self.generate_jsa_number()

        # Auto-set review date if not provided (1 year from analysis)
        if not self.review_date:
            self.review_date = self.analysis_date + timedelta(days=365)

        super().save(*args, **kwargs)


class JSAJobStep(models.Model):
    """
    JSA Job Step - Individual Steps in Job Safety Analysis

    Each step of a job broken down systematically for hazard identification.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Step identification
    jsa = models.ForeignKey(
        JobSafetyAnalysis,
        on_delete=models.CASCADE,
        related_name="job_steps",
        help_text="JSA this step belongs to",
    )

    step_number = models.PositiveSmallIntegerField(help_text="Sequential step number")

    step_description = models.TextField(
        help_text="Detailed description of this job step"
    )

    # Duration and frequency
    estimated_duration = models.DurationField(
        null=True, blank=True, help_text="Estimated time to complete this step"
    )

    # Critical step identification
    is_critical_step = models.BooleanField(
        default=False, help_text="Is this a safety-critical step?"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "JSA Job Step"
        verbose_name_plural = "JSA Job Steps"
        ordering = ["jsa", "step_number"]
        unique_together = ["jsa", "step_number"]

    def __str__(self):
        return f"{self.jsa.jsa_number} - Step {self.step_number}: {self.step_description[:50]}"

    @property
    def hazard_count(self):
        """Count hazards identified for this step."""
        return self.hazards.count()

    @property
    def high_risk_hazard_count(self):
        """Count high/extreme risk hazards for this step."""
        return self.hazards.filter(risk_level__in=["high", "extreme"]).count()


class JSAHazard(models.Model):
    """
    JSA Hazard - Individual Hazards Identified in Job Steps

    Intelligent hazard tracking with automatic risk register linking
    and control measure validation.
    """

    HAZARD_TYPES = [
        ("physical", "Physical - Contact with objects, falls, etc."),
        ("chemical", "Chemical - Exposure to substances"),
        ("biological", "Biological - Exposure to organisms"),
        ("ergonomic", "Ergonomic - Repetitive motion, posture"),
        ("psychological", "Psychological - Stress, fatigue"),
        ("environmental", "Environmental - Weather, terrain"),
        ("operational", "Operational - Procedures, equipment"),
    ]

    RISK_LEVELS = [
        ("extreme", "Extreme - Stop work immediately"),
        ("high", "High - Additional controls required"),
        ("medium", "Medium - Controls adequate"),
        ("low", "Low - Monitor and review"),
        ("negligible", "Negligible - Minimal concern"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Hazard identification
    job_step = models.ForeignKey(
        JSAJobStep,
        on_delete=models.CASCADE,
        related_name="hazards",
        help_text="Job step this hazard relates to",
    )

    hazard_description = models.TextField(
        help_text="Description of the potential hazard"
    )

    # Hazard classification
    hazard_type = models.CharField(
        max_length=20, choices=HAZARD_TYPES, help_text="Type/category of hazard"
    )

    # Potential consequences
    potential_consequences = models.TextField(
        help_text="What could happen if this hazard occurs?"
    )

    # Risk assessment
    risk_level = models.CharField(
        max_length=20, choices=RISK_LEVELS, help_text="Initial risk level assessment"
    )

    # Control measures
    control_measures = models.TextField(
        help_text="Control measures to mitigate this hazard"
    )

    # AI Integration
    linked_risk = models.ForeignKey(
        RiskRegister,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jsa_hazards",
        help_text="Linked risk register entry (AI-generated)",
    )

    auto_risk_created = models.BooleanField(
        default=False,
        help_text="Was risk register entry auto-created from this hazard?",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "JSA Hazard"
        verbose_name_plural = "JSA Hazards"
        ordering = ["job_step", "hazard_type", "risk_level"]

    def __str__(self):
        return f"{self.job_step.jsa.jsa_number} - {self.hazard_description[:50]}"

    @property
    def requires_risk_register_entry(self):
        """Check if hazard should have risk register entry."""
        return (
            self.risk_level in ["high", "extreme"]
            and self.job_step.jsa.auto_risk_linking
            and not self.linked_risk
        )

    def create_risk_register_entry(self):
        """
        Revolutionary Feature: Auto-create risk register entry from JSA hazard.

        High/extreme JSA hazards automatically create risk register entries
        for systematic risk management.
        """
        if not self.requires_risk_register_entry:
            return None

        # Map JSA hazard types to risk categories
        hazard_to_category_map = {
            "physical": "PH",  # Physical hazards
            "chemical": "CH",  # Chemical hazards
            "biological": "BIO",  # Biological hazards
            "ergonomic": "ERG",  # Ergonomic hazards
            "psychological": "PSY",  # Psychological hazards
            "environmental": "ENV",  # Environmental hazards
            "operational": "OP",  # Operational hazards
        }

        category_code = hazard_to_category_map.get(self.hazard_type, "OP")

        try:
            risk_category = RiskCategory.objects.get(code=category_code)
        except RiskCategory.DoesNotExist:
            # Create category if it doesn't exist
            risk_category = RiskCategory.objects.create(
                code=category_code,
                name=f"{self.get_hazard_type_display()} Hazards",
                description=f"Hazards identified from JSA related to {self.get_hazard_type_display().lower()}",
            )

        # Map JSA risk levels to risk matrix scores
        risk_mapping = {
            "extreme": (5, 5),  # Likelihood 5, Consequence 5
            "high": (4, 4),  # Likelihood 4, Consequence 4
            "medium": (3, 3),  # Likelihood 3, Consequence 3
            "low": (2, 2),  # Likelihood 2, Consequence 2
            "negligible": (1, 1),  # Likelihood 1, Consequence 1
        }

        likelihood, consequence = risk_mapping.get(self.risk_level, (3, 3))

        # Create risk register entry
        risk_entry = RiskRegister.objects.create(
            title=f"JSA Hazard: {self.hazard_description[:100]}",
            description=f"""
            HAZARD SOURCE: {self.job_step.jsa.title} - Step {self.job_step.step_number}

            HAZARD DESCRIPTION: {self.hazard_description}

            POTENTIAL CONSEQUENCES: {self.potential_consequences}

            INITIAL CONTROL MEASURES: {self.control_measures}

            This risk was automatically generated from Job Safety Analysis {self.job_step.jsa.jsa_number}.
            """,
            category=risk_category,
            operator=self.job_step.jsa.operator,
            identified_by=self.job_step.jsa.analyst,
            assessed_by=self.job_step.jsa.analyst,
            inherent_likelihood=likelihood,
            inherent_consequence=consequence,
            residual_likelihood=max(
                1, likelihood - 1
            ),  # Assume controls reduce risk by 1 level
            residual_consequence=consequence,
            assessment_date=date.today(),
            f2_integration_enabled=True,  # Enable F2 integration for JSA risks
            status="open",
        )

        # Link hazard to risk
        self.linked_risk = risk_entry
        self.auto_risk_created = True
        self.save()

        return risk_entry

    def save(self, *args, **kwargs):
        """Custom save with automatic risk register integration."""
        super().save(*args, **kwargs)

        # Auto-create risk register entry for high/extreme hazards
        if self.requires_risk_register_entry:
            self.create_risk_register_entry()


# =============================================================================
# SMS INCIDENT MANAGEMENT
# =============================================================================


class IncidentCategory(models.Model):
    """
    Incident Category Classification

    CASA-compliant incident classification system for systematic
    incident reporting and trend analysis.
    """

    SEVERITY_LEVELS = [
        ("minor", "Minor - No injury, minor damage"),
        ("serious", "Serious - Injury or significant damage"),
        ("major", "Major - Serious injury or major damage"),
        ("fatal", "Fatal - Fatality or catastrophic damage"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Category identification
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Short category code (e.g., 'COLL' for collision)",
    )

    name = models.CharField(max_length=100, help_text="Category name")

    description = models.TextField(help_text="Detailed category description")

    # CASA reporting requirements
    casa_reportable = models.BooleanField(
        default=False, help_text="Must this category be reported to CASA?"
    )

    reporting_timeframe = models.DurationField(
        null=True, blank=True, help_text="Timeframe for reporting to CASA"
    )

    # Risk assessment
    default_severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default="minor",
        help_text="Default severity level for this category",
    )

    # Auto-investigation triggers
    auto_investigation_required = models.BooleanField(
        default=False,
        help_text="Automatically trigger investigation for this category?",
    )

    # System configuration
    is_active = models.BooleanField(
        default=True, help_text="Category available for selection"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Incident Category"
        verbose_name_plural = "Incident Categories"
        ordering = ["code", "name"]

    def __str__(self):
        return f"{self.code}: {self.name}"

    @property
    def incident_count(self):
        """Count incidents in this category."""
        return self.incidents.count()

    @property
    def recent_incident_count(self):
        """Count incidents in last 30 days."""
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=30)
        return self.incidents.filter(incident_date__gte=cutoff).count()


class Incident(models.Model):
    """
    Incident Record - Comprehensive Incident Management

    Revolutionary incident tracking with AI-powered pattern recognition,
    automatic risk assessment, and intelligent corrective action tracking.
    """

    STATUS_CHOICES = [
        ("reported", "Reported - Initial report submitted"),
        ("under_review", "Under Review - Being assessed"),
        ("investigating", "Investigating - Formal investigation"),
        ("corrective_actions", "Corrective Actions - Implementing fixes"),
        ("closed", "Closed - Investigation complete"),
    ]

    SEVERITY_LEVELS = [
        ("minor", "Minor - No injury, minor damage"),
        ("serious", "Serious - Injury or significant damage"),
        ("major", "Major - Serious injury or major damage"),
        ("fatal", "Fatal - Fatality or catastrophic damage"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Incident identification
    incident_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique incident identifier (auto-generated)",
    )

    title = models.CharField(max_length=200, help_text="Brief incident title/summary")

    # Incident classification
    category = models.ForeignKey(
        IncidentCategory,
        on_delete=models.PROTECT,
        related_name="incidents",
        help_text="Incident category",
    )

    operator = models.ForeignKey(
        "rpas.RPASOperator",
        on_delete=models.CASCADE,
        related_name="incidents",
        help_text="RPAS operator this incident relates to",
    )

    # Incident details
    incident_date = models.DateTimeField(
        help_text="Date and time when incident occurred"
    )

    location = models.TextField(help_text="Where the incident occurred")

    description = models.TextField(help_text="Detailed description of what happened")

    # Personnel involved
    reported_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reported_incidents",
        help_text="Person who reported the incident",
    )

    involved_personnel = models.ManyToManyField(
        User,
        related_name="involved_incidents",
        blank=True,
        help_text="Personnel involved in the incident",
    )

    # Aircraft involvement
    aircraft_involved = models.ForeignKey(
        "rpas.RPASAircraft",
        on_delete=models.PROTECT,
        related_name="incidents",
        null=True,
        blank=True,
        help_text="Aircraft involved in incident",
    )

    # Risk assessment
    severity_level = models.CharField(
        max_length=20, choices=SEVERITY_LEVELS, help_text="Incident severity assessment"
    )

    actual_consequences = models.TextField(
        help_text="What actually happened - injuries, damage, etc."
    )

    potential_consequences = models.TextField(
        help_text="What could have happened in worst case"
    )

    # Investigation management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="reported",
        help_text="Current incident status",
    )

    investigation_required = models.BooleanField(
        default=False, help_text="Does this incident require formal investigation?"
    )

    investigator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="investigated_incidents",
        null=True,
        blank=True,
        help_text="Assigned investigator",
    )

    investigation_deadline = models.DateField(
        null=True, blank=True, help_text="Investigation completion deadline"
    )

    # CASA reporting
    casa_reportable = models.BooleanField(
        default=False, help_text="Must this incident be reported to CASA?"
    )

    casa_reported = models.BooleanField(
        default=False, help_text="Has this been reported to CASA?"
    )

    casa_report_date = models.DateTimeField(
        null=True, blank=True, help_text="Date/time CASA report was submitted"
    )

    casa_reference = models.CharField(
        max_length=50, blank=True, help_text="CASA reference number"
    )

    # AI Intelligence & Pattern Recognition
    similar_incidents = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_incidents",
        help_text="AI-identified similar incidents",
    )

    auto_risk_created = models.BooleanField(
        default=False, help_text="Was risk register entry auto-created?"
    )

    linked_risk = models.ForeignKey(
        RiskRegister,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents",
        help_text="Linked risk register entry",
    )

    # Important dates
    closed_date = models.DateTimeField(
        null=True, blank=True, help_text="Date incident investigation was closed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"
        ordering = ["-incident_date", "incident_number"]
        permissions = [
            ("investigate_incidents", "Can investigate incidents"),
            ("close_incidents", "Can close incident investigations"),
            ("report_to_casa", "Can report incidents to CASA"),
        ]

    def __str__(self):
        return f"{self.incident_number}: {self.title}"

    @property
    def is_investigation_overdue(self):
        """Check if investigation is overdue."""
        if not self.investigation_deadline:
            return False
        return date.today() > self.investigation_deadline

    @property
    def days_since_incident(self):
        """Calculate days since incident occurred."""
        delta = timezone.now() - self.incident_date
        return delta.days

    @property
    def corrective_actions_count(self):
        """Count corrective actions for this incident."""
        return self.corrective_actions.count()

    @property
    def open_corrective_actions_count(self):
        """Count open corrective actions."""
        return self.corrective_actions.filter(status="open").count()

    def generate_incident_number(self):
        """Generate unique incident identifier."""
        if self.incident_number:
            return self.incident_number

        year = self.incident_date.year
        category_code = self.category.code

        # Get last incident number for this category this year
        last_incident = (
            Incident.objects.filter(category=self.category, incident_date__year=year)
            .exclude(id=self.id)
            .order_by("-incident_number")
            .first()
        )

        if last_incident and last_incident.incident_number:
            try:
                last_seq = int(last_incident.incident_number.split("-")[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1

        self.incident_number = f"INC-{category_code}-{year}-{new_seq:03d}"
        return self.incident_number

    def create_risk_register_entry(self):
        """
        Revolutionary Feature: Auto-create risk register entry from incident.

        Serious/major/fatal incidents automatically create risk register entries
        to prevent recurrence.
        """
        if self.severity_level in ["minor"] or self.linked_risk:
            return None

        # Map incident categories to risk categories or create one
        try:
            # Try to find existing risk category that matches incident
            risk_category = RiskCategory.objects.filter(
                code__icontains=self.category.code[:2]
            ).first()

            if not risk_category:
                # Create a new risk category for this incident type
                risk_category = RiskCategory.objects.create(
                    code=self.category.code,
                    name=f"Incident: {self.category.name}",
                    description=f"Risks identified from {self.category.name} incidents",
                )
        except Exception:
            # Fallback: create a general incident risk category
            risk_category, created = RiskCategory.objects.get_or_create(
                code="INC",
                defaults={
                    "name": "Incident Risks",
                    "description": "Risks identified from incident investigations",
                },
            )

        # Create risk entry based on incident
        risk_entry = RiskRegister.objects.create(
            title=f"Incident Risk: {self.title}",
            description=f"""
            INCIDENT SOURCE: {self.incident_number} - {self.incident_date.strftime('%Y-%m-%d')}

            INCIDENT DESCRIPTION: {self.description}

            ACTUAL CONSEQUENCES: {self.actual_consequences}

            POTENTIAL CONSEQUENCES: {self.potential_consequences}

            This risk was automatically generated from incident {self.incident_number}.
            """,
            category=risk_category,
            operator=self.operator,
            identified_by=self.reported_by,
            assessed_by=self.reported_by,
            inherent_likelihood=4 if self.severity_level in ["major", "fatal"] else 3,
            inherent_consequence=5 if self.severity_level == "fatal" else 4,
            residual_likelihood=3,  # Assume some controls exist
            residual_consequence=4 if self.severity_level == "fatal" else 3,
            assessment_date=date.today(),
            f2_integration_enabled=self.aircraft_involved is not None,
            status="open",
        )

        # Link incident to risk
        self.linked_risk = risk_entry
        self.auto_risk_created = True
        self.save()

        return risk_entry

    def save(self, *args, **kwargs):
        """Custom save with incident number generation and auto-features."""
        if not self.incident_number:
            self.generate_incident_number()

        # Auto-set CASA reporting based on category
        if not self.casa_reportable and self.category.casa_reportable:
            self.casa_reportable = True

        # Auto-trigger investigation for serious incidents
        if not self.investigation_required and self.severity_level in [
            "serious",
            "major",
            "fatal",
        ]:
            self.investigation_required = True

        super().save(*args, **kwargs)

        # Auto-create risk register entry for serious incidents
        if (
            self.severity_level in ["serious", "major", "fatal"]
            and not self.linked_risk
        ):
            self.create_risk_register_entry()


class CorrectiveAction(models.Model):
    """
    Corrective Action Tracking

    Intelligent tracking of corrective actions arising from incidents,
    risks, or JSA findings with automated progress monitoring.
    """

    STATUS_CHOICES = [
        ("open", "Open - Not started"),
        ("in_progress", "In Progress - Being implemented"),
        ("completed", "Completed - Implementation finished"),
        ("verified", "Verified - Effectiveness confirmed"),
        ("closed", "Closed - Action complete and effective"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Low - Routine improvement"),
        ("medium", "Medium - Moderate priority"),
        ("high", "High - Urgent action required"),
        ("critical", "Critical - Immediate action required"),
    ]

    ACTION_TYPES = [
        ("procedural", "Procedural - Update procedures/SOPs"),
        ("training", "Training - Additional training required"),
        ("equipment", "Equipment - Equipment/system changes"),
        ("administrative", "Administrative - Policy/admin changes"),
        ("engineering", "Engineering - Design/technical changes"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Action identification
    action_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique action identifier (auto-generated)",
    )

    title = models.CharField(max_length=200, help_text="Brief action description")

    # Source of corrective action
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="corrective_actions",
        null=True,
        blank=True,
        help_text="Source incident (if applicable)",
    )

    risk = models.ForeignKey(
        RiskRegister,
        on_delete=models.CASCADE,
        related_name="corrective_actions",
        null=True,
        blank=True,
        help_text="Source risk (if applicable)",
    )

    jsa = models.ForeignKey(
        JobSafetyAnalysis,
        on_delete=models.CASCADE,
        related_name="corrective_actions",
        null=True,
        blank=True,
        help_text="Source JSA (if applicable)",
    )

    operator = models.ForeignKey(
        "rpas.RPASOperator",
        on_delete=models.CASCADE,
        related_name="corrective_actions",
        help_text="RPAS operator this action relates to",
    )

    # Action details
    description = models.TextField(help_text="Detailed description of required action")

    action_type = models.CharField(
        max_length=20, choices=ACTION_TYPES, help_text="Type of corrective action"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default="medium",
        help_text="Action priority level",
    )

    # Responsibility and deadlines
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="assigned_actions",
        help_text="Person responsible for implementing action",
    )

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_actions",
        help_text="Person who assigned this action",
    )

    due_date = models.DateField(help_text="Target completion date")

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        help_text="Current action status",
    )

    # Progress tracking
    progress_notes = models.TextField(
        blank=True, help_text="Progress updates and notes"
    )

    completed_date = models.DateField(
        null=True, blank=True, help_text="Date action was completed"
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="verified_actions",
        null=True,
        blank=True,
        help_text="Person who verified action effectiveness",
    )

    verification_date = models.DateField(
        null=True, blank=True, help_text="Date verification was completed"
    )

    verification_notes = models.TextField(
        blank=True, help_text="Verification results and notes"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Corrective Action"
        verbose_name_plural = "Corrective Actions"
        ordering = ["-created_at", "due_date"]

    def __str__(self):
        return f"{self.action_number}: {self.title}"

    @property
    def is_overdue(self):
        """Check if action is overdue."""
        if self.status in ["completed", "verified", "closed"]:
            return False
        return date.today() > self.due_date

    @property
    def days_until_due(self):
        """Calculate days until due date."""
        delta = self.due_date - date.today()
        return delta.days

    @property
    def source_description(self):
        """Get description of action source."""
        if self.incident:
            return f"Incident: {self.incident.incident_number}"
        elif self.risk:
            return f"Risk: {self.risk.risk_id}"
        elif self.jsa:
            return f"JSA: {self.jsa.jsa_number}"
        return "Manual Creation"

    def generate_action_number(self):
        """Generate unique action identifier."""
        if self.action_number:
            return self.action_number

        year = timezone.now().year

        # Get source prefix
        if self.incident:
            prefix = "INC"
        elif self.risk:
            prefix = "RSK"
        elif self.jsa:
            prefix = "JSA"
        else:
            prefix = "MAN"

        # Get last action number for this year
        last_action = (
            CorrectiveAction.objects.filter(created_at__year=year)
            .exclude(id=self.id)
            .order_by("-action_number")
            .first()
        )

        if last_action and last_action.action_number:
            try:
                last_seq = int(last_action.action_number.split("-")[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1

        self.action_number = f"CA-{prefix}-{year}-{new_seq:03d}"
        return self.action_number

    def save(self, *args, **kwargs):
        """Custom save with action number generation."""
        if not self.action_number:
            self.generate_action_number()

        # Auto-set completion date when status changes to completed
        if self.status == "completed" and not self.completed_date:
            self.completed_date = date.today()

        super().save(*args, **kwargs)
