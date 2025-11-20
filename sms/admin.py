"""
SMS Admin Configuration - Intelligent Safety Management Interface

Admin interface for the revolutionary SMS that transforms safety from
bureaucratic burden into intelligent competitive advantage.
"""

from datetime import date

from django.contrib import admin, messages
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    CorrectiveAction,
    Incident,
    IncidentCategory,
    JobSafetyAnalysis,
    JSAHazard,
    JSAJobStep,
    RiskCategory,
    RiskControl,
    RiskRegister,
    SOPAcknowledgment,
    StandardOperatingProcedure,
)


@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    """Admin interface for risk categories."""

    list_display = [
        "code",
        "name",
        "active_risks_display",
        "high_risks_display",
        "is_active",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "code", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Category Information",
            {"fields": ("name", "code", "description", "casa_reference", "is_active")},
        ),
        (
            "AI Intelligence Settings",
            {
                "fields": (
                    "default_likelihood_modifier",
                    "default_consequence_modifier",
                ),
                "description": "AI modifiers for automatic risk scoring (0.1-2.0)",
            },
        ),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def active_risks_display(self, obj):
        count = obj.active_risks_count
        if count > 0:
            color = "red" if obj.high_risks_count > 0 else "orange"
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>', color, count
            )
        return format_html('<span style="color: green;">0</span>')

    active_risks_display.short_description = "Active Risks"

    def high_risks_display(self, obj):
        count = obj.high_risks_count
        if count > 0:
            return format_html(
                '<span style="color: red; font-weight: bold; background: #ffebee; padding: 2px 6px; border-radius: 3px;">⚠️ {}</span>',
                count,
            )
        return format_html('<span style="color: green;">✓ 0</span>')

    high_risks_display.short_description = "High/Extreme"


class RiskControlInline(admin.TabularInline):
    """Inline for managing risk controls."""

    model = RiskControl
    extra = 1
    fields = [
        "title",
        "control_type",
        "effectiveness_rating",
        "responsible_person",
        "is_active",
    ]
    readonly_fields = ["control_number"]


