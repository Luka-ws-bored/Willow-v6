"""
Prompt Checker Plugin for Willow v6

This plugin checks prompts for clarity, bias, and optimization suggestions.
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def check_clarity(prompt_text: str) -> Dict[str, List[str]]:
    """
    Check prompt for clarity issues.
    
    Args:
        prompt_text: Prompt to analyze
        
    Returns:
        Dictionary of clarity issues found
    """
    issues = {
        'vague_terms': [],
        'ambiguous_instructions': [],
        'missing_context': [],
        'length_issues': []
    }
    
    # Check for vague terms
    vague_terms = [
        'good', 'bad', 'better', 'worse', 'appropriate', 'suitable',
        'relevant', 'important', 'significant', 'proper', 'correct'
    ]
    
    for term in vague_terms:
        if re.search(rf'\b{term}\b', prompt_text.lower()):
            issues['vague_terms'].append(f"Vague term: '{term}' - consider being more specific")
    
    # Check for ambiguous instructions
    ambiguous_patterns = [
        (r'be\s+creative', 'Vague instruction: "be creative" - specify what type of creativity'),
        (r'write\s+well', 'Vague instruction: "write well" - specify style, tone, or format'),
        (r'make\s+it\s+good', 'Vague instruction: "make it good" - define what "good" means'),
    ]
    
    for pattern, message in ambiguous_patterns:
        if re.search(pattern, prompt_text.lower()):
            issues['ambiguous_instructions'].append(message)
    
    # Check for missing context
    if len(prompt_text.split()) < 10:
        issues['missing_context'].append("Prompt may be too short - consider adding more context")
    
    # Check length
    word_count = len(prompt_text.split())
    if word_count > 500:
        issues['length_issues'].append("Prompt is very long - consider breaking it into smaller parts")
    elif word_count < 5:
        issues['length_issues'].append("Prompt is very short - may need more detail")
    
    return issues


def check_bias(prompt_text: str) -> Dict[str, List[str]]:
    """
    Check prompt for potential bias.
    
    Args:
        prompt_text: Prompt to analyze
        
    Returns:
        Dictionary of bias issues found
    """
    issues = {
        'gender_bias': [],
        'cultural_bias': [],
        'stereotyping': [],
        'exclusionary_language': []
    }
    
    # Check for gender bias
    gender_patterns = [
        (r'\bhe\b', 'Consider using gender-neutral language'),
        (r'\bshe\b', 'Consider using gender-neutral language'),
        (r'\bhis\b', 'Consider using gender-neutral language'),
        (r'\bher\b', 'Consider using gender-neutral language'),
    ]
    
    for pattern, message in gender_patterns:
        if re.search(pattern, prompt_text.lower()):
            issues['gender_bias'].append(message)
    
    # Check for cultural bias
    cultural_patterns = [
        (r'western\s+standards', 'May assume Western cultural context'),
        (r'american\s+way', 'May assume American cultural context'),
        (r'traditional\s+values', 'May assume specific cultural values'),
    ]
    
    for pattern, message in cultural_patterns:
        if re.search(pattern, prompt_text.lower()):
            issues['cultural_bias'].append(message)
    
    # Check for stereotyping
    stereotype_patterns = [
        (r'all\s+\w+\s+are', 'Avoid generalizations and stereotypes'),
        (r'typical\s+\w+', 'May reinforce stereotypes'),
        (r'normal\s+\w+', 'May exclude diverse perspectives'),
    ]
    
    for pattern, message in stereotype_patterns:
        if re.search(pattern, prompt_text.lower()):
            issues['stereotyping'].append(message)
    
    return issues


def suggest_improvements(clarity_issues: Dict[str, List[str]], bias_issues: Dict[str, List[str]]) -> List[str]:
    """
    Generate improvement suggestions based on analysis.
    
    Args:
        clarity_issues: Clarity analysis results
        bias_issues: Bias analysis results
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    # Clarity suggestions
    if clarity_issues['vague_terms']:
        suggestions.append("Replace vague terms with specific, measurable criteria")
    
    if clarity_issues['ambiguous_instructions']:
        suggestions.append("Provide clear, actionable instructions")
    
    if clarity_issues['missing_context']:
        suggestions.append("Add relevant context and background information")
    
    if clarity_issues['length_issues']:
        suggestions.append("Adjust prompt length for optimal clarity")
    
    # Bias suggestions
    if bias_issues['gender_bias']:
        suggestions.append("Use gender-neutral language throughout")
    
    if bias_issues['cultural_bias']:
        suggestions.append("Consider diverse cultural perspectives")
    
    if bias_issues['stereotyping']:
        suggestions.append("Avoid generalizations and stereotypes")
    
    if bias_issues['exclusionary_language']:
        suggestions.append("Use inclusive language that welcomes diverse perspectives")
    
    return suggestions


