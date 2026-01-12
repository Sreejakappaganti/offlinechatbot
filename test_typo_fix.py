"""Quick test for the specific row fix"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.table_extractor import TableExtractor
from core.data_analyzer import DataAnalyzer
import pandas as pd

# Create test data matching the PDF structure
test_data = {
    'Order_ID': [1, 2, 3, 4, 5],
    'Product': ['A', 'B', 'C', 'D', 'E'],
    'Total_Sales': [1000, 3600, 5000, 2000, 4000],
    'Region': ['North', 'East', 'West', 'South', 'North']
}

df = pd.DataFrame(test_data)
analyzer = DataAnalyzer(df)

print("=" * 80)
print("TESTING SPECIFIC ROW DETECTION")
print("=" * 80)

# Test queries
test_queries = [
    "what is the total sales of orderID 2",     # Correct spelling
    "what is the total sales of oederID 2",     # Typo (like in screenshot)
    "what is the total sales of order 2",
    "what is the total sales of oeder 2",       # Typo
    "what is the total sales in East region",   # Should return 3600 (only 1 record)
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('-'*60)
    
    result = analyzer.analyze(query)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        operation = result.get('operation', 'N/A')
        res = result.get('result', 'N/A')
        
        if operation == 'VALUE LOOKUP':
            print(f"✅ Operation: {operation}")
            print(f"   Result: {res}")
            print(f"   Expected: 3600")
            if res == 3600:
                print(f"   ✓ CORRECT!")
            else:
                print(f"   ✗ WRONG!")
        else:
            print(f"⚠️  Operation: {operation}")
            print(f"   Result: {res}")
            if 'sample_size' in result:
                print(f"   Sample Size: {result['sample_size']}")

print("\n" + "=" * 80)