@admin.register(RiskRegister)
class RiskRegisterAdmin(admin.ModelAdmin):
    """Admin interface for the intelligent risk register."""

    list_display = [
        "risk_number",
        "title_short",
        "category",
        "residual_risk_display",
        "control_effectiveness_display",
        "status_display",
        "review_status",
        "f2_integration_display",
    ]
    list_filter = [
        "residual_risk_rating",
        "status",
        "category",
        "f2_integration_enabled",
        "auto_review_enabled",
        "assessment_date",
    ]
    search_fields = ["risk_number", "title", "description"]
    readonly_fields = [
        "risk_number",
        "inherent_risk_rating",
        "residual_risk_rating",
        "control_effectiveness",
        "days_until_review",
        "is_overdue_review",
        "requires_immediate_action",
        "f2_maintenance_trigger",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Risk Identification",
            {"fields": ("risk_number", "title", "description", "category", "operator")},
        ),
        ("Risk Assessment Team", {"fields": ("identified_by", "assessed_by")}),
        (
            "Inherent Risk (Before Controls)",
            {
                "fields": (
                    ("inherent_likelihood", "inherent_consequence"),
                    "inherent_risk_rating",
                ),
                "description": "Risk level without any controls in place",
            },
        ),
        (
            "Residual Risk (After Controls)",
            {
                "fields": (
                    ("residual_likelihood", "residual_consequence"),
                    "residual_risk_rating",
                    "control_effectiveness",
                ),
                "description": "Risk level with current controls in place",
            },
        ),
        (
            "Risk Management",
            {
                "fields": (
                    "status",
                    ("assessment_date", "review_date"),
                    ("days_until_review", "is_overdue_review"),
                    "requires_immediate_action",
                )
            },
        ),
        (
            "AI Intelligence Features",
            {
                "fields": (
                    "auto_review_enabled",
                    "f2_integration_enabled",
                    "f2_maintenance_trigger",
                ),
                "classes": ("collapse",),
                "description": "Revolutionary AI features that automate safety management",
            },
        ),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [RiskControlInline]

    actions = [
        "trigger_f2_maintenance_action",
        "schedule_review_action",
        "activate_f2_integration_action",
    ]

    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title

    title_short.short_description = "Title"

    def residual_risk_display(self, obj):
        colors = {
            "extreme": "#d32f2f",  # Red
            "high": "#f57c00",  # Orange
            "medium": "#fbc02d",  # Yellow
            "low": "#388e3c",  # Green
            "negligible": "#1976d2",  # Blue
        }
        color = colors.get(obj.residual_risk_rating, "#666666")

        return format_html(
            '<span style="color: {}; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_residual_risk_rating_display(),
        )

    residual_risk_display.short_description = "Risk Level"

    def control_effectiveness_display(self, obj):
        effectiveness = obj.control_effectiveness
        if effectiveness >= 80:
            color = "green"
            icon = "✓"
        elif effectiveness >= 60:
            color = "orange"
            icon = "⚠"
        else:
            color = "red"
            icon = "⚠"

        return format_html(
            '<span style="color: {};">{} {}%</span>', color, icon, int(effectiveness)
        )

    control_effectiveness_display.short_description = "Control Effectiveness"

    def status_display(self, obj):
        colors = {
            "draft": "#666666",
            "open": "#d32f2f",  # Red - needs attention
            "monitoring": "#f57c00",  # Orange - being managed
            "closed": "#388e3c",  # Green - resolved
            "superseded": "#9e9e9e",  # Grey - replaced
        }
        color = colors.get(obj.status, "#666666")

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def review_status(self, obj):
        if obj.is_overdue_review:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>'
            )
        elif obj.days_until_review <= 30:
            return format_html(
                '<span style="color: orange;">📅 {} days</span>', obj.days_until_review
            )
        else:
            return format_html(
                '<span style="color: green;">✓ {} days</span>', obj.days_until_review
            )

    review_status.short_description = "Review Due"

    def f2_integration_display(self, obj):
        if obj.f2_integration_enabled:
            if obj.f2_maintenance_trigger:
                return format_html(
                    '<span style="color: red; font-weight: bold;">🔧 ACTIVE TRIGGER</span>'
                )
            else:
                return format_html('<span style="color: green;">✓ Enabled</span>')
        return format_html('<span style="color: #666;">Disabled</span>')

    f2_integration_display.short_description = "F2 Integration"

    def trigger_f2_maintenance_action(self, request, queryset):
        """Admin action to manually trigger F2 maintenance for selected risks."""
        count = 0
        for risk in queryset.filter(f2_integration_enabled=True):
            if risk.f2_maintenance_trigger:
                maintenance_items = risk.trigger_f2_maintenance()
                if maintenance_items:
                    count += len(maintenance_items)

        if count > 0:
            self.message_user(
                request,
                f"Successfully created {count} F2 maintenance requirements from high risks.",
            )
        else:
            self.message_user(
                request,
                "No high/extreme risks with F2 integration found.",
                level="warning",
            )

    trigger_f2_maintenance_action.short_description = (
        "Trigger F2 maintenance for high risks"
    )

    def schedule_review_action(self, request, queryset):
        """Admin action to reschedule risk reviews."""
        for risk in queryset:
            risk.schedule_next_review()
            risk.save()

        self.message_user(
            request,
            f"Rescheduled reviews for {queryset.count()} risks based on their risk ratings.",
        )

    schedule_review_action.short_description = "Reschedule reviews based on risk rating"

    def activate_f2_integration_action(self, request, queryset):
        """Admin action to enable F2 integration for aircraft-related risks."""
        aircraft_categories = ["AO", "AC", "MAINT"]
        eligible_risks = queryset.filter(
            category__code__in=aircraft_categories,
            residual_risk_rating__in=["high", "extreme"],
        )

        count = eligible_risks.update(f2_integration_enabled=True)
        self.message_user(
            request, f"Enabled F2 integration for {count} eligible aircraft risks."
        )

    activate_f2_integration_action.short_description = (
        "Enable F2 integration for aircraft risks"
    )


@admin.register(RiskControl)
class RiskControlAdmin(admin.ModelAdmin):
    """Admin interface for risk controls."""

    list_display = [
        "control_number",
        "title",
        "risk_number_link",
        "control_type",
        "effectiveness_rating",
        "verification_status",
        "is_active",
    ]
    list_filter = [
        "control_type",
        "effectiveness_rating",
        "is_active",
        "implementation_date",
    ]
    search_fields = ["control_number", "title", "risk__risk_number", "risk__title"]
    readonly_fields = [
        "control_number",
        "days_until_verification",
        "is_verification_overdue",
    ]

    fieldsets = (
        (
            "Control Identification",
            {"fields": ("control_number", "title", "description", "risk")},
        ),
        (
            "Control Details",
            {"fields": ("control_type", "effectiveness_rating", "linked_sop")},
        ),
        (
            "Implementation",
            {"fields": ("responsible_person", "implementation_date", "is_active")},
        ),
        (
            "Verification Tracking",
            {
                "fields": (
                    ("verification_date", "next_verification_date"),
                    ("days_until_verification", "is_verification_overdue"),
                )
            },
        ),
    )

    def risk_number_link(self, obj):
        url = reverse("admin:sms_riskregister_change", args=[obj.risk.id])
        return format_html(
            '<a href="{}" style="color: #1976d2; text-decoration: none;">{}</a>',
            url,
            obj.risk.risk_number,
        )

    risk_number_link.short_description = "Risk"

    def verification_status(self, obj):
        if obj.is_verification_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>'
            )
        elif obj.days_until_verification <= 30:
            return format_html(
                '<span style="color: orange;">📅 {} days</span>',
                obj.days_until_verification,
            )
        else:
            return format_html(
                '<span style="color: green;">✓ {} days</span>',
                obj.days_until_verification,
            )

    verification_status.short_description = "Verification Due"


