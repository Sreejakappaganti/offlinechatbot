"""
Simple standalone server to test hybrid chatbot
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("Starting simple test server...")

try:
    from src.core.hybrid_chatbot import HybridChatbot
    from src.core.config import FLASK_HOST, FLASK_PORT
    import pandas as pd
    
    app = Flask(__name__)
    CORS(app)
    
    # Create hybrid chatbot with sample data
    chatbot = HybridChatbot()
    
    # Load sample data
    df = pd.DataFrame({
        'Product': ['A', 'B', 'C', 'D', 'E'],
        'Total_Sales': [1000, 1500, 2000, 1200, 1800],
        'Quantity': [10, 15, 20, 12, 18],
        'Region': ['North', 'South', 'North', 'South', 'North']
    })
    
    chatbot.current_dataframe = df
    chatbot.current_document_name = "sample_data.csv"
    
    print("✓ Hybrid chatbot initialized with sample data")
    print(f"  Columns: {', '.join(df.columns.tolist())}")
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'has_tables': chatbot.has_tables(),
            'columns': df.columns.tolist() if chatbot.has_tables() else []
        })
    
    @app.route('/chat', methods=['POST'])
    def chat():
        try:
            data = request.get_json()
            query = data.get('query', '').strip()
            
            if not query:
                return jsonify({'error': 'Query cannot be empty'}), 400
            
            # Mock RAG function
            def mock_rag(q):
                return {
                    'answer': f'Mock RAG response for: {q}',
                    'sources': []
                }
            
            result = chatbot.query(query, rag_function=mock_rag)
            return jsonify(result)
        
        except Exception as e:
            import traceback
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    print(f"\nStarting server on {FLASK_HOST}:{FLASK_PORT}")
    print("Try these queries:")
    print("  - What is the average Total_Sales?")
    print("  - What is the sum of Quantity?")
    print("  - Show me the top 3 Total_Sales")
    print("\n")
    
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
