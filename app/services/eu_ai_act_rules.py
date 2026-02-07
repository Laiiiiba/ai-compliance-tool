"""
EU AI Act rule definitions.

Based on the EU AI Act risk categories and prohibited practices.
These rules are deterministic and fully explainable.

Reference: https://artificialintelligenceact.eu/
"""

from app.services.rules import (
    ComplianceRule,
    RuleCondition,
    RiskLevel,
    RuleCategory,
)


# ============================================================================
# UNACCEPTABLE RISK - PROHIBITED AI SYSTEMS
# ============================================================================

RULE_SOCIAL_SCORING = ComplianceRule(
    rule_id="RULE_001_SOCIAL_SCORING",
    name="Social Scoring by Public Authorities",
    description=(
        "AI systems that evaluate or classify natural persons based on their "
        "social behavior or personal characteristics, with the evaluation "
        "leading to detrimental treatment."
    ),
    category=RuleCategory.PROHIBITED_PRACTICE,
    risk_level=RiskLevel.UNACCEPTABLE,
    regulation="EU_AI_ACT",
    article_reference="Article 5(1)(c)",
    conditions=[
        RuleCondition(
            question_id="system_purpose",
            operator="equals",
            expected_value="social_scoring"
        ),
    ],
)

RULE_REAL_TIME_BIOMETRIC = ComplianceRule(
    rule_id="RULE_002_REAL_TIME_BIOMETRIC",
    name="Real-Time Remote Biometric Identification",
    description=(
        "Real-time remote biometric identification systems in publicly "
        "accessible spaces for law enforcement purposes (with narrow exceptions)."
    ),
    category=RuleCategory.PROHIBITED_PRACTICE,
    risk_level=RiskLevel.UNACCEPTABLE,
    regulation="EU_AI_ACT",
    article_reference="Article 5(1)(d)",
    conditions=[
        RuleCondition(
            question_id="uses_biometric_identification",
            operator="equals",
            expected_value=True
        ),
        RuleCondition(
            question_id="real_time_processing",
            operator="equals",
            expected_value=True
        ),
        RuleCondition(
            question_id="public_spaces",
            operator="equals",
            expected_value=True
        ),
    ],
)

RULE_SUBLIMINAL_MANIPULATION = ComplianceRule(
    rule_id="RULE_003_SUBLIMINAL_MANIPULATION",
    name="Subliminal Manipulation",
    description=(
        "AI systems that deploy subliminal techniques beyond a person's "
        "consciousness to materially distort their behavior, causing harm."
    ),
    category=RuleCategory.PROHIBITED_PRACTICE,
    risk_level=RiskLevel.UNACCEPTABLE,
    regulation="EU_AI_ACT",
    article_reference="Article 5(1)(a)",
    conditions=[
        RuleCondition(
            question_id="uses_manipulation",
            operator="equals",
            expected_value=True
        ),
    ],
)


# ============================================================================
# HIGH RISK AI SYSTEMS
# ============================================================================

RULE_CREDIT_SCORING = ComplianceRule(
    rule_id="RULE_101_CREDIT_SCORING",
    name="Credit Scoring and Creditworthiness",
    description=(
        "AI systems used for evaluating creditworthiness of natural persons "
        "or establishing their credit score."
    ),
    category=RuleCategory.HIGH_RISK_SYSTEM,
    risk_level=RiskLevel.HIGH,
    regulation="EU_AI_ACT",
    article_reference="Annex III(5)(b)",
    conditions=[
        RuleCondition(
            question_id="system_purpose",
            operator="equals",
            expected_value="credit_scoring"
        ),
    ],
)

RULE_EMPLOYMENT_RECRUITMENT = ComplianceRule(
    rule_id="RULE_102_EMPLOYMENT",
    name="Employment and Recruitment Decisions",
    description=(
        "AI systems used for recruitment, making decisions on promotion, "
        "termination, or task allocation for natural persons."
    ),
    category=RuleCategory.HIGH_RISK_SYSTEM,
    risk_level=RiskLevel.HIGH,
    regulation="EU_AI_ACT",
    article_reference="Annex III(4)",
    conditions=[
        RuleCondition(
            question_id="system_purpose",
            operator="in",
            expected_value=["recruitment", "employment_decisions", "hiring"]
        ),
    ],
)

RULE_EDUCATION_ASSESSMENT = ComplianceRule(
    rule_id="RULE_103_EDUCATION",
    name="Educational Assessment and Admission",
    description=(
        "AI systems used for determining access to educational institutions "
        "or assessing students."
    ),
    category=RuleCategory.HIGH_RISK_SYSTEM,
    risk_level=RiskLevel.HIGH,
    regulation="EU_AI_ACT",
    article_reference="Annex III(3)",
    conditions=[
        RuleCondition(
            question_id="system_purpose",
            operator="contains",
            expected_value="education"
        ),
    ],
)