class SOPAcknowledgmentInline(admin.TabularInline):
    """Inline for SOP acknowledgments."""

    model = SOPAcknowledgment
    extra = 0
    readonly_fields = ["acknowledged_date", "version_acknowledged", "ip_address"]
    fields = [
        "staff_member",
        "acknowledged_date",
        "version_acknowledged",
        "is_current",
        "training_completed",
    ]


@admin.register(StandardOperatingProcedure)
class StandardOperatingProcedureAdmin(admin.ModelAdmin):
    """Admin interface for SOPs."""

    list_display = [
        "sop_number",
        "title_short",
        "sop_type",
        "version_number",
        "status_display",
        "acknowledgment_status",
        "review_status",
        "requires_training",
    ]
    list_filter = [
        "sop_type",
        "status",
        "requires_training",
        "auto_acknowledgment_tracking",
        "created_date",
    ]
    search_fields = ["sop_number", "title", "purpose"]
    readonly_fields = [
        "sop_number",
        "acknowledgment_percentage",
        "days_until_review",
        "is_review_due",
        "updated_at",
    ]

    fieldsets = (
        (
            "SOP Identification",
            {"fields": ("sop_number", "title", "sop_type", "operator")},
        ),
        ("Content", {"fields": ("purpose", "procedure_content")}),
        ("Version Control", {"fields": ("version_number", "status")}),
        ("Authoring & Approval", {"fields": ("author", "reviewer", "approver")}),
        (
            "Important Dates",
            {
                "fields": (
                    ("created_date", "approved_date", "effective_date"),
                    ("review_date", "days_until_review", "is_review_due"),
                )
            },
        ),
        (
            "AI Intelligence",
            {
                "fields": (
                    "auto_acknowledgment_tracking",
                    "acknowledgment_percentage",
                    "requires_training",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [SOPAcknowledgmentInline]

    actions = ["create_new_version_action", "approve_sop_action"]

    def title_short(self, obj):
        return obj.title[:40] + "..." if len(obj.title) > 40 else obj.title

    title_short.short_description = "Title"

    def status_display(self, obj):
        colors = {
            "draft": "#666666",
            "review": "#f57c00",  # Orange
            "approved": "#388e3c",  # Green
            "superseded": "#9e9e9e",  # Grey
            "archived": "#9e9e9e",  # Grey
        }
        color = colors.get(obj.status, "#666666")

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def acknowledgment_status(self, obj):
        if not obj.auto_acknowledgment_tracking:
            return format_html('<span style="color: #666;">Not Tracked</span>')

        percentage = obj.acknowledgment_percentage
        if percentage >= 100:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ 100%</span>'
            )
        elif percentage >= 80:
            return format_html(
                '<span style="color: orange;">📊 {}%</span>', int(percentage)
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {}%</span>',
                int(percentage),
            )

    acknowledgment_status.short_description = "Staff Acknowledgment"

    def review_status(self, obj):
        if obj.is_review_due:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ DUE NOW</span>'
            )
        elif obj.days_until_review <= 30:
            return format_html(
                '<span style="color: orange;">📅 {} days</span>', obj.days_until_review
            )
        else:
            return format_html(
                '<span style="color: green;">✓ {} days</span>', obj.days_until_review
            )

    review_status.short_description = "Review Due"

    def create_new_version_action(self, request, queryset):
        """Admin action to create new versions of selected SOPs."""
        count = 0
        for sop in queryset.filter(status="approved"):
            sop.create_new_version(request.user)
            count += 1

        if count > 0:
            self.message_user(
                request, f"Created {count} new SOP versions ready for editing."
            )
        else:
            self.message_user(
                request,
                "Only approved SOPs can have new versions created.",
                level="warning",
            )

    create_new_version_action.short_description = "Create new versions of approved SOPs"

    def approve_sop_action(self, request, queryset):
        """Admin action to approve SOPs that are under review."""
        count = queryset.filter(status="review").update(
            status="approved", approved_date=timezone.now().date()
        )

        if count > 0:
            self.message_user(request, f"Approved {count} SOPs.")
        else:
            self.message_user(
                request, "Only SOPs under review can be approved.", level="warning"
            )

    approve_sop_action.short_description = "Approve SOPs under review"


@admin.register(SOPAcknowledgment)
class SOPAcknowledgmentAdmin(admin.ModelAdmin):
    """Admin interface for SOP acknowledgments."""

    list_display = [
        "sop_number_link",
        "staff_member",
        "version_acknowledged",
        "acknowledged_date",
        "is_current",
        "training_status",
    ]
    list_filter = [
        "is_current",
        "training_completed",
        "acknowledged_date",
        "sop__sop_type",
    ]
    search_fields = [
        "sop__sop_number",
        "sop__title",
        "staff_member__first_name",
        "staff_member__last_name",
        "staff_member__email",
    ]
    readonly_fields = ["acknowledged_date", "ip_address"]

    def sop_number_link(self, obj):
        url = reverse("admin:sms_standardoperatingprocedure_change", args=[obj.sop.id])
        return format_html(
            '<a href="{}" style="color: #1976d2; text-decoration: none;">{}</a>',
            url,
            obj.sop.sop_number,
        )

    sop_number_link.short_description = "SOP"

    def training_status(self, obj):
        if not obj.sop.requires_training:
            return format_html('<span style="color: #666;">N/A</span>')

        if obj.training_completed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Completed</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ Required</span>'
            )

    training_status.short_description = "Training"


# Customize admin site header and title for SMS
admin.site.site_header = "RPAS Safety Management System"
admin.site.site_title = "SMS Admin"
admin.site.index_title = "Intelligent Safety Management Dashboard"


# =============================================================================
# SMS JSA ADMIN INTERFACES
# =============================================================================


class JSAHazardInline(admin.TabularInline):
    """Inline for hazards within job steps."""

    model = JSAHazard
    extra = 1
    fields = [
        "hazard_description",
        "hazard_type",
        "potential_consequences",
        "risk_level",
        "control_measures",
        "linked_risk",
        "auto_risk_created",
    ]
    readonly_fields = ["linked_risk", "auto_risk_created"]

    def get_queryset(self, request):
        """Optimize queryset for better performance."""
        return super().get_queryset(request).select_related("linked_risk")


class JSAJobStepInline(admin.TabularInline):
    """Inline for job steps within JSA."""

    model = JSAJobStep
    extra = 1
    fields = [
        "step_number",
        "step_description",
        "estimated_duration",
        "is_critical_step",
        "hazard_count_display",
    ]
    readonly_fields = ["hazard_count_display"]

    def hazard_count_display(self, obj):
        """Display hazard count for this step."""
        if obj.pk:
            count = obj.hazard_count
            high_risk_count = obj.high_risk_hazard_count
            if high_risk_count > 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">{} hazards ({} high risk)</span>',
                    count,
                    high_risk_count,
                )
            return f"{count} hazards"
        return "0 hazards"

    hazard_count_display.short_description = "Hazards"


