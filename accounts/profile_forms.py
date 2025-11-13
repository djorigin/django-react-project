"""
Profile forms for user profile management

Includes geographical chained selection and conditional field validation
based on profile types with HTMX integration for dynamic forms.
"""

from crispy_forms.bootstrap import InlineRadios

# Crispy Forms imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

from core.models import BaseProfile, City, Country, PostalCode, ProfileType, State


class ProfileEditForm(forms.ModelForm):
    """
    Main profile editing form with geographical chained selection

    Uses HTMX for dynamic Country -> State -> City -> PostalCode selection
    Includes conditional field requirements based on profile type
    """

    # Geographical fields for chained selection
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(is_active=True).order_by("name"),
        empty_label="Select Country",
        required=False,
    )

    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        empty_label="Select State/Province",
        required=False,
    )

    city_direct = forms.ModelChoiceField(
        queryset=City.objects.none(),
        empty_label="Select City/Town",
        required=False,
    )

    postal_code_select = forms.ModelChoiceField(
        queryset=PostalCode.objects.none(),
        empty_label="Select Postal Code (Optional)",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent"
            }
        ),
    )

    postal_code_manual = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                "placeholder": "Enter postal code",
            }
        ),
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
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Enter your phone number",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "tax_file_number": forms.TextInput(
                attrs={
                    "placeholder": "Enter your Tax File Number",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "arn_number": forms.TextInput(
                attrs={
                    "placeholder": "Enter your Aviation Reference Number",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "address_line_1": forms.TextInput(
                attrs={
                    "placeholder": "Street address",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "address_line_2": forms.TextInput(
                attrs={
                    "placeholder": "Apartment, suite, etc. (optional)",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "step": "0.0000001",
                    "placeholder": "Latitude (optional)",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "step": "0.0000001",
                    "placeholder": "Longitude (optional)",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us about yourself...",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "website": forms.URLInput(
                attrs={
                    "placeholder": "https://your-website.com",
                    "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-brand-purple file:text-white hover:file:bg-brand-purple-dark"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set up initial querysets for geographical fields
        if self.instance and self.instance.pk:
            # Populate existing data
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

            elif self.instance.postal_code:
                # If postal code exists but not direct city
                city = self.instance.postal_code.city
                state = city.state
                country = state.country
                self.fields["country"].initial = country
                self.fields["state"].queryset = State.objects.filter(country=country)
                self.fields["state"].initial = state
                self.fields["city_direct"].queryset = City.objects.filter(state=state)
                self.fields["city_direct"].initial = city
                self.fields["postal_code_select"].queryset = PostalCode.objects.filter(
                    city=city
                )
                self.fields["postal_code_select"].initial = self.instance.postal_code

        # Handle form submission - populate querysets based on submitted data
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

        # Configure Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "space-y-6"
        self.helper.attrs = {
            "hx-post": "/profile/edit/",
            "hx-target": "#profile-form-container",
            "hx-swap": "outerHTML",
            "enctype": "multipart/form-data",
        }

        # Add HTMX attributes to geographical fields
        self.fields["country"].widget.attrs.update(
            {
                "hx-get": "/load-states/",
                "hx-target": "#id_state",
                "hx-trigger": "change",
                "hx-swap": "outerHTML",
                "hx-include": '[name="country"]',
                "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
            }
        )

        self.fields["state"].widget.attrs.update(
            {
                "hx-get": "/load-cities/",
                "hx-target": "#id_city_direct",
                "hx-trigger": "change",
                "hx-swap": "outerHTML",
                "hx-include": '[name="state"]',
                "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
            }
        )

        self.fields["city_direct"].widget.attrs.update(
            {
                "hx-get": "/load-postal-codes/",
                "hx-target": "#id_postal_code_select",
                "hx-trigger": "change",
                "hx-swap": "outerHTML",
                "hx-include": '[name="city_direct"]',
                "class": "block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
            }
        )

        # Configure Crispy Forms layout
        self.helper.layout = Layout(
            Div(
                Div("first_name", css_class="col-md-6"),
                Div("last_name", css_class="col-md-6"),
                css_class="row",
            ),
            Div(
                Div("email", css_class="col-md-6"),
                Div("phone", css_class="col-md-6"),
                css_class="row",
            ),
            "date_of_birth",
            "bio",
            Div(
                Div("country", css_class="col-md-6"),
                Div("state", css_class="col-md-6"),
                css_class="row",
            ),
            Div(
                Div("city_direct", css_class="col-md-6"),
                Div("postal_code_select", css_class="col-md-6"),
                css_class="row",
            ),
            "postal_code_manual",
            "address_line_1",
            "address_line_2",
            Div(
                Div("latitude", css_class="col-md-6"),
                Div("longitude", css_class="col-md-6"),
                css_class="row",
            ),
            "tax_file_number",
            "arn_number",
            "image",
            Submit("submit", "Save Profile", css_class="btn btn-primary"),
        )

        # Set field requirements based on profile type
        profile_type = None
        if self.instance and self.instance.profile_type:
            profile_type = self.instance.profile_type
        elif self.user and hasattr(self.user, "profile"):
            profile_type = self.user.profile.profile_type

        self._set_field_requirements(profile_type)

    # _build_layout method removed - using manual form rendering in templates

    def _set_field_requirements(self, profile_type):
        """Set field requirements based on profile type"""
        if not profile_type:
            return

        # Requirements for staff and pilot profiles
        if profile_type.code in ["staff", "pilot"]:
            self.fields["date_of_birth"].required = True
            self.fields["tax_file_number"].required = True

            # Image required for staff and pilots
            if profile_type.requires_image:
                self.fields["image"].required = True

            # ARN required for pilots only
            if profile_type.code == "pilot":
                self.fields["arn_number"].required = True

    def clean_state(self):
        """Validate state field dynamically"""
        state = self.cleaned_data.get("state")
        country = self.data.get("country")  # Get from form data, not cleaned_data

        if state and country:
            # Check if state belongs to the selected country
            if not State.objects.filter(
                id=state.id, country_id=country, is_active=True
            ).exists():
                raise forms.ValidationError("Invalid state for the selected country.")

        return state

    def clean_city_direct(self):
        """Validate city field dynamically"""
        city = self.cleaned_data.get("city_direct")
        state = self.data.get("state")  # Get from form data, not cleaned_data

        if city and state:
            # Check if city belongs to the selected state
            if not City.objects.filter(
                id=city.id, state_id=state, is_active=True
            ).exists():
                raise forms.ValidationError("Invalid city for the selected state.")

        return city

    def clean(self):
        """Custom form validation"""
        cleaned_data = super().clean()

        # Validate geographical consistency
        country = cleaned_data.get("country")
        state = cleaned_data.get("state")
        city_direct = cleaned_data.get("city_direct")
        postal_code_select = cleaned_data.get("postal_code_select")

        if state and not country:
            self.add_error("country", "Country is required when state is selected.")

        if city_direct and not state:
            self.add_error("state", "State is required when city is selected.")

        if postal_code_select and not city_direct:
            self.add_error(
                "city_direct", "City is required when postal code is selected."
            )

        # Validate state belongs to country
        if country and state and state.country != country:
            self.add_error(
                "state", "Selected state does not belong to the selected country."
            )

        # Validate city belongs to state
        if state and city_direct and city_direct.state != state:
            self.add_error(
                "city_direct", "Selected city does not belong to the selected state."
            )

        # Validate postal code belongs to city
        if (
            city_direct
            and postal_code_select
            and postal_code_select.city != city_direct
        ):
            self.add_error(
                "postal_code_select",
                "Selected postal code does not belong to the selected city.",
            )

        return cleaned_data

    def save(self, commit=True):
        """Custom save method to handle geographical relationships"""
        profile = super().save(commit=False)

        # Set geographical relationships with priority: postal_code_select > city_direct + manual postal
        city_direct = self.cleaned_data.get("city_direct")
        postal_code_select = self.cleaned_data.get("postal_code_select")
        postal_code_manual = self.cleaned_data.get("postal_code_manual", "").strip()

        if postal_code_select:
            # Database postal code selected - highest priority
            profile.postal_code = postal_code_select
            profile.city = None  # Use postal code's city
            profile.postal_code_manual = None
        elif city_direct:
            # City selected with optional manual postal code
            profile.city = city_direct
            profile.postal_code = None
            profile.postal_code_manual = (
                postal_code_manual if postal_code_manual else None
            )
        else:
            # Neither selected - clear all
            profile.city = None
            profile.postal_code = None
            profile.postal_code_manual = None

        if commit:
            profile.save()

        return profile
