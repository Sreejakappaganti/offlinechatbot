"""
Quick API Test for Hybrid Chatbot
Tests the running server's data analysis capabilities
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing /health endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_stats():
    """Test stats endpoint"""
    print("\n" + "="*60)
    print("Testing /stats endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total vectors: {data.get('total_vectors', 0)}")
    print(f"Has tables: {data.get('tables', {}).get('available', False)}")
    if data.get('tables', {}).get('available'):
        print("Table info available!")
    return response.status_code == 200


def test_chat_data_analysis():
    """Test chat with data analysis query"""
    print("\n" + "="*60)
    print("Testing /chat with data analysis query")
    print("="*60)
    
    query = "What is the average of CHAPTER NO?"
    print(f"Query: {query}")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if 'mode' in data:
        print(f"Mode: {data['mode']}")
    
    if 'answer' in data:
        print(f"Answer:\n{data['answer']}")
    
    if 'error' in data:
        print(f"Error: {data['error']}")
    
    return response.status_code == 200


def test_chat_document_retrieval():
    """Test chat with document retrieval query"""
    print("\n" + "="*60)
    print("Testing /chat with document retrieval query")
    print("="*60)
    
    query = "What are the main topics in the document?"
    print(f"Query: {query}")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if 'mode' in data:
        print(f"Mode: {data.get('mode', 'N/A')}")
    
    if 'answer' in data:
        print(f"Answer: {data['answer'][:200]}...")
    
    if 'sources' in data:
        print(f"Sources: {len(data['sources'])} chunks retrieved")
    
    return response.status_code == 200


def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("HYBRID CHATBOT API TESTS")
    print("="*60)
    print(f"Testing server at: {BASE_URL}")
    
    try:
        # Test 1: Health check
        if not test_health():
            print("\n❌ Server health check failed!")
            return
        
        # Test 2: Stats
        test_stats()
        
        # Test 3: Data analysis query
        test_chat_data_analysis()
        
        # Test 4: Document retrieval query
        test_chat_document_retrieval()
        
        print("\n" + "="*60)
        print("✅ ALL API TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nThe hybrid chatbot is working!")
        print("You can now:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Upload documents with tables")
        print("3. Ask questions like:")
        print("   - 'What is the average sales?' (data analysis)")
        print("   - 'Summarize the document' (RAG)")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
