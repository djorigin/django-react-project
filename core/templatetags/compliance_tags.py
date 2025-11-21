"""
Compliance Template Tags - Phase 3 Visual Integration

Provides template tags for seamless three-color compliance integration
across all forms and models. Designed to work with current models and
automatically support future models that inherit ComplianceMixin.

Usage:
    {% load compliance_tags %}
    {% compliance_border form.field_name object %}
    {% compliance_status object %}
    {% compliance_widget object %}
"""

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("components/compliance_field_wrapper.html")
def compliance_field(field, obj=None, status=None, size="md"):
    """
    Wrap any form field with three-color compliance status.

    Args:
        field: Django form field
        obj: Model object with ComplianceMixin (optional)
        status: Manual status override ('green'|'yellow'|'red')
        size: Size variant ('sm'|'md'|'lg')

    Returns:
        Rendered field with compliance border and status indicator
    """
    # Get compliance status from object if available
    computed_status = "green"  # Default
    compliance_data = {}

    if obj and hasattr(obj, "get_compliance_summary"):
        try:
            compliance_data = obj.get_compliance_summary()
            computed_status = compliance_data.get("overall_status", "green")
        except Exception:
            # Graceful fallback for any compliance checking errors
            computed_status = "yellow"
    elif status:
        computed_status = status

    # Determine CSS classes based on status
    border_classes = {
        "green": "border-green-500 bg-green-50/10 focus-within:ring-green-500/20",
        "yellow": "border-yellow-500 bg-yellow-50/10 focus-within:ring-yellow-500/20",
        "red": "border-red-500 bg-red-50/10 focus-within:ring-red-500/20",
    }

    status_classes = {
        "green": "text-green-400 bg-green-900/20",
        "yellow": "text-yellow-400 bg-yellow-900/20",
        "red": "text-red-400 bg-red-900/20",
    }

    context = {
        "field": field,
        "object": obj,
        "status": computed_status,
        "size": size,
        "border_class": border_classes.get(computed_status, border_classes["green"]),
        "status_class": status_classes.get(computed_status, status_classes["green"]),
        "compliance_data": compliance_data,
        "field_id": (
            field.id_for_label
            if hasattr(field, "id_for_label")
            else f"field_{id(field)}"
        ),
    }

    return context


@register.inclusion_tag("components/compliance_status_badge.html")
def compliance_status(obj, size="md", show_details=False):
    """
    Display compliance status badge for any ComplianceMixin object.

    Args:
        obj: Model object with ComplianceMixin
        size: Badge size ('xs'|'sm'|'md'|'lg')
        show_details: Whether to show check counts

    Returns:
        Rendered status badge with appropriate colors
    """
    status = "green"
    compliance_data = {}

    if obj and hasattr(obj, "get_compliance_summary"):
        try:
            compliance_data = obj.get_compliance_summary()
            status = compliance_data.get("overall_status", "green")
        except Exception:
            status = "yellow"

    return {
        "status": status,
        "size": size,
        "show_details": show_details,
        "compliance_data": compliance_data,
        "object": obj,
    }


@register.simple_tag
def compliance_css_class(obj, prefix="border"):
    """
    Return CSS class based on compliance status.

    Args:
        obj: Model object with ComplianceMixin
        prefix: CSS prefix ('border'|'bg'|'text'|'ring')

    Returns:
        CSS class string for the compliance status
    """
    status = "green"

    if obj and hasattr(obj, "get_compliance_summary"):
        try:
            compliance_data = obj.get_compliance_summary()
            status = compliance_data.get("overall_status", "green")
        except Exception:
            status = "yellow"

    css_map = {
        "border": {
            "green": "border-green-500",
            "yellow": "border-yellow-500",
            "red": "border-red-500",
        },
        "bg": {"green": "bg-green-500", "yellow": "bg-yellow-500", "red": "bg-red-500"},
        "text": {
            "green": "text-green-500",
            "yellow": "text-yellow-500",
            "red": "text-red-500",
        },
        "ring": {
            "green": "ring-green-500",
            "yellow": "ring-yellow-500",
            "red": "ring-red-500",
        },
    }

    return css_map.get(prefix, css_map["border"]).get(status, "border-green-500")


@register.filter
def has_compliance(obj):
    """
    Check if object has ComplianceMixin functionality.

    Args:
        obj: Model object to check

    Returns:
        Boolean indicating if object supports compliance checking
    """
    return obj and hasattr(obj, "get_compliance_summary")


@register.inclusion_tag("components/compliance_form_wrapper.html", takes_context=True)
def compliance_form(context, form, obj=None, title=None):
    """
    Wrap entire form with compliance-aware styling.

    Args:
        form: Django form instance
        obj: Associated model object with ComplianceMixin
        title: Form title override

    Returns:
        Complete form wrapper with compliance status integration
    """
    status = "green"
    compliance_data = {}

    if obj and hasattr(obj, "get_compliance_summary"):
        try:
            compliance_data = obj.get_compliance_summary()
            status = compliance_data.get("overall_status", "green")
        except Exception:
            status = "yellow"

    return {
        "form": form,
        "object": obj,
        "status": status,
        "compliance_data": compliance_data,
        "title": title or f"{obj._meta.verbose_name.title()} Form" if obj else "Form",
        "request": context.get("request"),
        "user": context.get("user"),
    }


@register.simple_tag
def model_compliance_data(obj):
    """
    Get compliance data as JSON for HTMX integration.

    Args:
        obj: Model object with ComplianceMixin

    Returns:
        JSON string of compliance data for frontend use
    """
    import json

    if not obj or not hasattr(obj, "get_compliance_summary"):
        return json.dumps({"status": "green", "supported": False})

    try:
        compliance_data = obj.get_compliance_summary()
        compliance_data["supported"] = True
        compliance_data["object_type"] = obj._meta.label
        compliance_data["object_id"] = obj.pk if obj.pk else None
        return json.dumps(compliance_data)
    except Exception:
        return json.dumps({"status": "yellow", "supported": False, "error": True})


@register.filter
def model_name(obj):
    """
    Get model name for an object.

    Args:
        obj: Django model instance

    Returns:
        Model label (app_label.model_name) or empty string
    """
    if obj and hasattr(obj, "_meta"):
        return obj._meta.label
    return ""
