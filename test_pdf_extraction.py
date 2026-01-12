"""Test PDF extraction for Naac_appLetter.pdf"""
import PyPDF2
import pdfplumber
from pathlib import Path

pdf_path = Path("data/documents/Naac_appLetter.pdf")

print("Testing PDF extraction methods:")
print("=" * 80)

# Test PyPDF2
print("\n1. PyPDF2:")
print("-" * 80)
try:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        print(f"Pages: {len(reader.pages)}")
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text += page_text + "\n"
            print(f"Page {i+1} chars: {len(page_text)}")
        print(f"\nTotal text length: {len(text)} chars")
        print(f"Preview (first 500 chars):\n{text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test pdfplumber
print("\n\n2. pdfplumber:")
print("-" * 80)
try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        text = ""
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            print(f"Page {i+1} chars: {len(page_text) if page_text else 0}")
        print(f"\nTotal text length: {len(text)} chars")
        print(f"Preview (first 1000 chars):\n{text[:1000]}")
except Exception as e:
    print(f"Error: {e}")
