import requests
import os

BASE_URL = "http://localhost:8000"

def test_ingest():
    print("Testing Ingestion...")
    files = [
        ('files', ('product_specs.md', open('data/product_specs.md', 'rb'), 'text/markdown')),
        ('files', ('checkout.html', open('checkout.html', 'rb'), 'text/html'))
    ]
    response = requests.post(f"{BASE_URL}/ingest", files=files)
    print(response.json())

def test_generate_tests():
    print("\nTesting Test Generation...")
    payload = {
        "query": "Generate test cases for discount code",
        "model": "llama3"
    }
    response = requests.post(f"{BASE_URL}/generate-tests", json=payload)
    print(response.json())

def test_generate_script():
    print("\nTesting Script Generation...")
    payload = {
        "test_case": "Test Scenario: Apply valid discount code. Expected: 15% off.",
        "html_content": "<html>...</html>",
        "model": "llama3"
    }
    response = requests.post(f"{BASE_URL}/generate-script", json=payload)
    print(response.json())

if __name__ == "__main__":
    try:
        test_ingest()
        test_generate_tests()
        test_generate_script()
    except Exception as e:
        print(f"Error: {e}")
