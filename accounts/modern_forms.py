"""
Modernized Profile Form using Enterprise Standards

This demonstrates the new standard for all forms in the application:
- Cotton component integration
- Three-color compliance system
- Enterprise HSL styling
- Professional error handling
- HTMX real-time interactions

This will replace the existing profile_forms.py gradually.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

from core.models import BaseProfile, City, Country, PostalCode, ProfileType, State

from .enterprise_forms import (
    EnterpriseMixin,
    create_enterprise_layout,
    create_enterprise_submit_button,
)


class ModernProfileForm(EnterpriseMixin, forms.ModelForm):
    """
    Modern enterprise profile form demonstrating our new standards

    Features:
    - Cotton component integration
    - Three-color compliance validation
    - Professional HTMX interactions
    - Enterprise styling throughout
    - Real-time compliance checking
    """

    # Geographical chained selection with enterprise styling
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(is_active=True).order_by("name"),
        empty_label="Select Country",
        required=False,
        help_text="Select your country for address validation",
    )

    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        empty_label="Select State/Province",
        required=False,
        help_text="State/Province will populate based on country selection",
    )

    city_direct = forms.ModelChoiceField(
        queryset=City.objects.none(),
        empty_label="Select City/Town",
        required=False,
        help_text="City/Town will populate based on state selection",
    )

    postal_code_select = forms.ModelChoiceField(
        queryset=PostalCode.objects.none(),
        empty_label="Select Postal Code (Optional)",
        required=False,
        help_text="Postal code selection (optional - you can also enter manually below)",
    )

    postal_code_manual = forms.CharField(
        max_length=20,
        required=False,
        help_text="Enter postal code manually if not available in selection above",
    )

    class Meta:
        model = BaseProfile
        fields = [
            "phone",
            "date_of_birth",
            "tax_file_number",
            "arn_number",
            "address_line_1",
            "address_line_2",
            "latitude",
            "longitude",
            "bio",
            "website",
            "image",
        ]

        # Professional help text for aviation compliance
        help_texts = {
            "tax_file_number": "Required for Staff and Pilot profiles (CASA compliance)",
            "arn_number": "Aviation Reference Number - Required for Pilot profiles",
            "date_of_birth": "Required for Staff and Pilot profiles (identity verification)",
            "image": "Professional photo required for Staff and Pilot profiles",
            "latitude": "Automatically populated from address - can be manually adjusted",
            "longitude": "Automatically populated from address - can be manually adjusted",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set up geographical chained selection data
        self._setup_geographical_data()

        # Apply enterprise styling with compliance integration
        self.apply_enterprise_styling()

        # Add HTMX geographical chaining
        self._setup_geographical_htmx()

        # Configure Crispy Forms with professional layout
        self.helper = self.get_enterprise_helper(
            reverse("accounts:profile_edit"), htmx_target="#profile-form-container"
        )

        # Professional layout using Cotton components
        self.helper.layout = self._create_professional_layout()

    def _setup_geographical_data(self):
        """Set up initial data for geographical chained selection"""
        if self.instance and self.instance.pk:
            # Populate existing geographical data
            if self.instance.city:
                country = self.instance.city.state.country
                state = self.instance.city.state
                self.fields["country"].initial = country
                self.fields["state"].queryset = State.objects.filter(country=country)
                self.fields["state"].initial = state
                self.fields["city_direct"].queryset = City.objects.filter(state=state)
                self.fields["city_direct"].initial = self.instance.city

                if self.instance.postal_code:
                    self.fields["postal_code_select"].queryset = (
                        PostalCode.objects.filter(city=self.instance.city)
                    )
                    self.fields["postal_code_select"].initial = (
                        self.instance.postal_code
                    )

        # Handle form submission data
        if self.is_bound and self.data:
            country_id = self.data.get("country")
            state_id = self.data.get("state")
            city_id = self.data.get("city_direct")

            if country_id:
                self.fields["state"].queryset = State.objects.filter(
                    country_id=country_id, is_active=True
                )

            if state_id:
                self.fields["city_direct"].queryset = City.objects.filter(
                    state_id=state_id, is_active=True
                )

            if city_id:
                self.fields["postal_code_select"].queryset = PostalCode.objects.filter(
                    city_id=city_id, is_active=True
                )

    def _setup_geographical_htmx(self):
        """Configure HTMX for geographical chained selection"""
        # Country -> State chaining
        self.fields["country"].widget.attrs.update(
            {
                "hx-get": reverse("accounts:load_states"),
                "hx-target": "#id_state",
                "hx-trigger": "change",
                "hx-swap": "outerHTML",
                "hx-include": '[name="country"]',
                "hx-indicator": "#geo-loading",
            }
        )

        # State -> City chaining
        self.fields["state"].widget.attrs.update(
            {
                "hx-get": reverse("accounts:load_cities"),
                "hx-target": "#id_city_direct",
                "hx-trigger": "change",
                "hx-swap": "outerHTML",
                "hx-include": '[name="state"]',
                "hx-indicator": "#geo-loading",
            }
        )

        # City -> Postal Code chaining
        self.fields["city_direct"].widget.attrs.update(
            {
                "hx-get": reverse("accounts:load_postal_codes"),
                "hx-target": "#id_postal_code_select",
                "hx-trigger": "change",
                "hx-swap": "outerHTML",
                "hx-include": '[name="city_direct"]',
                "hx-indicator": "#geo-loading",
            }
        )

    def _create_professional_layout(self):
        """Create professional layout using Cotton components and enterprise standards"""
        from crispy_forms.layout import HTML, Layout

        return Layout(
            # Profile Type Display (read-only information)
            HTML(
                """
                {% load cotton %}
                <div class="mb-6">
                    {% c card title="Profile Information" variant="info" %}
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-enterprise-secondary">Profile Type</p>
                                <p class="font-medium text-enterprise-black">{{ form.instance.profile_type.name|default:"Not Set" }}</p>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="text-sm text-enterprise-secondary">Compliance Status:</span>
                                <div id="profile-compliance-status">
                                    <!-- Compliance status will be populated via HTMX -->
                                </div>
                            </div>
                        </div>
                    {% endc %}
                </div>
            """
            ),
            # Contact Information Section
            create_enterprise_layout(
                "phone", columns=1, card_title="Contact Information"
            ),
            # CASA Compliance Section (critical fields)
            HTML(
                """
                {% load cotton %}
                <div class="mb-6">
                    {% c card title="CASA Compliance Information" variant="warning" %}
                        <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
                            <div class="flex">
                                <svg class="h-5 w-5 text-yellow-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 18.5c-.77.833.192 2.5 1.732 2.5z" />
                                </svg>
                                <div class="ml-3">
                                    <h3 class="text-sm font-medium text-yellow-800">Aviation Compliance Requirements</h3>
                                    <div class="mt-1 text-sm text-yellow-700">
                                        <p>Required fields vary by profile type. Pilot profiles require all fields for CASA compliance.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="space-y-4">
            """
            ),
            create_enterprise_layout("date_of_birth", "tax_file_number", columns=2),
            create_enterprise_layout("arn_number", columns=1),
            HTML("</div>{% endc %}</div>"),
            # Address Information Section
            HTML(
                """
                {% load cotton %}
                <div class="mb-6">
                    {% c card title="Address Information" variant="default" %}
                        <div class="space-y-4">
                            <div id="geo-loading" class="htmx-indicator">
                                <div class="flex items-center justify-center py-2">
                                    <svg class="animate-spin h-4 w-4 text-professional-blue mr-2" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    <span class="text-sm text-enterprise-secondary">Updating location options...</span>
                                </div>
                            </div>
            """
            ),
            create_enterprise_layout("country", "state", columns=2),
            create_enterprise_layout("city_direct", "postal_code_select", columns=2),
            create_enterprise_layout("postal_code_manual", columns=1),
            create_enterprise_layout("address_line_1", "address_line_2", columns=1),
            create_enterprise_layout("latitude", "longitude", columns=2),
            HTML("</div>{% endc %}</div>"),
            # Additional Information Section
            create_enterprise_layout(
                "bio",
                "website",
                "image",
                columns=1,
                card_title="Additional Information",
            ),
            # Professional submit button with loading state
            create_enterprise_submit_button(
                "Update Profile",
                loading_text="Updating profile...",
                extra_classes="w-full sm:w-auto",
            ),
            # Real-time compliance checking
            HTML(
                """
                <script>
                    // Trigger compliance check when critical fields change
                    document.addEventListener('htmx:afterSettle', function(event) {
                        if (event.target.id === 'profile-form-container') {
                            // Refresh compliance status after form updates
                            htmx.trigger('#profile-compliance-status', 'refresh');
                        }
                    });
                </script>
            """
            ),
        )

    def get_field_compliance_status(self, field_name):
        """
        Override to provide real-time compliance status for profile fields
        """
        if not self.instance or not self.instance.profile_type:
            return "default"

        profile_type = self.instance.profile_type.code

        # Critical compliance fields for aviation operations
        critical_fields = {
            "arn_number": {
                "required_for": ["pilot"],
                "field_value": self.instance.arn_number if self.instance else None,
            },
            "tax_file_number": {
                "required_for": ["staff", "pilot"],
                "field_value": self.instance.tax_file_number if self.instance else None,
            },
            "date_of_birth": {
                "required_for": ["staff", "pilot"],
                "field_value": self.instance.date_of_birth if self.instance else None,
            },
            "image": {
                "required_for": ["staff", "pilot"],
                "field_value": self.instance.image if self.instance else None,
            },
        }

        if field_name in critical_fields:
            field_info = critical_fields[field_name]
            if profile_type in field_info["required_for"]:
                # RED: Required but missing
                if not field_info["field_value"]:
                    return "red"
                # GREEN: Required and present
                else:
                    return "green"
            else:
                # YELLOW: Not required but recommended
                return "yellow" if not field_info["field_value"] else "green"

        return "default"

    def supports_real_time_compliance(self, field_name):
        """Enable real-time compliance for critical aviation fields"""
        critical_fields = ["arn_number", "tax_file_number", "date_of_birth", "image"]
        return field_name in critical_fields

    def clean(self):
        """
        Enhanced validation with three-color compliance system
        """
        cleaned_data = super().clean()

        if not self.instance or not self.instance.profile_type:
            return cleaned_data

        profile_type = self.instance.profile_type.code
        errors = {}

        # RED compliance - Critical requirements for operational profiles
        if profile_type == "pilot":
            if not cleaned_data.get("arn_number"):
                errors["arn_number"] = (
                    "Aviation Reference Number is required for Pilot profiles (CASA compliance)"
                )
            if not cleaned_data.get("date_of_birth"):
                errors["date_of_birth"] = (
                    "Date of birth is required for Pilot profiles (identity verification)"
                )

        # YELLOW compliance - Important but not critical
        if profile_type in ["staff", "pilot"]:
            if not cleaned_data.get("tax_file_number"):
                errors["tax_file_number"] = (
                    "Tax File Number is recommended for Staff and Pilot profiles"
                )

        if errors:
            raise ValidationError(errors)

        return cleaned_data

    def save(self, commit=True):
        """
        Enhanced save with geographical data processing
        """
        instance = super().save(commit=False)

        # Process geographical selection
        city = self.cleaned_data.get("city_direct")
        postal_code_select = self.cleaned_data.get("postal_code_select")
        postal_code_manual = self.cleaned_data.get("postal_code_manual")

        if city:
            instance.city = city

        # Handle postal code selection vs manual entry
        if postal_code_select:
            instance.postal_code = postal_code_select
        elif postal_code_manual:
            instance.postal_code_manual = postal_code_manual

        if commit:
            instance.save()

        return instance
