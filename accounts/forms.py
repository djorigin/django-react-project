"""
Authentication forms for DarkLight Meta project

Uses Crispy Forms with Tailwind CSS styling and HTMX integration
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.urls import reverse

User = get_user_model()


class LoginForm(forms.Form):
    """Custom login form with email and password"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter your email address", "class": "w-full"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter your password", "class": "w-full"}
        )
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "rounded border-brand-gold focus:ring-brand-purple"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "login-form"
        self.helper.attrs = {
            "hx-post": reverse("accounts:login"),
            "hx-target": "#login-form-container",
            "hx-swap": "outerHTML",
            "class": "space-y-6",
        }

        self.helper.layout = Layout(
            Div(
                Field(
                    "email",
                    css_class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                ),
                css_class="mb-4",
            ),
            Div(
                Field(
                    "password",
                    css_class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                ),
                css_class="mb-4",
            ),
            Div(
                Field("remember_me"),
                HTML(
                    '<label for="id_remember_me" class="ml-2 text-sm text-gray-600">Remember me</label>'
                ),
                css_class="flex items-center mb-6",
            ),
            Submit(
                "submit",
                "Sign In",
                css_class="w-full bg-gradient-to-r from-brand-gold to-brand-bronze hover:from-brand-gold-dark hover:to-brand-bronze-dark text-white font-bold py-3 px-4 rounded-lg transition duration-200 shadow-lg",
            ),
            HTML(
                """
                <div class="mt-4 text-center">
                    <a href="{% url 'accounts:register' %}" class="text-brand-purple hover:text-brand-purple-dark">
                        Don't have an account? Sign up
                    </a>
                </div>
            """
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            # Authenticate user
            user = authenticate(
                request=self.request,
                username=email,  # Our CustomUser uses email as username
                password=password,
            )

            if user is None:
                raise ValidationError("Invalid email or password.")

            if not user.is_active:
                raise ValidationError("This account is inactive.")

            cleaned_data["user"] = user

        return cleaned_data


class RegisterForm(UserCreationForm):
    """Custom registration form with email-based authentication"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter your email address", "class": "w-full"}
        )
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your first name", "class": "w-full"}
        ),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your last name", "class": "w-full"}
        ),
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove username field since we use email
        if "username" in self.fields:
            del self.fields["username"]

        # Update password field placeholders
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Create a strong password", "class": "w-full"}
        )
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Confirm your password", "class": "w-full"}
        )

        self.helper = FormHelper()
        self.helper.form_id = "register-form"
        self.helper.attrs = {
            "hx-post": reverse("accounts:register"),
            "hx-target": "#register-form-container",
            "hx-swap": "outerHTML",
            "class": "space-y-6",
        }

        self.helper.layout = Layout(
            Div(
                Div(
                    Field(
                        "first_name",
                        css_class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                    ),
                    css_class="w-1/2 pr-2",
                ),
                Div(
                    Field(
                        "last_name",
                        css_class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                    ),
                    css_class="w-1/2 pl-2",
                ),
                css_class="flex mb-4",
            ),
            Div(
                Field(
                    "email",
                    css_class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                ),
                css_class="mb-4",
            ),
            Div(
                Field(
                    "password1",
                    css_class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                ),
                css_class="mb-4",
            ),
            Div(
                Field(
                    "password2",
                    css_class="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-purple focus:border-transparent",
                ),
                css_class="mb-6",
            ),
            Submit(
                "submit",
                "Create Account",
                css_class="w-full bg-gradient-to-r from-brand-purple to-brand-magenta hover:from-brand-purple-dark hover:to-brand-magenta-dark text-white font-bold py-3 px-4 rounded-lg transition duration-200 shadow-lg",
            ),
            HTML(
                """
                <div class="mt-4 text-center">
                    <a href="{% url 'accounts:login' %}" class="text-brand-gold hover:text-brand-gold-dark">
                        Already have an account? Sign in
                    </a>
                </div>
            """
            ),
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        # Set email as username for authentication
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