@admin.register(JobSafetyAnalysis)
class JobSafetyAnalysisAdmin(admin.ModelAdmin):
    """Revolutionary JSA admin with intelligent hazard management."""

    list_display = [
        "jsa_number",
        "title",
        "jsa_type",
        "status",
        "analyst_name",
        "analysis_date",
        "review_status_display",
        "hazard_summary_display",
        "ai_integration_display",
    ]

    list_filter = [
        "jsa_type",
        "status",
        "analysis_date",
        "review_date",
        "auto_risk_linking",
        "operator",
    ]

    search_fields = [
        "jsa_number",
        "title",
        "job_description",
        "analyst__email",
        "operator__company_name",
    ]

    readonly_fields = [
        "jsa_number",
        "total_hazards",
        "high_risk_hazards",
        "is_current",
        "is_review_due",
        "days_until_review",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "JSA Identification",
            {"fields": ("jsa_number", "title", "jsa_type", "operator")},
        ),
        (
            "Job Details",
            {
                "fields": (
                    "job_description",
                    "location_description",
                    "personnel_required",
                    "equipment_required",
                )
            },
        ),
        (
            "Analysis & Approval",
            {
                "fields": (
                    ("analyst", "analysis_date"),
                    ("reviewer", "approved_date"),
                    ("approver", "status"),
                )
            },
        ),
        (
            "Review Management",
            {"fields": ("review_date", "is_review_due", "days_until_review")},
        ),
        (
            "AI Intelligence",
            {
                "fields": ("auto_risk_linking", "total_hazards", "high_risk_hazards"),
                "classes": ("collapse",),
            },
        ),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [JSAJobStepInline]

    actions = ["approve_jsas", "mark_for_review", "update_risk_linking"]

    def get_queryset(self, request):
        """Optimize queryset for better performance."""
        return (
            super()
            .get_queryset(request)
            .select_related("analyst", "reviewer", "approver", "operator")
            .prefetch_related("job_steps__hazards")
        )

    def analyst_name(self, obj):
        """Display analyst name."""
        return obj.analyst.get_full_name() or obj.analyst.email

    analyst_name.short_description = "Analyst"

    def review_status_display(self, obj):
        """Display review status with visual indicators."""
        if obj.is_review_due:
            return format_html(
                '<span style="color: red; font-weight: bold;">OVERDUE</span>'
            )
        elif obj.days_until_review <= 30:
            return format_html(
                '<span style="color: orange;">Due in {} days</span>',
                obj.days_until_review,
            )
        else:
            return format_html(
                '<span style="color: green;">Due in {} days</span>',
                obj.days_until_review,
            )

    review_status_display.short_description = "Review Status"

    def hazard_summary_display(self, obj):
        """Display hazard summary with risk indicators."""
        total = obj.total_hazards
        high_risk = obj.high_risk_hazards

        if high_risk > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">{} total ({} high risk)</span>',
                total,
                high_risk,
            )
        elif total > 0:
            return format_html(
                '<span style="color: green;">{} hazards identified</span>', total
            )
        return format_html('<span style="color: gray;">No hazards</span>')

    hazard_summary_display.short_description = "Hazards"

    def ai_integration_display(self, obj):
        """Display AI integration status."""
        if obj.auto_risk_linking:
            linked_count = obj.job_steps.filter(
                hazards__linked_risk__isnull=False
            ).count()
            if linked_count > 0:
                return format_html(
                    '<span style="color: green;">✓ Active ({} risks created)</span>',
                    linked_count,
                )
            return format_html('<span style="color: blue;">✓ Enabled</span>')
        return format_html('<span style="color: gray;">Disabled</span>')

    ai_integration_display.short_description = "AI Integration"

    @admin.action(description="Approve selected JSAs")
    def approve_jsas(self, request, queryset):
        """Action to approve selected JSAs."""
        count = 0
        for jsa in queryset.filter(status="review"):
            jsa.status = "approved"
            jsa.approved_date = date.today()
            jsa.save()
            count += 1

        self.message_user(request, f"Approved {count} JSAs.", messages.SUCCESS)

    @admin.action(description="Mark selected JSAs for review")
    def mark_for_review(self, request, queryset):
        """Action to mark JSAs for review."""
        count = queryset.filter(status="approved").update(status="review")

        self.message_user(request, f"Marked {count} JSAs for review.", messages.INFO)

    @admin.action(description="Update risk register linking for selected JSAs")
    def update_risk_linking(self, request, queryset):
        """Action to update risk register linking."""
        risk_count = 0

        for jsa in queryset.filter(auto_risk_linking=True):
            for step in jsa.job_steps.all():
                for hazard in step.hazards.filter(
                    risk_level__in=["high", "extreme"], linked_risk__isnull=True
                ):
                    risk_entry = hazard.create_risk_register_entry()
                    if risk_entry:
                        risk_count += 1

        self.message_user(
            request,
            f"Created {risk_count} risk register entries from JSA hazards.",
            messages.SUCCESS,
        )


