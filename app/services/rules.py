"""
Rule definitions for AI compliance risk assessment.

All rules are deterministic and based on EU AI Act categories.
Each rule has clear conditions and outcomes.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any


class RiskLevel(str, Enum):
    """
    EU AI Act risk levels.
    
    Based on: https://artificialintelligenceact.eu/
    """
    UNACCEPTABLE = "unacceptable"  # Prohibited AI systems
    HIGH = "high"  # High-risk AI systems (strict requirements)
    LIMITED = "limited"  # Transparency requirements only
    MINIMAL = "minimal"  # No requirements


class RuleCategory(str, Enum):
    """
    Categories of compliance rules.
    """
    PROHIBITED_PRACTICE = "prohibited_practice"
    HIGH_RISK_SYSTEM = "high_risk_system"
    TRANSPARENCY = "transparency"
    DATA_GOVERNANCE = "data_governance"
    HUMAN_OVERSIGHT = "human_oversight"


@dataclass
class RuleCondition:
    """
    Represents a condition that must be met to trigger a rule.
    
    Examples:
    - answer['Q1'] == 'yes'
    - 'biometric_data' in answer['Q3_data_types']
    - answer['Q5_risk_score'] > 7
    """
    question_id: str
    operator: str  # 'equals', 'contains', 'greater_than', etc.
    expected_value: Any
    
    def evaluate(self, answers: dict[str, Any]) -> bool:
        """
        Check if this condition is met.
        
        Args:
            answers: Dictionary of question_id -> answer_value
            
        Returns:
            bool: True if condition is met
        """
        if self.question_id not in answers:
            return False
        
        actual_value = answers[self.question_id]
        
        if self.operator == "equals":
            return actual_value == self.expected_value
        elif self.operator == "contains":
            return self.expected_value in actual_value
        elif self.operator == "greater_than":
            return actual_value > self.expected_value
        elif self.operator == "less_than":
            return actual_value < self.expected_value
        elif self.operator == "in":
            return actual_value in self.expected_value
        else:
            raise ValueError(f"Unknown operator: {self.operator}")
    
    def __repr__(self) -> str:
        return f"{self.question_id} {self.operator} {self.expected_value}"


@dataclass
class ComplianceRule:
    """
    Represents a single compliance rule.
    
    A rule has:
    - Unique identifier
    - Conditions that trigger it
    - Risk level it assigns
    - Category it belongs to
    - Explanation for users
    """
    rule_id: str
    name: str
    description: str
    category: RuleCategory
    risk_level: RiskLevel
    conditions: list[RuleCondition]
    regulation: str  # e.g., "EU_AI_ACT"
    article_reference: str | None = None  # e.g., "Article 5"
    
    def evaluate(self, answers: dict[str, Any]) -> bool:
        """
        Check if this rule is triggered by the given answers.
        
        All conditions must be met (AND logic).
        
        Args:
            answers: Dictionary of question_id -> answer_value
            
        Returns:
            bool: True if rule is triggered
        """
        if not self.conditions:
            return False
        
        return all(condition.evaluate(answers) for condition in self.conditions)
    
    def get_explanation(self) -> str:
        """
        Generate human-readable explanation of this rule.
        
        Returns:
            str: Explanation text
        """
        conditions_text = " AND ".join(str(c) for c in self.conditions)
        return (
            f"{self.name}\n"
            f"Triggered when: {conditions_text}\n"
            f"Risk Level: {self.risk_level.value}\n"
            f"Regulation: {self.regulation}"
        )


@dataclass
class RuleEvaluationResult:
    """
    Result of evaluating a rule.
    
    Contains:
    - The rule that was evaluated
    - Whether it was triggered
    - Explanation of why
    """
    rule: ComplianceRule
    triggered: bool
    explanation: str
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "rule_id": self.rule.rule_id,
            "rule_name": self.rule.name,
            "triggered": self.triggered,
            "risk_level": self.rule.risk_level.value if self.triggered else None,
            "category": self.rule.category.value,
            "explanation": self.explanation,
        }