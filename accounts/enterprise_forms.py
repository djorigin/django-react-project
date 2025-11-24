"""
Enterprise Form Standards for RPAS Management System

Cotton Component Integration + Three-Color Compliance System
Design Once, Use Everywhere - Professional Aviation Operations Standard

This module establishes the standard form patterns for the entire application:
1. Cotton component integration for consistent UI
2. Three-color compliance validation (GREEN/YELLOW/RED)
3. Enterprise styling with HSL color system
4. HTMX integration for real-time interactions
5. Professional error handling and feedback

Usage throughout application:
- Import EnterpriseMixin for all forms
- Use create_enterprise_layout() for consistent layouts
- Apply get_compliance_styling() for field validation
- Leverage professional_error_display() for user feedback
"""

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit

from django import forms
from django.core.exceptions import ValidationError

from core.models import BaseProfile


class EnterpriseMixin:
    """
    Mixin for all enterprise forms with Cotton + Three-Color integration

    Provides:
    - Consistent enterprise styling
    - Three-color compliance validation
    - Cotton component integration
    - Professional error handling
    - HTMX real-time interactions
    """

    def get_enterprise_helper(self, form_action_url, htmx_target="#form-container"):
        """
        Standard Crispy Forms helper with enterprise styling and HTMX
        """
        helper = FormHelper()
        helper.form_method = "post"
        helper.form_class = "space-y-6"
        helper.attrs = {
            "hx-post": form_action_url,
            "hx-target": htmx_target,
            "hx-swap": "outerHTML",
            "hx-indicator": ".loading-spinner",
            "enctype": "multipart/form-data",
        }
        return helper

    def get_enterprise_field_classes(self, field_name, compliance_status="green"):
        """
        Return enterprise field styling based on compliance status

        Args:
            field_name: Name of the form field
            compliance_status: green, yellow, red for three-color system

        Returns:
            CSS classes string with compliance colors
        """
        base_classes = (
            "block w-full px-3 py-2 text-sm rounded-md transition-colors duration-200"
        )

        compliance_classes = {
            "green": "border-green-300 focus:border-green-500 focus:ring-green-200",
            "yellow": "border-yellow-300 focus:border-yellow-500 focus:ring-yellow-200 bg-yellow-50",
            "red": "border-red-300 focus:border-red-500 focus:ring-red-200 bg-red-50",
            "default": "border-enterprise-gray-300 focus:border-professional-blue focus:ring-professional-blue-light",
        }

        return f"{base_classes} {compliance_classes.get(compliance_status, compliance_classes['default'])}"

    def apply_enterprise_styling(self):
        """
        Apply enterprise styling to all form fields
        """
        for field_name, field in self.fields.items():
            # Get compliance status for this field if model has ComplianceMixin
            compliance_status = self.get_field_compliance_status(field_name)

            # Apply enterprise styling
            field_classes = self.get_enterprise_field_classes(
                field_name, compliance_status
            )

            if hasattr(field.widget, "attrs"):
                # Preserve existing attrs and add our styling
                existing_attrs = field.widget.attrs.copy()

                # Ensure ID attribute is set correctly
                if "id" not in existing_attrs:
                    existing_attrs["id"] = f"id_{field_name}"

                # Add autocomplete attributes for better UX
                autocomplete_mapping = {
                    "first_name": "given-name",
                    "last_name": "family-name",
                    "email": "email",
                    "phone": "tel",
                    "address_line_1": "address-line1",
                    "address_line_2": "address-line2",
                    "country": "country",
                    "postal_code_manual": "postal-code",
                    "date_of_birth": "bday",
                }

                if field_name in autocomplete_mapping:
                    existing_attrs["autocomplete"] = autocomplete_mapping[field_name]

                # Update with our enterprise styling
                existing_attrs.update(
                    {"class": field_classes, "data-compliance": compliance_status}
                )

                # Set the updated attrs
                field.widget.attrs = existing_attrs

                # Add HTMX compliance checking for supported fields
                if self.supports_real_time_compliance(field_name):
                    field.widget.attrs.update(
                        {
                            "hx-get": "/compliance/check/field/",
                            "hx-trigger": "blur, change",
                            "hx-target": f"#compliance-{field_name}",
                            "hx-swap": "outerHTML",
                            "hx-include": f'[name="{field_name}"]',
                        }
                    )

    def get_field_compliance_status(self, field_name):
        """
        Get compliance status for specific field
        Override in forms where compliance checking is needed
        """
        if hasattr(self.instance, "get_compliance_summary"):
            # If instance has ComplianceMixin, check field compliance
            try:
                compliance = self.instance.get_compliance_summary()
                # Field-specific compliance logic would go here
                return compliance.get("overall_status", "default")
            except Exception:
                pass
        return "default"

    def supports_real_time_compliance(self, field_name):
        """
        Determine if field supports real-time compliance checking
        Override in specific forms
        """
        # Critical fields that need real-time compliance
        critical_fields = ["arn_number", "tax_file_number", "date_of_birth"]
        return field_name in critical_fields


