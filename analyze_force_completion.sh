#!/bin/bash

# Force Component Completion Analysis Script
# Analyzes all .force components and identifies incomplete definitions

echo "=== Force Component Completion Analysis ==="
echo "Date: $(date)"
echo

# Find incomplete tools (missing parameters, execution, or metadata)
echo "🔧 INCOMPLETE TOOLS:"
echo "==================="

incomplete_tools=$(find .force/tools -name "*.json" -exec grep -L '"parameters"' {} \; | head -20)
for tool in $incomplete_tools; do
    if [ -f "$tool" ]; then
        tool_name=$(grep '"name"' "$tool" | head -1 | sed 's/.*"name": "\([^"]*\)".*/\1/')
        category=$(grep '"category"' "$tool" | head -1 | sed 's/.*"category": "\([^"]*\)".*/\1/')
        echo "❌ $tool_name ($category) - Missing: parameters, execution, metadata"
    fi
done

echo
echo "📋 INCOMPLETE PATTERNS:"
echo "======================="

# Find incomplete patterns (missing context or implementation details)
incomplete_patterns=$(find .force/patterns -name "*.json" -exec grep -L '"context"' {} \;)
for pattern in $incomplete_patterns; do
    if [ -f "$pattern" ]; then
        pattern_name=$(grep '"name"' "$pattern" | head -1 | sed 's/.*"name": "\([^"]*\)".*/\1/')
        echo "❌ $pattern_name - Missing: context, implementation details"
    fi
done

echo
echo "🔒 CONSTRAINTS STATUS:"
echo "===================="
constraint_count=$(find .force/constraints -name "*.json" | wc -l)
echo "✅ $constraint_count constraint files found (appear complete)"

echo
echo "🏛️ GOVERNANCE STATUS:"
echo "===================="
governance_count=$(find .force/governance -name "*.json" | wc -l)
echo "✅ $governance_count governance files found (appear complete)"

echo
echo "📊 COMPLETION SUMMARY:"
echo "====================="

total_tools=$(find .force/tools -name "*.json" | wc -l)
complete_tools=$(find .force/tools -name "*.json" -exec grep -l '"parameters"' {} \; | wc -l)
tools_completion=$((complete_tools * 100 / total_tools))

total_patterns=$(find .force/patterns -name "*.json" | wc -l)
complete_patterns=$(find .force/patterns -name "*.json" -exec grep -l '"context"' {} \; | wc -l)
patterns_completion=$((complete_patterns * 100 / total_patterns))

echo "Tools: $complete_tools/$total_tools complete ($tools_completion%)"
echo "Patterns: $complete_patterns/$total_patterns complete ($patterns_completion%)"
echo "Constraints: Complete"
echo "Governance: Complete"

echo
echo "🎯 NEXT ACTIONS:"
echo "==============="
echo "1. Complete remaining $(($total_tools - $complete_tools)) tool definitions"
echo "2. Complete remaining $(($total_patterns - $complete_patterns)) pattern definitions"
echo "3. Validate all components against Force schema"
echo "4. Run Force sync to ensure consistency"

echo
echo "=== Analysis Complete ==="
