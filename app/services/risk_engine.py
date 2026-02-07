"""
Risk assessment engine.

Evaluates AI systems against compliance rules and calculates risk levels.
100% deterministic - no AI, no probabilistic scoring.
"""

from __future__ import annotations
import logging
from typing import Any

from app.services.rules import (
    ComplianceRule,
    RuleEvaluationResult,
    RiskLevel,
)
from app.services.eu_ai_act_rules import get_all_rules


logger = logging.getLogger(__name__)


class RiskAssessmentEngine:
    """
    Evaluates AI systems against compliance rules.
    
    All decisions are deterministic and fully explainable.
    """
    
    def __init__(self, rules: list[ComplianceRule] | None = None):
        """
        Initialize the engine with a set of rules.
        
        Args:
            rules: List of rules to evaluate. If None, uses all EU AI Act rules.
        """
        self.rules = rules or get_all_rules()
        logger.info(f"Risk engine initialized with {len(self.rules)} rules")
    
    def evaluate_assessment(
        self,
        answers: dict[str, Any]
    ) -> tuple[RiskLevel, list[RuleEvaluationResult]]:
        """
        Evaluate an assessment against all rules.
        
        Args:
            answers: Dictionary mapping question_id -> answer_value
            
        Returns:
            tuple: (overall_risk_level, list_of_triggered_rules)
        """
        logger.info(f"Evaluating assessment with {len(answers)} answers")
        
        # Evaluate all rules
        results: list[RuleEvaluationResult] = []
        
        for rule in self.rules:
            triggered = rule.evaluate(answers)
            
            result = RuleEvaluationResult(
                rule=rule,
                triggered=triggered,
                explanation=rule.get_explanation() if triggered else ""
            )
            
            results.append(result)
            
            if triggered:
                logger.info(
                    f"Rule triggered: {rule.rule_id} "
                    f"({rule.name}, risk={rule.risk_level.value})"
                )
        
        # Calculate overall risk level
        overall_risk = self._calculate_overall_risk(results)
        
        logger.info(f"Overall risk level: {overall_risk.value}")
        
        return overall_risk, results
    
    def _calculate_overall_risk(
        self,
        results: list[RuleEvaluationResult]
    ) -> RiskLevel:
        """
        Calculate overall risk level from triggered rules.
        
        Logic:
        - If any UNACCEPTABLE rule triggered → UNACCEPTABLE
        - Else if any HIGH rule triggered → HIGH
        - Else if any LIMITED rule triggered → LIMITED
        - Else → MINIMAL
        
        Args:
            results: List of rule evaluation results
            
        Returns:
            RiskLevel: Overall risk level
        """
        triggered_rules = [r for r in results if r.triggered]
        
        if not triggered_rules:
            return RiskLevel.MINIMAL
        
        # Check in order of severity
        for risk_level in [RiskLevel.UNACCEPTABLE, RiskLevel.HIGH, RiskLevel.LIMITED]:
            if any(r.rule.risk_level == risk_level for r in triggered_rules):
                return risk_level
        
        return RiskLevel.MINIMAL
    
    def get_triggered_rules(
        self,
        results: list[RuleEvaluationResult]
    ) -> list[RuleEvaluationResult]:
        """
        Filter results to only triggered rules.
        
        Args:
            results: All rule evaluation results
            
        Returns:
            list: Only triggered rules
        """
        return [r for r in results if r.triggered]
    
    def generate_report(
        self,
        risk_level: RiskLevel,
        results: list[RuleEvaluationResult]
    ) -> dict[str, Any]:
        """
        Generate a compliance report.
        
        Args:
            risk_level: Overall risk level
            results: Rule evaluation results
            
        Returns:
            dict: Report data
        """
        triggered = self.get_triggered_rules(results)
        
        report = {
            "overall_risk_level": risk_level.value,
            "total_rules_evaluated": len(results),
            "rules_triggered": len(triggered),
            "triggered_rules": [r.to_dict() for r in triggered],
            "compliance_summary": self._generate_summary(risk_level, triggered),
        }
        
        return report
    
    def _generate_summary(
        self,
        risk_level: RiskLevel,
        triggered_rules: list[RuleEvaluationResult]
    ) -> str:
        """Generate human-readable summary."""
        if risk_level == RiskLevel.UNACCEPTABLE:
            return (
                "⚠️ UNACCEPTABLE RISK: This AI system involves prohibited practices "
                "under the EU AI Act and cannot be deployed."
            )
        elif risk_level == RiskLevel.HIGH:
            return (
                "⚠️ HIGH RISK: This AI system is classified as high-risk under the "
                "EU AI Act and must comply with strict requirements including risk "
                "management, data governance, transparency, human oversight, and "
                "accuracy standards."
            )
        elif risk_level == RiskLevel.LIMITED:
            return (
                "ℹ️ LIMITED RISK: This AI system must comply with transparency "
                "obligations under the EU AI Act."
            )
        else:
            return (
                "✓ MINIMAL RISK: This AI system is not subject to specific "
                "requirements under the EU AI Act."
            )