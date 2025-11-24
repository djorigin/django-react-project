"""
ComplianceEngine - Central Intelligence for Three-Color CASA Compliance

This service provides the central intelligence for the revolutionary three-color
compliance system that transforms CASA regulatory compliance from a burden into
an automated competitive advantage.

The ComplianceEngine manages:
- Automated compliance rule evaluation
- Three-color status determination (GREEN/YELLOW/RED)
- Real-time compliance checking
- Compliance rule management and enforcement
- Integration with all ComplianceMixin models across the application

Design Philosophy:
- Centralized compliance intelligence
- Zero configuration compliance checking
- Automated rule discovery and application
- Real-time status updates
- Intelligent caching for performance
"""

from datetime import timedelta
from typing import Any, Dict, List, Optional, Type

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from .models import ComplianceCheck, ComplianceMixin, ComplianceRule, ComplianceStatus


class ComplianceEngine:
    """
    Central engine for three-color compliance system intelligence.

    This service orchestrates all compliance checking across the application
    and provides the intelligence for the revolutionary CASA compliance automation.
    """

    def __init__(self):
        """Initialize the ComplianceEngine"""
        self._rule_cache = {}
        self._cache_timeout = timedelta(hours=1)
        self._last_cache_update = None

    def get_applicable_rules(
        self, model_class: Type[models.Model]
    ) -> List[ComplianceRule]:
        """
        Get all compliance rules applicable to a specific model class.

        Args:
            model_class: The Django model class to get rules for

        Returns:
            List of applicable ComplianceRule objects
        """
        # For now, return all active rules
        # In the future, this can be enhanced with model-specific rule filtering
        return list(ComplianceRule.objects.filter(is_active=True))

    def check_object_compliance(
        self,
        obj: ComplianceMixin,
        rules: Optional[List[ComplianceRule]] = None,
        user: Optional[models.Model] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive compliance checking for a single object.

        Args:
            obj: Object implementing ComplianceMixin to check
            rules: Optional specific rules to check (defaults to all applicable)
            user: User performing the check

        Returns:
            Dict containing compliance results and status
        """
        if not isinstance(obj, ComplianceMixin):
            raise ValueError("Object must implement ComplianceMixin")

        if rules is None:
            rules = self.get_applicable_rules(obj.__class__)

        results = {
            "object": str(obj),
            "overall_status": ComplianceStatus.GREEN,
            "checks_performed": 0,
            "checks_passed": 0,
            "checks_failed": 0,
            "rule_results": [],
            "timestamp": timezone.now(),
        }

        content_type = ContentType.objects.get_for_model(obj)

        for rule in rules:
            # Get or create compliance check record
            check, created = ComplianceCheck.objects.get_or_create(
                content_type=content_type,
                object_id=obj.id,
                rule=rule,
                defaults={"status": ComplianceStatus.GREEN, "checked_by": user},
            )

            # Perform the actual compliance check
            check_result = self._evaluate_rule(obj, rule, user)

            # Update the check record
            check.status = check_result["status"]
            check.details = check_result.get("details", {})
            check.checked_by = user
            check.update_next_check_due()
            check.save()

            # Update results
            results["checks_performed"] += 1
            if check_result["status"] == ComplianceStatus.GREEN:
                results["checks_passed"] += 1
            else:
                results["checks_failed"] += 1

            results["rule_results"].append(
                {
                    "rule": rule.rule_code,
                    "status": check_result["status"],
                    "message": check_result.get("message", ""),
                    "details": check_result.get("details", {}),
                }
            )

            # Update overall status (worst case wins)
            if check_result["status"] == ComplianceStatus.RED:
                results["overall_status"] = ComplianceStatus.RED
            elif (
                check_result["status"] == ComplianceStatus.YELLOW
                and results["overall_status"] != ComplianceStatus.RED
            ):
                results["overall_status"] = ComplianceStatus.YELLOW

        return results

    def _evaluate_rule(
        self,
        obj: ComplianceMixin,
        rule: ComplianceRule,
        user: Optional[models.Model] = None,
    ) -> Dict[str, Any]:
        """
        REVOLUTIONARY: Dynamic rule evaluation using new ComplianceRule.evaluate_against_object()

        BREAKING CHANGE: Completely replaces hardcoded evaluation logic with
        intelligent, configurable rule-driven evaluation.

        Args:
            obj: Object to evaluate
            rule: ComplianceRule with dynamic evaluation logic
            user: User performing the evaluation

        Returns:
            Dict with evaluation results using new rule-driven system
        """
        # Use the revolutionary new dynamic rule evaluation
        rule_result = rule.evaluate_against_object(obj)

        # Convert to expected format for ComplianceEngine
        result = {
            "status": rule_result["status"],
            "message": rule_result["message"],
            "details": {
                "rule_code": rule_result["rule_code"],
                "field_value": rule_result.get("field_value"),
                "evaluation_type": rule_result.get("evaluation_type"),
                "evaluation_time": timezone.now().isoformat(),
                "evaluator": str(user) if user else "System",
                "rule_engine_version": "2.0_dynamic",
            },
        }

        # Add error details if evaluation failed due to error
        if "error" in rule_result:
            result["details"]["error"] = rule_result["error"]

        return result

    def bulk_check_compliance(
        self, objects: List[ComplianceMixin], user: Optional[models.Model] = None
    ) -> Dict[str, Any]:
        """
        Perform compliance checking for multiple objects.

        Args:
            objects: List of objects implementing ComplianceMixin
            user: User performing the checks

        Returns:
            Dict with bulk compliance results
        """
        results = {
            "total_objects": len(objects),
            "compliant_objects": 0,
            "warning_objects": 0,
            "non_compliant_objects": 0,
            "object_results": [],
            "timestamp": timezone.now(),
        }

        for obj in objects:
            obj_result = self.check_object_compliance(obj, user=user)

            # Count by status
            status = obj_result["overall_status"]
            if status == ComplianceStatus.GREEN:
                results["compliant_objects"] += 1
            elif status == ComplianceStatus.YELLOW:
                results["warning_objects"] += 1
            else:
                results["non_compliant_objects"] += 1

            results["object_results"].append(obj_result)

        return results

    def get_overdue_checks(self) -> List[ComplianceCheck]:
        """
        Get all compliance checks that are overdue for re-evaluation.

        Returns:
            List of overdue ComplianceCheck objects
        """
        return list(
            ComplianceCheck.objects.filter(
                next_check_due__lt=timezone.now(), rule__is_active=True
            )
        )

    def run_scheduled_compliance_checks(
        self, user: Optional[models.Model] = None
    ) -> Dict[str, Any]:
        """
        Run all scheduled/overdue compliance checks across the system.

        Args:
            user: User performing the checks

        Returns:
            Dict with results of scheduled checks
        """
        overdue_checks = self.get_overdue_checks()

        results = {
            "overdue_checks_found": len(overdue_checks),
            "checks_completed": 0,
            "checks_failed": 0,
            "objects_processed": [],
            "timestamp": timezone.now(),
        }

        # Group checks by object to avoid duplicate processing
        objects_to_check = {}
        for check in overdue_checks:
            obj = check.content_object
            if obj not in objects_to_check:
                objects_to_check[obj] = []
            objects_to_check[obj].append(check.rule)

        # Process each object with its overdue rules
        for obj, rules in objects_to_check.items():
            try:
                obj_result = self.check_object_compliance(obj, rules=rules, user=user)
                results["checks_completed"] += obj_result["checks_performed"]
                results["objects_processed"].append(
                    {
                        "object": str(obj),
                        "status": obj_result["overall_status"],
                        "checks": obj_result["checks_performed"],
                    }
                )
            except Exception as e:
                results["checks_failed"] += len(rules)
                results["objects_processed"].append(
                    {"object": str(obj), "error": str(e), "checks": len(rules)}
                )

        return results

    def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive compliance data for dashboard display.

        Returns:
            Dict with dashboard-ready compliance statistics
        """
        # Get all compliance checks grouped by status
        all_checks = ComplianceCheck.objects.filter(rule__is_active=True)

        dashboard_data = {
            "total_checks": all_checks.count(),
            "green_checks": all_checks.filter(status=ComplianceStatus.GREEN).count(),
            "yellow_checks": all_checks.filter(status=ComplianceStatus.YELLOW).count(),
            "red_checks": all_checks.filter(status=ComplianceStatus.RED).count(),
            "overdue_checks": self.get_overdue_checks(),
            "recent_checks": list(all_checks.order_by("-last_checked")[:10]),
            "rules_summary": {
                "total_rules": ComplianceRule.objects.filter(is_active=True).count(),
                "critical_rules": ComplianceRule.objects.filter(
                    is_active=True, severity=ComplianceStatus.RED
                ).count(),
                "warning_rules": ComplianceRule.objects.filter(
                    is_active=True, severity=ComplianceStatus.YELLOW
                ).count(),
            },
            "timestamp": timezone.now(),
        }

        # Calculate percentages
        total = dashboard_data["total_checks"]
        if total > 0:
            dashboard_data["green_percentage"] = (
                dashboard_data["green_checks"] / total
            ) * 100
            dashboard_data["yellow_percentage"] = (
                dashboard_data["yellow_checks"] / total
            ) * 100
            dashboard_data["red_percentage"] = (
                dashboard_data["red_checks"] / total
            ) * 100
        else:
            dashboard_data.update(
                {"green_percentage": 100, "yellow_percentage": 0, "red_percentage": 0}
            )

        return dashboard_data


# Global ComplianceEngine instance
compliance_engine = ComplianceEngine()
