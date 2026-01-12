"""
Direct API test - Simulates what happens when you upload and query
"""
import requests
import json

print("=" * 80)
print("TESTING API DIRECTLY")
print("=" * 80)

base_url = "http://127.0.0.1:5000"

# Step 1: Upload PDF
print("\n1. Uploading PDF...")
with open("data/documents/sales_data_100_rows.pdf", "rb") as f:
    files = {"file": ("sales_data_100_rows.pdf", f, "application/pdf")}
    response = requests.post(f"{base_url}/ingest", files=files)
    
if response.status_code == 200:
    result = response.json()
    print(f"   ✓ Upload successful!")
    print(f"   Response: {json.dumps(result, indent=2)}")
else:
    print(f"   ✗ Upload failed: {response.status_code}")
    print(f"   {response.text}")
    exit(1)

# Step 2: Ask the question
print("\n2. Asking question: 'what is the total sales of orderID 2'")
query_data = {"query": "what is the total sales of orderID 2"}
response = requests.post(f"{base_url}/chat", json=query_data)

if response.status_code == 200:
    result = response.json()
    print(f"   ✓ Query successful!")
    print(f"\n   ANSWER:")
    print(f"   {result.get('answer', 'No answer')}")
    
    if 'calculation_result' in result:
        calc = result['calculation_result']
        print(f"\n   CALCULATION DETAILS:")
        print(f"   - Operation: {calc.get('operation', 'N/A')}")
        print(f"   - Result: {calc.get('result', 'N/A')}")
        if 'sample_size' in calc:
            print(f"   - Sample Size: {calc['sample_size']}")
        if 'details' in calc:
            print(f"   - Details: {calc['details']}")
else:
    print(f"   ✗ Query failed: {response.status_code}")
    print(f"   {response.text}")

print("\n" + "=" * 80)