def calculate_score(clarity_issues: Dict[str, List[str]], bias_issues: Dict[str, List[str]]) -> Tuple[int, str]:
    """
    Calculate overall prompt quality score.
    
    Args:
        clarity_issues: Clarity analysis results
        bias_issues: Bias analysis results
        
    Returns:
        Tuple of (score, grade)
    """
    total_issues = sum(len(issues) for issues in clarity_issues.values()) + \
                   sum(len(issues) for issues in bias_issues.values())
    
    if total_issues == 0:
        return 100, "A+"
    elif total_issues <= 2:
        return 85, "A"
    elif total_issues <= 4:
        return 75, "B"
    elif total_issues <= 6:
        return 65, "C"
    elif total_issues <= 8:
        return 55, "D"
    else:
        return 45, "F"


def run_prompt_checker(prompt_text: str) -> str:
    """
    Check prompts for clarity, bias, and optimization suggestions.
    
    Args:
        prompt_text: Prompt to analyze
        
    Returns:
        Analysis report with findings and suggestions
    """
    logger.info("Running prompt checker.")
    
    if not prompt_text.strip():
        return "No prompt provided for analysis."
    
    # Analyze clarity
    clarity_issues = check_clarity(prompt_text)
    
    # Analyze bias
    bias_issues = check_bias(prompt_text)
    
    # Calculate score
    score, grade = calculate_score(clarity_issues, bias_issues)
    
    # Generate suggestions
    suggestions = suggest_improvements(clarity_issues, bias_issues)
    
    # Build report
    report = "🔍 Prompt Checker Analysis Report:\n\n"
    report += f"Overall Score: {score}/100 ({grade})\n\n"
    
    # Clarity section
    total_clarity_issues = sum(len(issues) for issues in clarity_issues.values())
    if total_clarity_issues > 0:
        report += "📝 Clarity Issues:\n"
        for category, issues in clarity_issues.items():
            if issues:
                report += f"  • {category.replace('_', ' ').title()}:\n"
                for issue in issues:
                    report += f"    - {issue}\n"
        report += "\n"
    
    # Bias section
    total_bias_issues = sum(len(issues) for issues in bias_issues.values())
    if total_bias_issues > 0:
        report += "⚖️ Bias Issues:\n"
        for category, issues in bias_issues.items():
            if issues:
                report += f"  • {category.replace('_', ' ').title()}:\n"
                for issue in issues:
                    report += f"    - {issue}\n"
        report += "\n"
    
    # Suggestions
    if suggestions:
        report += "💡 Improvement Suggestions:\n"
        for suggestion in suggestions:
            report += f"• {suggestion}\n"
    
    if total_clarity_issues == 0 and total_bias_issues == 0:
        report += "\n✅ Excellent! Your prompt is clear and unbiased."
    
    return report


# Entry point for plugin loader
def run(input_text: str) -> str:
    """
    Main entry point for the prompt checker plugin.
    
    Args:
        input_text: Prompt text to analyze
        
    Returns:
        Analysis result
    """
    return run_prompt_checker(input_text) 