"""
JSA Section 2 ComplianceRules Setup Command

Creates ComplianceRule entries for JSA Section 2 CASA RCP Manual compliance
that delegate to our proven GREEN TDD business logic methods.

This integrates our TDD-proven JSA methods with the existing compliance_engine
infrastructure without breaking our working GREEN tests.
"""

from django.core.management.base import BaseCommand

from core.models import ComplianceRule, ComplianceStatus


class Command(BaseCommand):
    help = "Create JSA Section 2 ComplianceRules for compliance_engine integration"

    def handle(self, *args, **options):
        """Create JSA Section 2 compliance rules"""

        rules_created = 0
        rules_updated = 0

        # JSA Section 2 Exemption Rule
        exemption_rule, created = ComplianceRule.objects.get_or_create(
            rule_code="JSA_SECTION2_EXEMPTION",
            defaults={
                "rule_name": "JSA Section 2 Exemption Compliance",
                "description": "CASA RCP Manual: Section 2 does not need to be completed where operation falls within SOC, using RPA not heavier than 2kg and where no official authorization is required",
                "casa_reference": "CASA RCP Manual Section 2",
                "target_model": "FlightOperation",
                "target_app": "flight_operations",
                "evaluation_type": "custom_method",
                "custom_method_name": "check_jsa_section2_exemption",
                "severity": ComplianceStatus.YELLOW,
                "failure_message": "JSA Section 2 required - operation does not qualify for exemption",
                "check_frequency_hours": 1,  # Check frequently for operations
                "is_active": True,
            },
        )
        if created:
            rules_created += 1
            self.stdout.write(f"✅ Created: {exemption_rule.rule_code}")
        else:
            rules_updated += 1
            self.stdout.write(f"🔄 Updated: {exemption_rule.rule_code}")

        # Aircraft Weight Compliance Rule
        weight_rule, created = ComplianceRule.objects.get_or_create(
            rule_code="JSA_AIRCRAFT_WEIGHT_2KG",
            defaults={
                "rule_name": "Aircraft Weight ≤2kg Compliance",
                "description": "Aircraft must not exceed 2kg for JSA Section 2 exemption eligibility",
                "casa_reference": "CASA RCP Manual Section 2 - Aircraft Weight Requirements",
                "target_model": "FlightOperation",
                "target_app": "flight_operations",
                "evaluation_type": "custom_method",
                "custom_method_name": "check_aircraft_weight_compliance",
                "severity": ComplianceStatus.RED,
                "failure_message": "Aircraft exceeds 2kg weight limit - JSA Section 2 required",
                "check_frequency_hours": 24,
                "is_active": True,
            },
        )
        if created:
            rules_created += 1
            self.stdout.write(f"✅ Created: {weight_rule.rule_code}")
        else:
            rules_updated += 1
            self.stdout.write(f"🔄 Updated: {weight_rule.rule_code}")

        # Official Authorization Compliance Rule
        auth_rule, created = ComplianceRule.objects.get_or_create(
            rule_code="JSA_OFFICIAL_AUTHORIZATION",
            defaults={
                "rule_name": "Official Authorization Not Required",
                "description": "Operation must not require official authorization for JSA Section 2 exemption",
                "casa_reference": "CASA RCP Manual Section 2 - Authorization Requirements",
                "target_model": "FlightOperation",
                "target_app": "flight_operations",
                "evaluation_type": "custom_method",
                "custom_method_name": "check_official_authorization_compliance",
                "severity": ComplianceStatus.RED,
                "failure_message": "Official authorization required - JSA Section 2 mandatory",
                "check_frequency_hours": 1,
                "is_active": True,
            },
        )
        if created:
            rules_created += 1
            self.stdout.write(f"✅ Created: {auth_rule.rule_code}")
        else:
            rules_updated += 1
            self.stdout.write(f"🔄 Updated: {auth_rule.rule_code}")

        # SOC Compliance Rule
        soc_rule, created = ComplianceRule.objects.get_or_create(
            rule_code="JSA_SOC_COMPLIANCE",
            defaults={
                "rule_name": "Standard Operating Conditions (SOC) Compliance",
                "description": "Operation must fall within Standard Operating Conditions for JSA Section 2 exemption",
                "casa_reference": "CASA RCP Manual Section 1.3 - Preliminary Assessment",
                "target_model": "FlightOperation",
                "target_app": "flight_operations",
                "evaluation_type": "custom_method",
                "custom_method_name": "check_soc_compliance",
                "severity": ComplianceStatus.RED,
                "failure_message": "Operation outside SOC - JSA Section 2 required",
                "check_frequency_hours": 1,
                "is_active": True,
            },
        )
        if created:
            rules_created += 1
            self.stdout.write(f"✅ Created: {soc_rule.rule_code}")
        else:
            rules_updated += 1
            self.stdout.write(f"🔄 Updated: {soc_rule.rule_code}")

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"🎯 JSA Section 2 ComplianceRules Setup Complete!")
        self.stdout.write(f"📊 Rules Created: {rules_created}")
        self.stdout.write(f"🔄 Rules Updated: {rules_updated}")
        self.stdout.write(f"✅ Total Active Rules: {rules_created + rules_updated}")
        self.stdout.write(
            "\n🚀 compliance_engine now integrated with TDD GREEN JSA business logic!"
        )
        self.stdout.write("=" * 60)