RULE_LAW_ENFORCEMENT = ComplianceRule(
    rule_id="RULE_104_LAW_ENFORCEMENT",
    name="Law Enforcement AI System",
    description=(
        "AI systems used by or on behalf of law enforcement authorities."
    ),
    category=RuleCategory.HIGH_RISK_SYSTEM,
    risk_level=RiskLevel.HIGH,
    regulation="EU_AI_ACT",
    article_reference="Annex III(6)",
    conditions=[
        RuleCondition(
            question_id="used_by_law_enforcement",
            operator="equals",
            expected_value=True
        ),
    ],
)

RULE_CRITICAL_INFRASTRUCTURE = ComplianceRule(
    rule_id="RULE_105_CRITICAL_INFRASTRUCTURE",
    name="Critical Infrastructure Management",
    description=(
        "AI systems used as safety components in management and operation "
        "of critical infrastructure (water, gas, electricity, transport)."
    ),
    category=RuleCategory.HIGH_RISK_SYSTEM,
    risk_level=RiskLevel.HIGH,
    regulation="EU_AI_ACT",
    article_reference="Annex III(2)",
    conditions=[
        RuleCondition(
            question_id="system_purpose",
            operator="equals",
            expected_value="critical_infrastructure"
        ),
    ],
)


# ============================================================================
# LIMITED RISK - TRANSPARENCY OBLIGATIONS
# ============================================================================

RULE_CHATBOT_TRANSPARENCY = ComplianceRule(
    rule_id="RULE_201_CHATBOT",
    name="Chatbot Transparency",
    description=(
        "AI systems that interact with natural persons must inform users "
        "they are interacting with AI."
    ),
    category=RuleCategory.TRANSPARENCY,
    risk_level=RiskLevel.LIMITED,
    regulation="EU_AI_ACT",
    article_reference="Article 52(1)",
    conditions=[
        RuleCondition(
            question_id="system_type",
            operator="equals",
            expected_value="chatbot"
        ),
    ],
)

RULE_EMOTION_RECOGNITION = ComplianceRule(
    rule_id="RULE_202_EMOTION_RECOGNITION",
    name="Emotion Recognition System",
    description=(
        "AI systems that recognize emotions must inform users of the system's "
        "operation."
    ),
    category=RuleCategory.TRANSPARENCY,
    risk_level=RiskLevel.LIMITED,
    regulation="EU_AI_ACT",
    article_reference="Article 52(2)",
    conditions=[
        RuleCondition(
            question_id="recognizes_emotions",
            operator="equals",
            expected_value=True
        ),
    ],
)

RULE_DEEPFAKE = ComplianceRule(
    rule_id="RULE_203_DEEPFAKE",
    name="Deep Fake Content",
    description=(
        "AI-generated or manipulated image, audio, or video content (deepfakes) "
        "must be labeled as artificially generated."
    ),
    category=RuleCategory.TRANSPARENCY,
    risk_level=RiskLevel.LIMITED,
    regulation="EU_AI_ACT",
    article_reference="Article 52(3)",
    conditions=[
        RuleCondition(
            question_id="generates_synthetic_content",
            operator="equals",
            expected_value=True
        ),
    ],
)


# ============================================================================
# RULE REGISTRY
# ============================================================================

# All rules in one place for easy access
ALL_RULES: list[ComplianceRule] = [
    # Unacceptable risk
    RULE_SOCIAL_SCORING,
    RULE_REAL_TIME_BIOMETRIC,
    RULE_SUBLIMINAL_MANIPULATION,
    # High risk
    RULE_CREDIT_SCORING,
    RULE_EMPLOYMENT_RECRUITMENT,
    RULE_EDUCATION_ASSESSMENT,
    RULE_LAW_ENFORCEMENT,
    RULE_CRITICAL_INFRASTRUCTURE,
    # Limited risk
    RULE_CHATBOT_TRANSPARENCY,
    RULE_EMOTION_RECOGNITION,
    RULE_DEEPFAKE,
]


def get_all_rules() -> list[ComplianceRule]:
    """Get all defined rules."""
    return ALL_RULES


def get_rule_by_id(rule_id: str) -> ComplianceRule | None:
    """Get a specific rule by its ID."""
    for rule in ALL_RULES:
        if rule.rule_id == rule_id:
            return rule
    return None


def get_rules_by_category(category: RuleCategory) -> list[ComplianceRule]:
    """Get all rules in a specific category."""
    return [rule for rule in ALL_RULES if rule.category == category]


def get_rules_by_risk_level(risk_level: RiskLevel) -> list[ComplianceRule]:
    """Get all rules for a specific risk level."""
    return [rule for rule in ALL_RULES if rule.risk_level == risk_level]