@admin.register(JSAJobStep)
class JSAJobStepAdmin(admin.ModelAdmin):
    """Admin interface for JSA job steps."""

    list_display = [
        "jsa_number_display",
        "step_number",
        "step_description_short",
        "is_critical_step",
        "hazard_count_display",
        "high_risk_display",
    ]

    list_filter = ["is_critical_step", "jsa__jsa_type", "jsa__status"]

    search_fields = ["jsa__jsa_number", "jsa__title", "step_description"]

    inlines = [JSAHazardInline]

    def get_queryset(self, request):
        """Optimize queryset for better performance."""
        return (
            super()
            .get_queryset(request)
            .select_related("jsa")
            .prefetch_related("hazards")
        )

    def jsa_number_display(self, obj):
        """Display JSA number as link."""
        return obj.jsa.jsa_number

    jsa_number_display.short_description = "JSA Number"

    def step_description_short(self, obj):
        """Display shortened step description."""
        return (
            obj.step_description[:100] + "..."
            if len(obj.step_description) > 100
            else obj.step_description
        )

    step_description_short.short_description = "Step Description"

    def hazard_count_display(self, obj):
        """Display hazard count."""
        return obj.hazard_count

    hazard_count_display.short_description = "Hazards"

    def high_risk_display(self, obj):
        """Display high risk hazard indicator."""
        count = obj.high_risk_hazard_count
        if count > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">{} high risk</span>',
                count,
            )
        return "-"

    high_risk_display.short_description = "High Risk"


