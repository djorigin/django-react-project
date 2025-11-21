"""
Compliance Utilities - Phase 3 Scalable Framework

Utility functions and classes to make compliance integration
seamless for current and future models.
"""

import importlib

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from core.models import ComplianceCheck, ComplianceMixin, ComplianceRule


class ComplianceFramework:
    """
    Framework for managing compliance across the application.

    Provides utilities for:
    - Discovering models with ComplianceMixin
    - Batch compliance checking
    - Compliance reporting
    - Automatic compliance rule application
    """

    @classmethod
    def get_compliance_models(cls):
        """
        Get all models that inherit from ComplianceMixin.

        Returns:
            List of model classes that support compliance
        """
        compliance_models = []

        for model in apps.get_models():
            if issubclass(model, ComplianceMixin):
                compliance_models.append(model)

        return compliance_models

    @classmethod
    def get_compliance_objects(cls, user=None):
        """
        Get all objects with compliance support that a user can access.

        Args:
            user: Django user object (for permission filtering)

        Returns:
            List of model instances with compliance data
        """
        objects_with_compliance = []

        for model_class in cls.get_compliance_models():
            queryset = model_class.objects.all()

            # Apply user-based filtering if needed
            if user and hasattr(model_class, "filter_by_user"):
                queryset = model_class.filter_by_user(user)

            for obj in queryset:
                try:
                    compliance_data = obj.get_compliance_summary()
                    objects_with_compliance.append(
                        {
                            "object": obj,
                            "model": model_class,
                            "compliance": compliance_data,
                            "app_label": obj._meta.app_label,
                            "model_name": obj._meta.model_name,
                        }
                    )
                except Exception:
                    # Log but don't fail for individual compliance errors
                    continue

        return objects_with_compliance

    @classmethod
    def run_system_compliance_check(cls):
        """
        Run compliance check across all models in the system.

        Returns:
            Dictionary with system-wide compliance summary
        """
        total_objects = 0
        compliant_objects = 0
        warning_objects = 0
        non_compliant_objects = 0

        model_summaries = {}

        for model_class in cls.get_compliance_models():
            model_stats = {"total": 0, "green": 0, "yellow": 0, "red": 0, "errors": 0}

            for obj in model_class.objects.all():
                model_stats["total"] += 1
                total_objects += 1

                try:
                    compliance = obj.get_compliance_summary()
                    status = compliance.get("overall_status", "green")

                    if status == "green":
                        model_stats["green"] += 1
                        compliant_objects += 1
                    elif status == "yellow":
                        model_stats["yellow"] += 1
                        warning_objects += 1
                    else:
                        model_stats["red"] += 1
                        non_compliant_objects += 1

                except Exception:
                    model_stats["errors"] += 1

            model_summaries[
                f"{model_class._meta.app_label}.{model_class._meta.model_name}"
            ] = model_stats

        return {
            "total_objects": total_objects,
            "compliant_objects": compliant_objects,
            "warning_objects": warning_objects,
            "non_compliant_objects": non_compliant_objects,
            "compliance_rate": (
                (compliant_objects / total_objects * 100) if total_objects > 0 else 100
            ),
            "model_summaries": model_summaries,
        }

    @classmethod
    def get_compliance_model_info(cls):
        """
        Get information about all models with compliance support.

        Returns:
            Dictionary of model information for documentation/debugging
        """
        model_info = {}

        for model_class in cls.get_compliance_models():
            model_key = f"{model_class._meta.app_label}.{model_class._meta.model_name}"
            model_info[model_key] = {
                "model_class": model_class,
                "verbose_name": model_class._meta.verbose_name,
                "app_label": model_class._meta.app_label,
                "model_name": model_class._meta.model_name,
                "total_objects": model_class.objects.count(),
                "has_get_compliance_summary": hasattr(
                    model_class, "get_compliance_summary"
                ),
            }

        return model_info


class ComplianceModelMixin:
    """
    Mixin to provide additional compliance utilities to models.

    This can be added to existing models to enhance compliance functionality
    without requiring ComplianceMixin inheritance.
    """

    def get_compliance_css_classes(self, prefix="border"):
        """Get CSS classes for compliance status."""
        if hasattr(self, "get_compliance_summary"):
            try:
                compliance = self.get_compliance_summary()
                status = compliance.get("overall_status", "green")
            except Exception:
                status = "yellow"
        else:
            status = "green"

        css_map = {
            "border": {
                "green": "border-green-500",
                "yellow": "border-yellow-500",
                "red": "border-red-500",
            },
            "bg": {
                "green": "bg-green-500",
                "yellow": "bg-yellow-500",
                "red": "bg-red-500",
            },
            "text": {
                "green": "text-green-500",
                "yellow": "text-yellow-500",
                "red": "text-red-500",
            },
        }

        return css_map.get(prefix, css_map["border"]).get(status, "border-green-500")

    def is_compliance_supported(self):
        """Check if this model supports compliance checking."""
        return hasattr(self, "get_compliance_summary")


def apply_compliance_to_model(model_class, compliance_method=None):
    """
    Dynamically add compliance functionality to a model class.

    Args:
        model_class: The Django model class to enhance
        compliance_method: Custom compliance method (optional)

    This function allows adding compliance to existing models
    without modifying their source code.
    """
    if not hasattr(model_class, "get_compliance_summary"):

        def default_compliance_summary(self):
            """Default compliance method for dynamically enhanced models."""
            return {
                "overall_status": "green",
                "total_checks": 1,
                "failed_checks": 0,
                "issues": [],
                "last_checked": timezone.now(),
                "compliance_type": f"dynamic_{self._meta.model_name}",
            }

        # Apply the compliance method
        if compliance_method:
            model_class.get_compliance_summary = compliance_method
        else:
            model_class.get_compliance_summary = default_compliance_summary

        # Add the mixin utilities
        for attr_name in dir(ComplianceModelMixin):
            if not attr_name.startswith("_"):
                attr = getattr(ComplianceModelMixin, attr_name)
                if callable(attr):
                    setattr(model_class, attr_name, attr)


def get_model_compliance_dashboard_data():
    """
    Get compliance data formatted for dashboard display.

    Returns:
        Dictionary suitable for dashboard templates
    """
    framework = ComplianceFramework()
    system_stats = framework.run_system_compliance_check()
    model_info = framework.get_compliance_model_info()

    return {
        "system_summary": system_stats,
        "models": model_info,
        "compliance_models_count": len(model_info),
        "active_rules_count": ComplianceRule.objects.filter(is_active=True).count(),
        "total_checks_today": (
            ComplianceCheck.objects.filter(
                last_checked__date=timezone.now().date()
            ).count()
            if "ComplianceCheck" in str(apps.get_models())
            else 0
        ),
    }
