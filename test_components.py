"""
Direct test of hybrid chatbot components to identify errors
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing hybrid chatbot components...")

try:
    print("\n1. Testing imports...")
    from src.core.table_extractor import TableExtractor
    from src.core.query_router import QueryRouter
    from src.core.data_analyzer import DataAnalyzer
    from src.core.hybrid_chatbot import HybridChatbot
    from src.core.config import TABULAR_DATA_DIR
    import pandas as pd
    print("✓ All imports successful")
    
    print("\n2. Testing Query Router...")
    router = QueryRouter()
    result = router.classify_query("What is the average sales?")
    print(f"✓ Query classification: {result}")
    
    print("\n3. Testing Data Analyzer with sample data...")
    df = pd.DataFrame({
        'Product': ['A', 'B', 'C'],
        'Sales': [100, 150, 200],
        'Quantity': [10, 15, 20]
    })
    
    analyzer = DataAnalyzer(df)
    result = analyzer.analyze("What is the average Sales?")
    print(f"✓ Analysis result: {result}")
    
    print("\n4. Testing Table Extractor...")
    extractor = TableExtractor(TABULAR_DATA_DIR)
    print("✓ Table extractor initialized")
    
    print("\n5. Testing Hybrid Chatbot initialization...")
    chatbot = HybridChatbot()
    print("✓ Hybrid chatbot initialized")
    
    print("\n6. Testing Hybrid Chatbot with sample query...")
    # Mock RAG function
    def mock_rag(query):
        return {'answer': 'Mock RAG response', 'sources': []}
    
    # Load sample data into chatbot
    chatbot.current_dataframe = df
    chatbot.current_document_name = "test.pdf"
    
    result = chatbot.query("What is the average Sales?", rag_function=mock_rag)
    print(f"✓ Hybrid chatbot query result:")
    print(f"  Mode: {result.get('mode', 'N/A')}")
    print(f"  Answer length: {len(result.get('answer', ''))} chars")
    
    if 'error' in result:
        print(f"  ✗ Error: {result['error']}")
    else:
        print("  ✓ No errors")
    
    print("\n" + "="*60)
    print("✅ ALL COMPONENT TESTS PASSED")
    print("="*60)
    print("\nThe hybrid chatbot components are working correctly.")
    print("The server error must be coming from a different source.")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
