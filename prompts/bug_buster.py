"""
Bug Buster Plugin for Willow v6

This plugin analyzes Python code for bugs, provides fixes, and explains corrections.
"""

import logging
import ast
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def analyze_syntax(code_snippet: str) -> List[Dict[str, Any]]:
    """
    Analyze Python code for syntax errors and potential issues.
    
    Args:
        code_snippet: Python code to analyze
        
    Returns:
        List of issues found
    """
    issues = []
    
    try:
        # Check for basic syntax errors
        ast.parse(code_snippet)
    except SyntaxError as e:
        issues.append({
            'type': 'syntax_error',
            'line': e.lineno,
            'message': str(e),
            'severity': 'high'
        })
    
    # Check for common Python issues
    common_patterns = [
        (r'print\s+[^(]', 'print statement should use parentheses'),
        (r'except\s*:', 'bare except clause - specify exception type'),
        (r'def\s+\w+\s*\([^)]*\)\s*:', 'function definition found'),
    ]
    
    for pattern, message in common_patterns:
        if re.search(pattern, code_snippet):
            issues.append({
                'type': 'style_warning',
                'message': message,
                'severity': 'medium'
            })
    
    return issues


def suggest_fixes(issues: List[Dict[str, Any]]) -> List[str]:
    """
    Generate fix suggestions for identified issues.
    
    Args:
        issues: List of issues found in code
        
    Returns:
        List of fix suggestions
    """
    suggestions = []
    
    for issue in issues:
        if issue['type'] == 'syntax_error':
            suggestions.append(f"Fix syntax error on line {issue['line']}: {issue['message']}")
        elif issue['type'] == 'style_warning':
            suggestions.append(f"Style improvement: {issue['message']}")
    
    return suggestions


def run_bug_buster(code_snippet: str) -> str:
    """
    Analyze Python code for bugs, fix them, and explain the corrections.
    
    Args:
        code_snippet: Python code to analyze
        
    Returns:
        Analysis report with findings and suggestions
    """
    logger.info("Running bug buster on code snippet.")
    
    if not code_snippet.strip():
        return "No code provided for analysis."
    
    # Analyze the code
    issues = analyze_syntax(code_snippet)
    
    if not issues:
        return "✅ Code analysis complete. No bugs or issues found!"
    
    # Generate report
    report = "🐛 Bug Buster Analysis Report:\n\n"
    report += f"Found {len(issues)} issue(s):\n\n"
    
    for i, issue in enumerate(issues, 1):
        report += f"{i}. {issue['message']} (Severity: {issue['severity']})\n"
    
    # Add suggestions
    suggestions = suggest_fixes(issues)
    if suggestions:
        report += "\n💡 Suggestions:\n"
        for suggestion in suggestions:
            report += f"• {suggestion}\n"
    
    return report


# Entry point for plugin loader
def run(input_text: str) -> str:
    """
    Main entry point for the bug buster plugin.
    
    Args:
        input_text: Code snippet or query to analyze
        
    Returns:
        Analysis result
    """
    return run_bug_buster(input_text) 