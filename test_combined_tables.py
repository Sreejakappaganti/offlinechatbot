"""Test combined table loading"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.hybrid_chatbot import HybridChatbot
from core.data_analyzer import DataAnalyzer

print("=" * 80)
print("TESTING COMBINED TABLE LOADING")
print("=" * 80)

# Initialize chatbot
chatbot = HybridChatbot(vector_store=None, llm_client=None)

# Load the PDF
pdf_path = "data/documents/sales_data_100_rows.pdf"
result = chatbot.load_document(pdf_path)

print("\n" + "=" * 80)
print("DATAFRAME INFO")
print("=" * 80)

if chatbot.current_dataframe is not None:
    df = chatbot.current_dataframe
    print(f"Total Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    if 'Order_ID' in df.columns:
        print(f"\nOrder_ID Statistics:")
        print(f"  Min: {df['Order_ID'].min()}")
        print(f"  Max: {df['Order_ID'].max()}")
        print(f"  Unique: {df['Order_ID'].nunique()}")
        print(f"  Expected: 100")
        
        # Check for duplicates
        duplicates = df['Order_ID'].duplicated().sum()
        print(f"  Duplicates: {duplicates}")
        
        # Show first, middle, and last records
        print(f"\nFirst record (ID=1):")
        print(df[df['Order_ID'] == 1])
        
        print(f"\nMiddle record (ID=50):")
        print(df[df['Order_ID'] == 50])
        
        print(f"\nLast record (ID=100):")
        print(df[df['Order_ID'] == 100])

# Now test queries
print("\n" + "=" * 80)
print("TESTING QUERIES")
print("=" * 80)

if chatbot.current_dataframe is not None:
    analyzer = DataAnalyzer(chatbot.current_dataframe)
    
    test_queries = [
        "what is the total sales of orderID 2",
        "what is the total sales of orderID 50",
        "what is the total sales of order 100",
        "what is the average total sales"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('-'*60)
        result = analyzer.analyze(query)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            if 'suggestion' in result:
                print(f"   {result['suggestion']}")
        else:
            print(f"✅ Operation: {result.get('operation', 'N/A')}")
            print(f"   Result: {result.get('result', 'N/A')}")
            if 'details' in result and result.get('query_type') == 'specific_row':
                print(f"   Product: {result['details'].get('Product', 'N/A')}")
                print(f"   Region: {result['details'].get('Region', 'N/A')}")
