"""
Tests for the risk assessment engine.

Verifies that rules are evaluated correctly and risk levels are calculated properly.
"""

import pytest
from app.services.risk_engine import RiskAssessmentEngine
from app.services.rules import RiskLevel, RuleCategory
from app.services.eu_ai_act_rules import (
    RULE_CREDIT_SCORING,
    RULE_SOCIAL_SCORING,
    RULE_CHATBOT_TRANSPARENCY,
    get_all_rules,
)


class TestRiskEngine:
    """Test suite for RiskAssessmentEngine."""
    
    def test_engine_initialization(self):
        """Test that engine initializes with all rules."""
        engine = RiskAssessmentEngine()
        assert len(engine.rules) > 0
        assert len(engine.rules) == len(get_all_rules())
    
    def test_minimal_risk_no_triggers(self):
        """Test that system with no triggered rules is minimal risk."""
        engine = RiskAssessmentEngine()
        
        # Answers that don't trigger any rules
        answers = {
            "system_purpose": "general_chatbot",
            "system_type": "assistant",
            "uses_biometric_identification": False,
            "uses_manipulation": False,
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        assert risk_level == RiskLevel.MINIMAL
        assert len(engine.get_triggered_rules(results)) == 0
    
    def test_high_risk_credit_scoring(self):
        """Test that credit scoring system is classified as high risk."""
        engine = RiskAssessmentEngine()
        
        answers = {
            "system_purpose": "credit_scoring",
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        assert risk_level == RiskLevel.HIGH
        
        triggered = engine.get_triggered_rules(results)
        assert len(triggered) >= 1
        
        # Verify credit scoring rule was triggered
        credit_rule_triggered = any(
            r.rule.rule_id == "RULE_101_CREDIT_SCORING" 
            for r in triggered
        )
        assert credit_rule_triggered
    
    def test_unacceptable_risk_social_scoring(self):
        """Test that social scoring is prohibited (unacceptable risk)."""
        engine = RiskAssessmentEngine()
        
        answers = {
            "system_purpose": "social_scoring",
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        assert risk_level == RiskLevel.UNACCEPTABLE
        
        triggered = engine.get_triggered_rules(results)
        assert len(triggered) >= 1
        
        # Verify social scoring rule was triggered
        social_rule_triggered = any(
            r.rule.rule_id == "RULE_001_SOCIAL_SCORING"
            for r in triggered
        )
        assert social_rule_triggered
    
    def test_limited_risk_chatbot(self):
        """Test that chatbot has limited risk (transparency requirement)."""
        engine = RiskAssessmentEngine()
        
        answers = {
            "system_type": "chatbot",
            "system_purpose": "customer_service",
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        assert risk_level == RiskLevel.LIMITED
        
        triggered = engine.get_triggered_rules(results)
        assert len(triggered) >= 1
        
        # Verify chatbot transparency rule was triggered
        chatbot_rule_triggered = any(
            r.rule.rule_id == "RULE_201_CHATBOT"
            for r in triggered
        )
        assert chatbot_rule_triggered
    
    def test_highest_risk_wins(self):
        """Test that highest risk level takes precedence."""
        engine = RiskAssessmentEngine()
        
        # Answers that trigger both HIGH and LIMITED risk rules
        answers = {
            "system_purpose": "credit_scoring",  # HIGH
            "system_type": "chatbot",  # LIMITED
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        # Should be HIGH, not LIMITED
        assert risk_level == RiskLevel.HIGH
        
        triggered = engine.get_triggered_rules(results)
        assert len(triggered) >= 2
    
    def test_unacceptable_overrides_high(self):
        """Test that unacceptable risk overrides high risk."""
        engine = RiskAssessmentEngine()
        
        answers = {
            "system_purpose": "social_scoring",  # UNACCEPTABLE
            "used_by_law_enforcement": True,  # HIGH
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        # Should be UNACCEPTABLE, not HIGH
        assert risk_level == RiskLevel.UNACCEPTABLE
    
    def test_multiple_conditions_and_logic(self):
        """Test that rules with multiple conditions use AND logic."""
        engine = RiskAssessmentEngine()
        
        # Real-time biometric requires ALL conditions
        answers_partial = {
            "uses_biometric_identification": True,
            "real_time_processing": False,  # Missing this
            "public_spaces": True,
        }
        
        risk_level_partial, results_partial = engine.evaluate_assessment(answers_partial)
        
        biometric_triggered_partial = any(
            r.rule.rule_id == "RULE_002_REAL_TIME_BIOMETRIC" and r.triggered
            for r in results_partial
        )
        assert not biometric_triggered_partial
        
        # Now with all conditions met
        answers_complete = {
            "uses_biometric_identification": True,
            "real_time_processing": True,
            "public_spaces": True,
        }
        
        risk_level_complete, results_complete = engine.evaluate_assessment(answers_complete)
        
        biometric_triggered_complete = any(
            r.rule.rule_id == "RULE_002_REAL_TIME_BIOMETRIC" and r.triggered
            for r in results_complete
        )
        assert biometric_triggered_complete
        assert risk_level_complete == RiskLevel.UNACCEPTABLE
    
    def test_report_generation(self):
        """Test that compliance report is generated correctly."""
        engine = RiskAssessmentEngine()
        
        answers = {
            "system_purpose": "credit_scoring",
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        report = engine.generate_report(risk_level, results)
        
        assert "overall_risk_level" in report
        assert report["overall_risk_level"] == "high"
        
        assert "total_rules_evaluated" in report
        assert report["total_rules_evaluated"] > 0
        
        assert "rules_triggered" in report
        assert report["rules_triggered"] >= 1
        
        assert "triggered_rules" in report
        assert isinstance(report["triggered_rules"], list)
        
        assert "compliance_summary" in report
        assert "HIGH RISK" in report["compliance_summary"]
    
    def test_rule_condition_operators(self):
        """Test different condition operators."""
        from app.services.rules import RuleCondition
        
        # Test 'equals' operator
        cond_equals = RuleCondition("q1", "equals", "yes")
        assert cond_equals.evaluate({"q1": "yes"}) is True
        assert cond_equals.evaluate({"q1": "no"}) is False
        
        # Test 'contains' operator
        cond_contains = RuleCondition("q2", "contains", "biometric")
        assert cond_contains.evaluate({"q2": ["biometric", "facial"]}) is True
        assert cond_contains.evaluate({"q2": ["facial"]}) is False
        
        # Test 'in' operator
        cond_in = RuleCondition("q3", "in", ["opt1", "opt2"])
        assert cond_in.evaluate({"q3": "opt1"}) is True
        assert cond_in.evaluate({"q3": "opt3"}) is False
        
        # Test 'greater_than' operator
        cond_gt = RuleCondition("q4", "greater_than", 5)
        assert cond_gt.evaluate({"q4": 7}) is True
        assert cond_gt.evaluate({"q4": 3}) is False
        
        # Test 'less_than' operator
        cond_lt = RuleCondition("q5", "less_than", 10)
        assert cond_lt.evaluate({"q5": 5}) is True
        assert cond_lt.evaluate({"q5": 15}) is False
    
    def test_missing_answer_not_trigger(self):
        """Test that rules don't trigger when answer is missing."""
        from app.services.rules import RuleCondition
        
        cond = RuleCondition("q1", "equals", "yes")
        
        # Missing answer should not trigger
        assert cond.evaluate({}) is False
        assert cond.evaluate({"q2": "yes"}) is False  # Different question
    
    def test_employment_recruitment_variations(self):
        """Test that employment rule handles multiple values."""
        engine = RiskAssessmentEngine()
        
        # Test different employment purposes
        for purpose in ["recruitment", "employment_decisions", "hiring"]:
            answers = {"system_purpose": purpose}
            risk_level, results = engine.evaluate_assessment(answers)
            
            assert risk_level == RiskLevel.HIGH
            
            employment_triggered = any(
                r.rule.rule_id == "RULE_102_EMPLOYMENT" and r.triggered
                for r in results
            )
            assert employment_triggered, f"Failed for purpose: {purpose}"


class TestRuleExplainability:
    """Test that rules provide clear explanations."""
    
    def test_rule_explanation_format(self):
        """Test that rule explanations are properly formatted."""
        explanation = RULE_CREDIT_SCORING.get_explanation()
        
        assert RULE_CREDIT_SCORING.name in explanation
        assert "Risk Level:" in explanation
        assert "high" in explanation.lower()
        assert "Regulation:" in explanation
    
    def test_result_to_dict(self):
        """Test that evaluation results convert to dict correctly."""
        from app.services.rules import RuleEvaluationResult
        
        result = RuleEvaluationResult(
            rule=RULE_CREDIT_SCORING,
            triggered=True,
            explanation="Test explanation"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["rule_id"] == "RULE_101_CREDIT_SCORING"
        assert result_dict["triggered"] is True
        assert result_dict["risk_level"] == "high"
        assert result_dict["explanation"] == "Test explanation"
    
    def test_untriggered_result_to_dict(self):
        """Test that untriggered results have None risk_level."""
        from app.services.rules import RuleEvaluationResult
        
        result = RuleEvaluationResult(
            rule=RULE_CHATBOT_TRANSPARENCY,
            triggered=False,
            explanation=""
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["triggered"] is False
        assert result_dict["risk_level"] is None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_answers(self):
        """Test engine with no answers."""
        engine = RiskAssessmentEngine()
        
        risk_level, results = engine.evaluate_assessment({})
        
        # No rules should trigger with empty answers
        assert risk_level == RiskLevel.MINIMAL
        assert len(engine.get_triggered_rules(results)) == 0
    
    def test_invalid_operator(self):
        """Test that invalid operator raises error."""
        from app.services.rules import RuleCondition
        
        cond = RuleCondition("q1", "invalid_operator", "value")
        
        with pytest.raises(ValueError, match="Unknown operator"):
            cond.evaluate({"q1": "value"})
    
    def test_custom_rule_set(self):
        """Test engine with custom subset of rules."""
        custom_rules = [RULE_CREDIT_SCORING, RULE_CHATBOT_TRANSPARENCY]
        engine = RiskAssessmentEngine(rules=custom_rules)
        
        assert len(engine.rules) == 2
        
        answers = {"system_purpose": "social_scoring"}
        risk_level, results = engine.evaluate_assessment(answers)
        
        # Social scoring rule not in custom set, so should be minimal
        assert risk_level == RiskLevel.MINIMAL


# ============================================================================
# Integration-style tests
# ============================================================================

class TestRealWorldScenarios:
    """Test realistic assessment scenarios."""
    
    def test_customer_service_chatbot(self):
        """Test typical customer service chatbot."""
        engine = RiskAssessmentEngine()
        
        answers = {
            "system_type": "chatbot",
            "system_purpose": "customer_service",
            "uses_biometric_identification": False,
            "uses_manipulation": False,
            "processes_personal_data": True,
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        # Should be limited risk (chatbot transparency)
        assert risk_level == RiskLevel.LIMITED
        
        report = engine.generate_report(risk_level, results)
        assert "transparency" in report["compliance_summary"].lower()
    
    def test_loan_approval_system(self):
        """Test AI system for loan approvals."""
        engine = RiskAssessmentEngine()
        
        answers = {
            "system_purpose": "credit_scoring",
            "automated_decision_making": True,
            "processes_financial_data": True,
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        # Should be high risk
        assert risk_level == RiskLevel.HIGH
        
        report = engine.generate_report(risk_level, results)
        assert "strict requirements" in report["compliance_summary"].lower()
    
    def test_medical_diagnosis_assistant(self):
        """Test AI for medical diagnosis."""
        engine = RiskAssessmentEngine()
        
        # Medical diagnosis is not explicitly in current rules
        # but would be high-risk in real implementation
        answers = {
            "system_purpose": "medical_diagnosis",
            "safety_critical": True,
        }
        
        risk_level, results = engine.evaluate_assessment(answers)
        
        # Currently would be minimal (no specific rule)
        # This shows extensibility - can add medical rules later
        assert risk_level == RiskLevel.MINIMAL