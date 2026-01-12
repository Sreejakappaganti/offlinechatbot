"""Debug script to check ALL tables from the PDF"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.table_extractor import TableExtractor

pdf_path = "data/documents/sales_data_100_rows.pdf"

if not os.path.exists(pdf_path):
    print(f"❌ PDF not found: {pdf_path}")
    sys.exit(1)

print("=" * 80)
print("EXTRACTING ALL TABLES FROM PDF")
print("=" * 80)

cache_dir = "data/vector_store"
extractor = TableExtractor(cache_dir)

# Clear cache to force re-extraction
import shutil
cache_file = os.path.join(cache_dir, "sales_data_100_rows.pkl")
if os.path.exists(cache_file):
    os.remove(cache_file)
    print("✓ Cleared cache - forcing fresh extraction\n")

tables = extractor.extract_tables(pdf_path)

print(f"\n✅ Extracted {len(tables)} table(s)\n")

# Inspect EACH table
for idx, df in enumerate(tables, 1):
    print("=" * 80)
    print(f"TABLE {idx} of {len(tables)}")
    print("=" * 80)
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column Names: {list(df.columns)}")
    
    # Check for Order_ID column
    if 'Order_ID' in df.columns:
        print(f"\n✓ Found Order_ID column!")
        print(f"  Order_ID range: {df['Order_ID'].min()} to {df['Order_ID'].max()}")
        print(f"  Unique Order_IDs: {len(df['Order_ID'].unique())}")
        print(f"  Sample Order_IDs: {sorted(df['Order_ID'].unique())[:10]}")
    
    # Show first and last few rows
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    print(f"\nLast 3 rows:")
    print(df.tail(3))
    
    # Check for Order_ID = 2
    if 'Order_ID' in df.columns:
        order_2 = df[df['Order_ID'] == 2]
        print(f"\n🔍 Order_ID = 2: {len(order_2)} record(s)")
        if len(order_2) > 0:
            print(order_2)
    
    print("\n")

# Determine which table has the most complete data (1-100)
print("=" * 80)
print("SUMMARY")
print("=" * 80)

for idx, df in enumerate(tables, 1):
    if 'Order_ID' in df.columns:
        id_range = f"{df['Order_ID'].min()} to {df['Order_ID'].max()}"
        print(f"Table {idx}: {len(df)} rows, Order_ID range: {id_range}")
