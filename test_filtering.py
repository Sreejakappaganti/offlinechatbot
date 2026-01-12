"""
Test the improved filtering logic
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.data_analyzer import DataAnalyzer
import pandas as pd

# Create test data similar to sales data
df = pd.DataFrame({
    'Order_ID': [1, 2, 3, 4, 5],
    'Product': ['A', 'B', 'C', 'D', 'E'],
    'Total_Sales': [1000.50, 2500.75, 3000.00, 1500.25, 2000.00],
    'Quantity': [10, 25, 30, 15, 20],
    'Region': ['North', 'South', 'North', 'South', 'North']
})

print("Test Data:")
print(df)
print("\n" + "="*60)

analyzer = DataAnalyzer(df)

# Test queries
test_queries = [
    "What is the total sales of orderID 2?",
    "What is the total sales of order 2?",
    "What is the sum of Total_Sales for order ID 3?",
    "What is the average Total_Sales?",
    "What is the total sales in the North region?",
]

for query in test_queries:
    print(f"\nQuery: {query}")
    print("-" * 60)
    result = analyzer.analyze(query)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"Operation: {result.get('operation', 'N/A')}")
        print(f"Result: {result.get('result', 'N/A')}")
        if 'sample_size' in result:
            print(f"Sample Size: {result['sample_size']}")
        if 'details' in result:
            print(f"Details: {result['details']}")
    print("="*60)