def create_enterprise_layout(*fields, **kwargs):
    """
    Factory function to create standard enterprise layouts

    Args:
        *fields: Field names to include
        **kwargs: Layout options (columns, card_title, etc.)

    Returns:
        Crispy Forms Layout with Cotton component integration
    """
    columns = kwargs.get("columns", 1)
    card_title = kwargs.get("card_title", None)

    # Create responsive grid based on column count
    if columns == 2:
        grid_class = "grid grid-cols-1 md:grid-cols-2 gap-4"
    elif columns == 3:
        grid_class = "grid grid-cols-1 md:grid-cols-3 gap-4"
    else:
        grid_class = "space-y-4"

    layout_fields = []

    # Add card wrapper if title provided (simplified approach)
    if card_title:
        layout_fields.append(
            HTML(
                f'<div class="mb-6 bg-white rounded-lg shadow-sm border border-enterprise-gray-200"><div class="px-6 py-4 border-b border-enterprise-gray-200"><h3 class="text-lg font-medium text-enterprise-black">{card_title}</h3></div><div class="px-6 py-6 space-y-4">'
            )
        )

    # Group fields based on column layout
    if columns > 1 and len(fields) > 1:
        layout_fields.append(
            Div(*[Field(field) for field in fields], css_class=grid_class)
        )
    else:
        for field in fields:
            layout_fields.append(Field(field))

    # Add compliance status indicators
    for field in fields:
        layout_fields.append(HTML(f'<div id="compliance-{field}" class="mt-1"></div>'))

    # Close card wrapper if used
    if card_title:
        layout_fields.append(HTML("</div></div>"))

    return Layout(*layout_fields)


def create_enterprise_submit_button(text="Save", variant="primary", **kwargs):
    """
    Create standardized enterprise submit button with Cotton styling

    Args:
        text: Button text
        variant: Button variant (primary, secondary, success, warning, danger)
        **kwargs: Additional button options

    Returns:
        HTML for Cotton button component
    """
    extra_classes = kwargs.get("extra_classes", "")
    loading_text = kwargs.get("loading_text", "Saving...")

    return HTML(
        f"""
        <div class="flex items-center justify-end space-x-3 pt-6 border-t border-enterprise-gray-200">
            <div class="loading-spinner htmx-indicator">
                <svg class="animate-spin h-5 w-5 text-professional-blue" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="ml-2 text-sm text-enterprise-secondary">{loading_text}</span>
            </div>
            {{% load cotton %}}
            <button type="submit"
                    class="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200
                           bg-professional-blue text-white hover:bg-professional-blue-dark
                           focus:outline-none focus:ring-2 focus:ring-professional-blue focus:ring-offset-2
                           disabled:opacity-50 disabled:cursor-not-allowed {extra_classes}">
                {text}
            </button>
        </div>
    """
    )


