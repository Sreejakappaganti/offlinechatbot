"""Test all the fixed scenarios"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.hybrid_chatbot import HybridChatbot
from core.data_analyzer import DataAnalyzer

print("=" * 80)
print("TESTING ALL FIXED SCENARIOS")
print("=" * 80)

# Initialize and load PDF
chatbot = HybridChatbot(vector_store=None, llm_client=None)
pdf_path = "data/documents/sales_data_100_rows.pdf"
chatbot.load_document(pdf_path)

if chatbot.current_dataframe is None:
    print("❌ Failed to load data!")
    exit(1)

analyzer = DataAnalyzer(chatbot.current_dataframe)

# Test scenarios from screenshots
test_queries = [
    ("what is the total sales of orderID 2", "3600", "VALUE LOOKUP"),
    ("what is the average sales of first 10 orders", "Should average only first 10", "AVERAGE"),
    ("what is the average sales of t-shirts", "Should filter to T-Shirt product", "AVERAGE"),
    ("which region have the most sales", "Should show region with highest total", "GROUP ANALYSIS"),
    ("what is the average sales of each product", "Should group by product", "GROUP ANALYSIS"),
    ("which salesperson sold the highest sales", "Should show salesperson with highest sales", "GROUP ANALYSIS"),
    ("who sold the most", "Should identify top salesperson", "GROUP ANALYSIS"),
    ("what is the sum of sales between 1000 and 5000", "Should filter range and sum", "SUM"),
    ("average sales from order 1 to 20", "Should filter first 20 and average", "AVERAGE"),
    ("which product has the lowest sales", "Should show product with minimum total", "GROUP ANALYSIS"),
]

print(f"\n✅ Data loaded: {len(chatbot.current_dataframe)} rows\n")

for query, expected, expected_op in test_queries:
    print("=" * 80)
    print(f"Query: {query}")
    print(f"Expected: {expected}")
    print("-" * 80)
    
    result = analyzer.analyze(query)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        operation = result.get('operation', 'N/A')
        print(f"✓ Operation: {operation}")
        
        if 'result' in result:
            print(f"  Result: {result['result']}")
        if 'sample_size' in result:
            print(f"  Sample Size: {result['sample_size']} records")
        if 'results' in result:
            print(f"  Results by {result.get('group_by', 'Category')}:")
            for k, v in list(result['results'].items())[:3]:  # Show first 3
                print(f"    • {k}: {v}")
        if 'answer' in result:
            print(f"  Answer: {result['answer']}")
        if 'all_groups' in result:
            print(f"  Top 3 groups:")
            for k, v in list(sorted(result['all_groups'].items(), key=lambda x: x[1], reverse=True))[:3]:
                print(f"    • {k}: {v}")
    
    print()

print("=" * 80)
