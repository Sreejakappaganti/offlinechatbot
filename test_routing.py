"""Test query routing logic"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import classify_query_type

print("=" * 80)
print("TESTING QUERY ROUTING LOGIC")
print("=" * 80)

# Test cases: (query, has_tabular_data, expected_result)
test_cases = [
    # Document retrieval queries (PPT/PDF/Word)
    ("what is the title of project", False, "document_retrieval"),
    ("what is the title of project", True, "document_retrieval"),  # Should still be doc even with table
    ("summarize the document", False, "document_retrieval"),
    ("summarize the document", True, "document_retrieval"),
    ("who is the author", False, "document_retrieval"),
    ("who is the author", True, "document_retrieval"),
    ("explain the topic", False, "document_retrieval"),
    ("describe the project", True, "document_retrieval"),
    
    # Data analysis queries (only when tabular data exists)
    ("what is the average sales", False, "document_retrieval"),  # No table = doc retrieval
    ("what is the average sales", True, "data_analysis"),        # Has table = data analysis
    ("which region has most sales", False, "document_retrieval"),
    ("which region has most sales", True, "data_analysis"),
    ("total sales of orderID 2", False, "document_retrieval"),
    ("total sales of orderID 2", True, "data_analysis"),
    ("average of first 10 orders", True, "data_analysis"),
    ("which salesperson sold highest", True, "data_analysis"),
    ("sum of all records", True, "data_analysis"),
    ("count the items", True, "data_analysis"),
]

print(f"\nRunning {len(test_cases)} test cases...\n")

passed = 0
failed = 0

for query, has_table, expected in test_cases:
    result = classify_query_type(query, has_table)
    status = "✓" if result == expected else "✗"
    
    if result == expected:
        passed += 1
    else:
        failed += 1
        
    table_status = "WITH table" if has_table else "NO table"
    print(f"{status} [{table_status}] '{query[:40]}...'")
    print(f"   Expected: {expected}, Got: {result}")
    if result != expected:
        print(f"   ❌ FAILED!")
    print()

print("=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 80)

if failed == 0:
    print("\n🎉 All tests passed! Routing logic is working correctly.")
else:
    print(f"\n⚠️ {failed} tests failed. Please review the routing logic.")