class EnterpriseProfileForm(EnterpriseMixin, forms.ModelForm):
    """
    Example implementation: Enterprise Profile Form with full integration

    Demonstrates the standard pattern for all application forms:
    1. Inherit from EnterpriseMixin
    2. Apply enterprise styling
    3. Use enterprise layouts
    4. Include compliance checking
    5. Professional error handling
    """

    class Meta:
        model = BaseProfile
        fields = [
            "phone",
            "date_of_birth",
            "tax_file_number",
            "arn_number",
            "bio",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Apply enterprise styling to all fields
        self.apply_enterprise_styling()

        # Set up Crispy Forms with enterprise helper
        self.helper = self.get_enterprise_helper("/profile/edit/")

        # Create enterprise layout with Cotton components
        self.helper.layout = Layout(
            create_enterprise_layout(
                "phone", "date_of_birth", columns=2, card_title="Contact Information"
            ),
            create_enterprise_layout(
                "tax_file_number",
                "arn_number",
                columns=2,
                card_title="CASA Compliance Information",
            ),
            create_enterprise_layout(
                "bio", "image", columns=1, card_title="Additional Information"
            ),
            create_enterprise_submit_button(
                "Update Profile", loading_text="Updating..."
            ),
        )

    def clean(self):
        """
        Enhanced validation with three-color compliance integration
        """
        cleaned_data = super().clean()

        # Profile type specific validation
        if self.instance and self.instance.profile_type:
            profile_type = self.instance.profile_type.code

            # Pilot-specific validations (RED compliance)
            if profile_type == "pilot":
                if not cleaned_data.get("arn_number"):
                    raise ValidationError(
                        {
                            "arn_number": "Aviation Reference Number is required for Pilot profiles."
                        }
                    )
                if not cleaned_data.get("date_of_birth"):
                    raise ValidationError(
                        {
                            "date_of_birth": "Date of birth is required for Pilot profiles."
                        }
                    )

            # Staff-specific validations (YELLOW compliance)
            if profile_type in ["staff", "pilot"]:
                if not cleaned_data.get("tax_file_number"):
                    raise ValidationError(
                        {
                            "tax_file_number": "Tax File Number is required for Staff and Pilot profiles."
                        }
                    )

        return cleaned_data

    def get_field_compliance_status(self, field_name):
        """
        Override to provide field-specific compliance status
        """
        if not self.instance or not self.instance.profile_type:
            return "default"

        profile_type = self.instance.profile_type.code

        # Critical compliance fields for aviation operations
        if field_name == "arn_number" and profile_type == "pilot":
            return "red" if not self.instance.arn_number else "green"

        if field_name == "tax_file_number" and profile_type in ["staff", "pilot"]:
            return "yellow" if not self.instance.tax_file_number else "green"

        if field_name == "date_of_birth" and profile_type in ["staff", "pilot"]:
            return "yellow" if not self.instance.date_of_birth else "green"

        return "default"


# USAGE EXAMPLE FOR OTHER APPS:
"""
# In rpas/forms.py (F2 Technical Log forms)
from accounts.enterprise_forms import EnterpriseMixin, create_enterprise_layout

class F2MaintenanceForm(EnterpriseMixin, forms.ModelForm):
    class Meta:
        model = F2MaintenanceEntry
        fields = ['aircraft', 'work_performed', 'next_inspection_hours']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_enterprise_styling()
        self.helper = self.get_enterprise_helper('/f2/maintenance/add/')
        self.helper.layout = create_enterprise_layout(
            'aircraft', 'work_performed', 'next_inspection_hours',
            columns=2,
            card_title="F2 Maintenance Entry"
        )

# In sms/forms.py (Safety Management forms)
class JSAForm(EnterpriseMixin, forms.ModelForm):
    # Same pattern - consistent across entire application
    pass
"""