@admin.register(JSAHazard)
class JSAHazardAdmin(admin.ModelAdmin):
    """Admin interface for JSA hazards with AI risk integration."""

    list_display = [
        "jsa_number_display",
        "step_number_display",
        "hazard_type",
        "risk_level_display",
        "risk_integration_display",
        "control_status",
    ]

    list_filter = [
        "hazard_type",
        "risk_level",
        "auto_risk_created",
        "job_step__jsa__jsa_type",
    ]

    search_fields = [
        "hazard_description",
        "potential_consequences",
        "control_measures",
        "job_step__jsa__jsa_number",
    ]

    readonly_fields = ["auto_risk_created", "requires_risk_register_entry"]

    fieldsets = (
        (
            "Hazard Identification",
            {
                "fields": (
                    ("job_step", "hazard_type"),
                    "hazard_description",
                    "potential_consequences",
                )
            },
        ),
        ("Risk Assessment", {"fields": ("risk_level", "control_measures")}),
        (
            "AI Risk Integration",
            {
                "fields": (
                    "linked_risk",
                    "auto_risk_created",
                    "requires_risk_register_entry",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["create_risk_entries", "update_control_measures"]

    def get_queryset(self, request):
        """Optimize queryset for better performance."""
        return (
            super().get_queryset(request).select_related("job_step__jsa", "linked_risk")
        )

    def jsa_number_display(self, obj):
        """Display JSA number."""
        return obj.job_step.jsa.jsa_number

    jsa_number_display.short_description = "JSA Number"

    def step_number_display(self, obj):
        """Display step number."""
        return f"Step {obj.job_step.step_number}"

    step_number_display.short_description = "Step"

    def risk_level_display(self, obj):
        """Display risk level with color coding."""
        colors = {
            "extreme": "purple",
            "high": "red",
            "medium": "orange",
            "low": "green",
            "negligible": "gray",
        }

        color = colors.get(obj.risk_level, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_risk_level_display(),
        )

    risk_level_display.short_description = "Risk Level"

    def risk_integration_display(self, obj):
        """Display risk integration status."""
        if obj.linked_risk:
            if obj.auto_risk_created:
                return format_html('<span style="color: green;">✓ Auto-created</span>')
            else:
                return format_html(
                    '<span style="color: blue;">✓ Manually linked</span>'
                )
        elif obj.requires_risk_register_entry:
            return format_html(
                '<span style="color: orange;">⚠ Requires risk entry</span>'
            )
        return format_html('<span style="color: gray;">No risk entry needed</span>')

    risk_integration_display.short_description = "Risk Integration"

    def control_status(self, obj):
        """Display control measure status."""
        if obj.control_measures:
            length = len(obj.control_measures)
            if length > 200:
                return format_html(
                    '<span style="color: green;">✓ Detailed ({} chars)</span>', length
                )
            else:
                return format_html(
                    '<span style="color: orange;">Basic ({} chars)</span>', length
                )
        return format_html('<span style="color: red;">⚠ Missing</span>')

    control_status.short_description = "Controls"

    @admin.action(description="Create risk register entries for selected hazards")
    def create_risk_entries(self, request, queryset):
        """Action to create risk register entries for high/extreme hazards."""
        count = 0

        for hazard in queryset.filter(
            risk_level__in=["high", "extreme"], linked_risk__isnull=True
        ):
            risk_entry = hazard.create_risk_register_entry()
            if risk_entry:
                count += 1

        self.message_user(
            request, f"Created {count} risk register entries.", messages.SUCCESS
        )

    @admin.action(description="Update control measures for selected hazards")
    def update_control_measures(self, request, queryset):
        """Action to mark hazards requiring control measure updates."""
        count = queryset.filter(control_measures="").count()

        self.message_user(
            request, f"{count} hazards require control measure updates.", messages.INFO
        )


# =============================================================================
# SMS INCIDENT MANAGEMENT ADMIN INTERFACES
# =============================================================================


@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    """Admin interface for incident categories."""

    list_display = [
        "code",
        "name",
        "default_severity",
        "casa_reportable",
        "auto_investigation_required",
        "incident_count_display",
        "is_active",
    ]

    list_filter = [
        "default_severity",
        "casa_reportable",
        "auto_investigation_required",
        "is_active",
    ]

    search_fields = ["code", "name", "description"]

    fieldsets = (
        ("Category Details", {"fields": ("code", "name", "description", "is_active")}),
        ("CASA Requirements", {"fields": ("casa_reportable", "reporting_timeframe")}),
        (
            "Risk Assessment",
            {"fields": ("default_severity", "auto_investigation_required")},
        ),
    )

    def incident_count_display(self, obj):
        """Display incident count for this category."""
        total = obj.incident_count
        recent = obj.recent_incident_count

        if recent > 0:
            return format_html("<span>{} total ({} recent)</span>", total, recent)
        return f"{total} total"

    incident_count_display.short_description = "Incidents"


class CorrectiveActionInline(admin.TabularInline):
    """Inline for corrective actions."""

    model = CorrectiveAction
    extra = 0
    fields = [
        "action_number",
        "title",
        "action_type",
        "priority",
        "responsible_person",
        "due_date",
        "status",
    ]
    readonly_fields = ["action_number"]


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """Revolutionary incident management with AI pattern recognition."""

    list_display = [
        "incident_number",
        "title",
        "category",
        "severity_display",
        "incident_date",
        "status_display",
        "investigation_status",
        "casa_status_display",
        "corrective_actions_display",
    ]

    list_filter = [
        "category",
        "severity_level",
        "status",
        "casa_reportable",
        "casa_reported",
        "investigation_required",
        "operator",
    ]

    search_fields = [
        "incident_number",
        "title",
        "description",
        "location",
        "reported_by__email",
    ]

    readonly_fields = [
        "incident_number",
        "days_since_incident",
        "corrective_actions_count",
        "open_corrective_actions_count",
        "auto_risk_created",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Incident Identification",
            {"fields": ("incident_number", "title", "category", "operator")},
        ),
        (
            "Incident Details",
            {
                "fields": (
                    "incident_date",
                    "location",
                    "description",
                    "severity_level",
                    "actual_consequences",
                    "potential_consequences",
                )
            },
        ),
        (
            "Personnel & Equipment",
            {"fields": ("reported_by", "involved_personnel", "aircraft_involved")},
        ),
        (
            "Investigation Management",
            {
                "fields": (
                    "status",
                    "investigation_required",
                    "investigator",
                    "investigation_deadline",
                    "closed_date",
                )
            },
        ),
        (
            "CASA Reporting",
            {
                "fields": (
                    "casa_reportable",
                    "casa_reported",
                    "casa_report_date",
                    "casa_reference",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "AI Intelligence",
            {
                "fields": ("linked_risk", "auto_risk_created", "similar_incidents"),
                "classes": ("collapse",),
            },
        ),
        (
            "Status Information",
            {
                "fields": (
                    "days_since_incident",
                    "corrective_actions_count",
                    "open_corrective_actions_count",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [CorrectiveActionInline]

    actions = [
        "mark_casa_reported",
        "assign_investigator",
        "close_investigations",
        "create_corrective_actions",
    ]

    def get_queryset(self, request):
        """Optimize queryset for better performance."""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "category",
                "operator",
                "reported_by",
                "investigator",
                "aircraft_involved",
                "linked_risk",
            )
            .prefetch_related("involved_personnel", "corrective_actions")
        )

    def severity_display(self, obj):
        """Display severity with color coding."""
        colors = {
            "minor": "green",
            "serious": "orange",
            "major": "red",
            "fatal": "purple",
        }

        color = colors.get(obj.severity_level, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_level_display(),
        )

    severity_display.short_description = "Severity"

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            "reported": "#666666",
            "under_review": "#f57c00",
            "investigating": "#2196f3",
            "corrective_actions": "#9c27b0",
            "closed": "#388e3c",
        }

        color = colors.get(obj.status, "#666666")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def investigation_status(self, obj):
        """Display investigation status."""
        if not obj.investigation_required:
            return format_html('<span style="color: gray;">Not required</span>')

        if obj.status == "closed":
            return format_html('<span style="color: green;">✓ Complete</span>')

        if obj.is_investigation_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ OVERDUE</span>'
            )

        if obj.investigator:
            return format_html('<span style="color: blue;">📋 Assigned</span>')

        return format_html('<span style="color: orange;">⏳ Pending</span>')

    investigation_status.short_description = "Investigation"

    def casa_status_display(self, obj):
        """Display CASA reporting status."""
        if not obj.casa_reportable:
            return format_html('<span style="color: gray;">Not required</span>')

        if obj.casa_reported:
            return format_html('<span style="color: green;">✓ Reported</span>')

        return format_html(
            '<span style="color: red; font-weight: bold;">⚠️ REQUIRED</span>'
        )

    casa_status_display.short_description = "CASA Status"

    def corrective_actions_display(self, obj):
        """Display corrective actions status."""
        total = obj.corrective_actions_count
        open_count = obj.open_corrective_actions_count

        if total == 0:
            return format_html('<span style="color: gray;">None</span>')

        if open_count == 0:
            return format_html(
                '<span style="color: green;">✓ {} complete</span>', total
            )

        return format_html(
            '<span style="color: orange;">{} total ({} open)</span>', total, open_count
        )

    corrective_actions_display.short_description = "Actions"

    @admin.action(description="Mark selected incidents as reported to CASA")
    def mark_casa_reported(self, request, queryset):
        """Action to mark incidents as reported to CASA."""
        from django.utils import timezone

        count = 0
        for incident in queryset.filter(casa_reportable=True, casa_reported=False):
            incident.casa_reported = True
            incident.casa_report_date = timezone.now()
            incident.save()
            count += 1

        self.message_user(
            request, f"Marked {count} incidents as reported to CASA.", messages.SUCCESS
        )

    @admin.action(description="Assign investigator to selected incidents")
    def assign_investigator(self, request, queryset):
        """Action to assign investigator to incidents requiring investigation."""
        count = queryset.filter(
            investigation_required=True, investigator__isnull=True
        ).count()

        self.message_user(
            request,
            f"{count} incidents require investigator assignment.",
            messages.INFO,
        )

    @admin.action(description="Close selected incident investigations")
    def close_investigations(self, request, queryset):
        """Action to close completed investigations."""
        from django.utils import timezone

        count = 0
        for incident in queryset.filter(
            status="corrective_actions", open_corrective_actions_count=0
        ):
            incident.status = "closed"
            incident.closed_date = timezone.now()
            incident.save()
            count += 1

        self.message_user(
            request, f"Closed {count} incident investigations.", messages.SUCCESS
        )


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    """Admin interface for corrective action tracking."""

    list_display = [
        "action_number",
        "title",
        "source_display",
        "action_type",
        "priority_display",
        "responsible_person_display",
        "due_status",
        "status_display",
        "progress_display",
    ]

    list_filter = [
        "action_type",
        "priority",
        "status",
        "operator",
        "assigned_by",
        "responsible_person",
    ]

    search_fields = [
        "action_number",
        "title",
        "description",
        "responsible_person__email",
        "assigned_by__email",
    ]

    readonly_fields = [
        "action_number",
        "is_overdue",
        "days_until_due",
        "source_description",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Action Identification",
            {"fields": ("action_number", "title", "description", "action_type")},
        ),
        (
            "Source Information",
            {"fields": ("source_description", "incident", "risk", "jsa", "operator")},
        ),
        (
            "Assignment & Priority",
            {"fields": ("priority", "assigned_by", "responsible_person", "due_date")},
        ),
        (
            "Progress Tracking",
            {"fields": ("status", "progress_notes", "completed_date")},
        ),
        (
            "Verification",
            {
                "fields": ("verified_by", "verification_date", "verification_notes"),
                "classes": ("collapse",),
            },
        ),
        (
            "Status Information",
            {
                "fields": ("is_overdue", "days_until_due", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["mark_completed", "mark_verified", "extend_due_date"]

    def get_queryset(self, request):
        """Optimize queryset for better performance."""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "operator",
                "assigned_by",
                "responsible_person",
                "verified_by",
                "incident",
                "risk",
                "jsa",
            )
        )

    def source_display(self, obj):
        """Display action source."""
        return obj.source_description

    source_display.short_description = "Source"

    def priority_display(self, obj):
        """Display priority with color coding."""
        colors = {
            "low": "green",
            "medium": "orange",
            "high": "red",
            "critical": "purple",
        }

        color = colors.get(obj.priority, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display(),
        )

    priority_display.short_description = "Priority"

    def responsible_person_display(self, obj):
        """Display responsible person."""
        return obj.responsible_person.get_full_name() or obj.responsible_person.email

    responsible_person_display.short_description = "Responsible"

    def due_status(self, obj):
        """Display due date status."""
        if obj.status in ["completed", "verified", "closed"]:
            return format_html('<span style="color: green;">✓ Done</span>')

        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {} days overdue</span>',
                abs(obj.days_until_due),
            )
        elif obj.days_until_due <= 7:
            return format_html(
                '<span style="color: orange;">⏰ {} days</span>', obj.days_until_due
            )
        else:
            return format_html(
                '<span style="color: green;">{} days</span>', obj.days_until_due
            )

    due_status.short_description = "Due"

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            "open": "#666666",
            "in_progress": "#2196f3",
            "completed": "#ff9800",
            "verified": "#4caf50",
            "closed": "#388e3c",
        }

        color = colors.get(obj.status, "#666666")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def progress_display(self, obj):
        """Display progress information."""
        if obj.progress_notes:
            length = len(obj.progress_notes)
            return format_html('<span style="color: blue;">📝 {} chars</span>', length)
        return format_html('<span style="color: gray;">No updates</span>')

    progress_display.short_description = "Progress"

    @admin.action(description="Mark selected actions as completed")
    def mark_completed(self, request, queryset):
        """Action to mark corrective actions as completed."""
        count = 0
        for action in queryset.filter(status__in=["open", "in_progress"]):
            action.status = "completed"
            action.completed_date = date.today()
            action.save()
            count += 1

        self.message_user(
            request, f"Marked {count} actions as completed.", messages.SUCCESS
        )

    @admin.action(description="Mark selected actions as verified")
    def mark_verified(self, request, queryset):
        """Action to mark corrective actions as verified."""
        count = 0
        for action in queryset.filter(status="completed"):
            action.status = "verified"
            action.verified_by = request.user
            action.verification_date = date.today()
            action.save()
            count += 1

        self.message_user(request, f"Verified {count} actions.", messages.SUCCESS)
