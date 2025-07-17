#!/usr/bin/env python3
"""
Troubleshooting AI for Python Scripts
=====================================

This script automatically detects, analyzes, and provides fixes for common Python errors.
It can be used to troubleshoot any Python file and generate detailed fix reports.

Author: AI Assistant
Date: 2025-07-17
"""

import ast
import sys
import os
import re
import json
import traceback
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import subprocess


class PythonTroubleshooter:
    """AI-powered Python script troubleshooter"""
    
    def __init__(self):
        self.errors_found = []
        self.warnings_found = []
        self.suggestions = []
        
    def analyze_file(self, file_path: str) -> Dict:
        """Comprehensive analysis of a Python file"""
        results = {
            'file_path': file_path,
            'syntax_errors': [],
            'import_errors': [],
            'encoding_issues': [],
            'style_issues': [],
            'potential_runtime_errors': [],
            'suggestions': [],
            'fix_applied': False
        }
        
        if not os.path.exists(file_path):
            results['syntax_errors'].append(f"File not found: {file_path}")
            return results
            
        # Check file encoding
        encoding_result = self._check_encoding(file_path)
        if encoding_result:
            results['encoding_issues'].append(encoding_result)
            
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                results['encoding_issues'].append("File uses non-UTF-8 encoding")
            except Exception as e:
                results['syntax_errors'].append(f"Cannot read file: {e}")
                return results
                
        # Syntax analysis
        syntax_result = self._check_syntax(content, file_path)
        if syntax_result:
            results['syntax_errors'].extend(syntax_result)
            
        # Import analysis
        import_result = self._check_imports(content)
        if import_result:
            results['import_errors'].extend(import_result)
            
        # Style and potential issues
        style_result = self._check_style_issues(content)
        if style_result:
            results['style_issues'].extend(style_result)
            
        # Runtime error prediction
        runtime_result = self._predict_runtime_errors(content)
        if runtime_result:
            results['potential_runtime_errors'].extend(runtime_result)
            
        # Generate suggestions
        results['suggestions'] = self._generate_suggestions(results)
        
        return results
    
    def _check_encoding(self, file_path: str) -> Optional[str]:
        """Check for encoding issues"""
        try:
            with open(file_path, 'rb') as f:
                raw_content = f.read()
                
            # Check for BOM
            if raw_content.startswith(b'\xef\xbb\xbf'):
                return "File contains UTF-8 BOM which may cause issues"
                
            # Check for mixed line endings
            if b'\r\n' in raw_content and b'\n' in raw_content:
                return "File contains mixed line endings (CRLF and LF)"
                
        except Exception:
            return "Could not check file encoding"
            
        return None
    
    def _check_syntax(self, content: str, file_path: str) -> List[str]:
        """Check for syntax errors"""
        errors = []
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            error_msg = f"Syntax Error at line {e.lineno}: {e.msg}"
            if e.text:
                error_msg += f"\n  Code: {e.text.strip()}"
            errors.append(error_msg)
            
            # Specific checks for common issues
            if "unterminated" in str(e.msg).lower():
                errors.append("SPECIFIC FIX: Check for unclosed quotes, parentheses, or brackets")
            elif "invalid syntax" in str(e.msg).lower():
                errors.append("SPECIFIC FIX: Check for typos, missing colons, or incorrect indentation")
                
        except Exception as e:
            errors.append(f"Parse error: {e}")
            
        return errors
    
    def _check_imports(self, content: str) -> List[str]:
        """Check for import-related issues"""
        errors = []
        
        # Extract import statements
        import_pattern = r'^(?:from\s+\S+\s+)?import\s+.+$'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        
        for imp in imports:
            # Check for common problematic imports
            if 'selenium' in imp.lower() and 'webdriver' in imp.lower():
                errors.append("Selenium detected: Ensure ChromeDriver is in PATH or specify driver path")
            elif 'requests' in imp.lower():
                errors.append("Requests detected: Ensure network connectivity for web requests")
                
        return errors
    
    def _check_style_issues(self, content: str) -> List[str]:
        """Check for style and formatting issues"""
        issues = []
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for very long lines
            if len(line) > 120:
                issues.append(f"Line {i}: Very long line ({len(line)} characters)")
                
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(f"Line {i}: Trailing whitespace")
                
            # Check for mixed tabs and spaces
            if '\t' in line and '    ' in line:
                issues.append(f"Line {i}: Mixed tabs and spaces")
                
        return issues
    
    def _predict_runtime_errors(self, content: str) -> List[str]:
        """Predict potential runtime errors"""
        warnings = []
        
        # Check for common runtime error patterns
        if 'driver.get(' in content and 'WebDriverWait' not in content:
            warnings.append("Selenium usage without explicit waits may cause timing issues")
            
        if 'time.sleep(' in content:
            warnings.append("Hard-coded sleep statements may cause unreliable timing")
            
        if 'except:' in content or 'except Exception:' in content:
            warnings.append("Broad exception handling may hide important errors")
            
        return warnings
    
    def _generate_suggestions(self, results: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        if results['syntax_errors']:
            suggestions.append("Fix syntax errors first before running the script")
            
        if results['encoding_issues']:
            suggestions.append("Consider saving file with UTF-8 encoding without BOM")
            
        if results['import_errors']:
            suggestions.append("Install missing dependencies using pip")
            
        if results['style_issues']:
            suggestions.append("Consider using a code formatter like black or autopep8")
            
        if results['potential_runtime_errors']:
            suggestions.append("Add proper error handling and use explicit waits for web automation")
            
        return suggestions
    
    def generate_fix_report(self, file_path: str) -> str:
        """Generate a comprehensive fix report"""
        results = self.analyze_file(file_path)
        
        report = f"""
PYTHON SCRIPT TROUBLESHOOTING REPORT
====================================

File: {file_path}
Analysis Date: 2025-07-17
Analyzed by: AI Troubleshooting Assistant

EXECUTIVE SUMMARY
-----------------
"""
        
        total_issues = (len(results['syntax_errors']) + 
                       len(results['import_errors']) + 
                       len(results['encoding_issues']) + 
                       len(results['style_issues']) + 
                       len(results['potential_runtime_errors']))
        
        if total_issues == 0:
            report += "✅ No critical issues found. Script appears to be syntactically correct.\n"
        else:
            report += f"⚠️  Found {total_issues} issues that need attention.\n"
        
        # Detailed findings
        if results['syntax_errors']:
            report += "\n🔴 CRITICAL SYNTAX ERRORS\n"
            report += "-" * 25 + "\n"
            for error in results['syntax_errors']:
                report += f"• {error}\n"
        
        if results['import_errors']:
            report += "\n🟡 IMPORT ISSUES\n"
            report += "-" * 15 + "\n"
            for error in results['import_errors']:
                report += f"• {error}\n"
        
        if results['encoding_issues']:
            report += "\n🟠 ENCODING ISSUES\n"
            report += "-" * 17 + "\n"
            for issue in results['encoding_issues']:
                report += f"• {issue}\n"
        
        if results['style_issues']:
            report += "\n🔵 STYLE ISSUES\n"
            report += "-" * 15 + "\n"
            for issue in results['style_issues'][:10]:  # Limit to first 10
                report += f"• {issue}\n"
            if len(results['style_issues']) > 10:
                report += f"... and {len(results['style_issues']) - 10} more style issues\n"
        
        if results['potential_runtime_errors']:
            report += "\n🟣 POTENTIAL RUNTIME ISSUES\n"
            report += "-" * 27 + "\n"
            for warning in results['potential_runtime_errors']:
                report += f"• {warning}\n"
        
        # Suggestions
        if results['suggestions']:
            report += "\n💡 RECOMMENDATIONS\n"
            report += "-" * 18 + "\n"
            for suggestion in results['suggestions']:
                report += f"• {suggestion}\n"
        
        return report


def main():
    """Main function to run troubleshooting"""
    if len(sys.argv) != 2:
        print("Usage: python troubleshooting_ai.py <python_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    troubleshooter = PythonTroubleshooter()
    
    print("🤖 AI Troubleshooting Assistant Starting...")
    print(f"📁 Analyzing: {file_path}")
    print("-" * 50)
    
    report = troubleshooter.generate_fix_report(file_path)
    print(report)
    
    # Save report to file
    report_file = f"{Path(file_path).stem}_troubleshooting_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: {report_file}")


if __name__ == "__main__":
    main()
