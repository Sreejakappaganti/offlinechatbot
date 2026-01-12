"""Test script to debug the actual PDF data extraction and filtering"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.table_extractor import TableExtractor
from core.data_analyzer import DataAnalyzer

# Path to the actual PDF
pdf_path = "data/documents/sales_data_100_rows.pdf"

if not os.path.exists(pdf_path):
    print(f"❌ PDF not found: {pdf_path}")
    print("Available files in data/documents/:")
    if os.path.exists("data/documents/"):
        for file in os.listdir("data/documents/"):
            print(f"  - {file}")
    sys.exit(1)

print("=" * 60)
print("EXTRACTING TABLES FROM PDF")
print("=" * 60)

cache_dir = "data/vector_store"
extractor = TableExtractor(cache_dir)
tables = extractor.extract_tables(pdf_path)

print(f"\n✅ Extracted {len(tables)} table(s)")

if not tables:
    print("❌ No tables found!")
    sys.exit(1)

# Use the largest table (most likely the main data)
main_table = max(tables, key=lambda df: len(df))
print(f"\nMain table: {len(main_table)} rows × {len(main_table.columns)} columns")
print(f"Columns: {list(main_table.columns)}")

# Show first few rows
print("\nFirst 5 rows:")
print(main_table.head())

# Check for Order_ID = 2
print("\n" + "=" * 60)
print("CHECKING ORDER_ID = 2")
print("=" * 60)

if 'Order_ID' in main_table.columns:
    print(f"\nOrder_ID range: {main_table['Order_ID'].min()} to {main_table['Order_ID'].max()}")
    print(f"Unique Order_IDs: {sorted(main_table['Order_ID'].unique())}")
    
    order_2_data = main_table[main_table['Order_ID'] == 2]
    print(f"\nRecords with Order_ID = 2: {len(order_2_data)}")
    if len(order_2_data) > 0:
        print(order_2_data)
    else:
        print("⚠️ No record with Order_ID = 2 exists!")
        print("\nLet's check Order_ID = 36 (first row):")
        order_36_data = main_table[main_table['Order_ID'] == 36]
        print(order_36_data)
else:
    # Try to find ID column
    id_cols = [col for col in main_table.columns if 'id' in col.lower() or 'order' in col.lower()]
    print(f"Possible ID columns: {id_cols}")
    if id_cols:
        print(f"\nFirst column ({id_cols[0]}) sample values:")
        print(main_table[id_cols[0]].head(10))

# Now test the analyzer
print("\n" + "=" * 60)
print("TESTING DATA ANALYZER")
print("=" * 60)

analyzer = DataAnalyzer(main_table)

# Test 1: Invalid ID
query = "what is the total sales of orderID 2"
print(f"\nQuery: {query}")
print("-" * 60)

result = analyzer.analyze(query)
print(f"\nOperation: {result.get('operation', 'N/A')}")
print(f"Result: {result.get('result', 'N/A')}")
if 'error' in result:
    print(f"❌ Error: {result['error']}")
    if 'suggestion' in result:
        print(f"   Suggestion: {result['suggestion']}")

# Test 2: Valid ID (36)
print("\n" + "=" * 60)
query2 = "what is the total sales of orderID 36"
print(f"\nQuery: {query2}")
print("-" * 60)

result2 = analyzer.analyze(query2)
print(f"\nOperation: {result2.get('operation', 'N/A')}")
print(f"Result: {result2.get('result', 'N/A')}")
if 'error' in result2:
    print(f"❌ Error: {result2['error']}")
if 'details' in result2:
    print(f"Details: {result2['details']}")

# Test 3: Another valid ID (40)
print("\n" + "=" * 60)
query3 = "what is the total sales of order 40"
print(f"\nQuery: {query3}")
print("-" * 60)

result3 = analyzer.analyze(query3)
print(f"\nOperation: {result3.get('operation', 'N/A')}")
print(f"Result: {result3.get('result', 'N/A')}")
if 'error' in result3:
    print(f"❌ Error: {result3['error']}")
if 'details' in result3:
    print(f"Details: {result3['details']}")

# Check what the total sum is
if 'Total_Sales' in main_table.columns:
    total_sum = main_table['Total_Sales'].sum()
    print(f"\n📊 Total sum of all records: {total_sum}")
