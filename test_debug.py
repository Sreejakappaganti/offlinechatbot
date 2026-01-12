"""
Debug script to test the hybrid chatbot and identify errors
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def wait_for_server():
    """Wait for server to be ready"""
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✓ Server is ready")
                return True
        except:
            print(f"Waiting for server... ({i+1}/10)")
            time.sleep(1)
    return False

def test_query(query, expected_mode=None):
    """Test a query and show detailed response"""
    print(f"\n{'='*60}")
    print(f"Testing Query: {query}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ Success!")
            print(f"Mode: {data.get('mode', 'N/A')}")
            
            if expected_mode and data.get('mode') != expected_mode:
                print(f"⚠ Expected mode: {expected_mode}, got: {data.get('mode')}")
            
            if 'answer' in data:
                print(f"Answer Preview: {data['answer'][:200]}...")
            
            if 'calculation_result' in data:
                print(f"Calculation Result: {data['calculation_result']}")
            
            if 'sources' in data:
                print(f"Sources: {len(data['sources'])} chunks")
        else:
            print(f"✗ Error!")
            print(f"Error: {data.get('error', 'Unknown')}")
            print(f"Message: {data.get('message', 'N/A')}")
            
            if 'traceback' in data:
                print(f"\nTraceback:")
                print(data['traceback'])
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("DEBUG SCRIPT - Testing Hybrid Chatbot")
    print("="*60)
    
    if not wait_for_server():
        print("\n✗ Server is not responding!")
        print("Please start the server: python app.py")
        return
    
    # Test data analysis queries
    print("\n\n" + "="*60)
    print("TESTING DATA ANALYSIS QUERIES")
    print("="*60)
    
    test_query("What is the average Total_Sales?", expected_mode="data_analysis")
    test_query("What is the sum of Quantity?", expected_mode="data_analysis")
    test_query("How many orders are there?", expected_mode="data_analysis")
    test_query("Show me the top 5 Total_Sales", expected_mode="data_analysis")
    
    # Test document retrieval queries
    print("\n\n" + "="*60)
    print("TESTING DOCUMENT RETRIEVAL QUERIES")
    print("="*60)
    
    test_query("Summarize the document", expected_mode="document_retrieval")
    test_query("What are the main topics?", expected_mode="document_retrieval")
    
    print("\n" + "="*60)
    print("DEBUG COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
