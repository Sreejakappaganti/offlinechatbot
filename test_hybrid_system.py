"""
Test script for Hybrid RAG + Data Analysis
Tests table extraction, data analysis, and query routing
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.table_extractor import TableExtractor
from src.core.query_router import QueryRouter
from src.core.data_analyzer import DataAnalyzer
from src.core.config import TABULAR_DATA_DIR
import pandas as pd


def test_table_extraction():
    """Test table extraction from PDF"""
    print("\n" + "="*60)
    print("TEST 1: Table Extraction")
    print("="*60)
    
    extractor = TableExtractor(TABULAR_DATA_DIR)
    
    # Test with a sample PDF (you'll need to have one)
    pdf_files = list(Path("data/documents").glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️ No PDF files found in data/documents/")
        print("   Please add a PDF with tables to test this feature")
        return None
    
    pdf_path = str(pdf_files[0])
    print(f"\nTesting with: {pdf_path}")
    
    tables = extractor.extract_tables(pdf_path)
    
    if tables:
        print(f"✓ Extracted {len(tables)} table(s)")
        for i, df in enumerate(tables, 1):
            print(f"\n  Table {i}:")
            print(f"    Rows: {len(df)}")
            print(f"    Columns: {df.columns.tolist()}")
            print(f"    Sample data:")
            print(df.head(3).to_string(index=False))
        return tables[0]  # Return first table for further testing
    else:
        print("✗ No tables found")
        return None


def test_query_routing():
    """Test query classification"""
    print("\n" + "="*60)
    print("TEST 2: Query Routing")
    print("="*60)
    
    router = QueryRouter()
    
    test_queries = [
        ("What is the average sales?", "data_analysis"),
        ("Who is the CEO?", "document_retrieval"),
        ("Calculate the total revenue", "data_analysis"),
        ("Summarize the document", "document_retrieval"),
        ("Show me the top 5 products", "data_analysis"),
        ("What are the main points?", "document_retrieval"),
    ]
    
    print("\nQuery Classification Tests:")
    for query, expected in test_queries:
        result = router.classify_query(query)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{query}' -> {result} (expected: {expected})")


def test_data_analysis(df=None):
    """Test data analysis functionality"""
    print("\n" + "="*60)
    print("TEST 3: Data Analysis")
    print("="*60)
    
    # Create sample data if no table was extracted
    if df is None:
        print("\nUsing sample data (no tables extracted from PDFs)")
        df = pd.DataFrame({
            'Product': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B'],
            'Sales': [100, 150, 200, 120, 180, 210, 110, 160],
            'Region': ['North', 'North', 'South', 'South', 'North', 'South', 'North', 'South'],
            'Quantity': [10, 15, 20, 12, 18, 21, 11, 16]
        })
    else:
        print(f"\nUsing extracted table ({len(df)} rows)")
    
    analyzer = DataAnalyzer(df)
    
    # Test various analysis operations
    test_queries = [
        "What is the average Sales?",
        "What is the sum of Sales?",
        "How many products are there?",
        "What is the maximum Sales?",
        "What is the minimum Sales?",
        "Show me the top 3 Sales",
    ]
    
    print("\nData Analysis Tests:")
    for query in test_queries:
        print(f"\n  Query: {query}")
        result = analyzer.analyze(query)
        
        if 'error' in result:
            print(f"    ✗ Error: {result['error']}")
        else:
            print(f"    ✓ Operation: {result.get('operation', 'N/A')}")
            if 'result' in result:
                print(f"    ✓ Result: {result['result']}")
            if 'results' in result:
                print(f"    ✓ Results: {result['results']}")


def test_integration():
    """Test full integration"""
    print("\n" + "="*60)
    print("TEST 4: Full Integration Test")
    print("="*60)
    
    from src.core.hybrid_chatbot import HybridChatbot
    
    # Create hybrid chatbot (without vector store for this test)
    chatbot = HybridChatbot()
    
    # Test loading a document
    pdf_files = list(Path("data/documents").glob("*.pdf"))
    
    if pdf_files:
        pdf_path = str(pdf_files[0])
        print(f"\nLoading document: {pdf_path}")
        result = chatbot.load_document(pdf_path)
        print(f"  Has tables: {result['has_tables']}")
        print(f"  Tables count: {result['tables_count']}")
        
        if result['has_tables']:
            print("\n  Testing data analysis query...")
            # Create a mock RAG function
            def mock_rag(query):
                return {'answer': 'Mock RAG response', 'sources': []}
            
            query = "What is the average of the first numeric column?"
            response = chatbot.query(query, rag_function=mock_rag)
            print(f"  Query: {query}")
            print(f"  Mode: {response.get('mode', 'N/A')}")
            print(f"  Answer preview: {response.get('answer', 'N/A')[:200]}...")
    else:
        print("\n⚠️ No PDF files found - skipping integration test")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("HYBRID RAG + DATA ANALYSIS TEST SUITE")
    print("="*60)
    
    # Test 1: Table Extraction
    extracted_table = test_table_extraction()
    
    # Test 2: Query Routing
    test_query_routing()
    
    # Test 3: Data Analysis
    test_data_analysis(extracted_table)
    
    # Test 4: Integration
    test_integration()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("1. Upload a PDF with tables to data/documents/")
    print("2. Start the server: python app.py")
    print("3. Upload documents via the web interface")
    print("4. Try queries like:")
    print("   - 'What is the average sales?'  (data analysis)")
    print("   - 'Summarize the document'      (document retrieval)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
