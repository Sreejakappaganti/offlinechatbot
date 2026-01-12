# Quick Start Guide - Hybrid RAG + Data Analysis

## 🚀 Running the Server

```bash
# Start the server
python app.py
```

Server will run on: **http://localhost:5000**

---

## 📤 Upload Documents

1. Open http://localhost:5000 in browser
2. Click "Choose Files" or drag & drop
3. Upload PDF, DOCX, PPTX, or TXT files
4. System automatically:
   - Extracts text for Q&A
   - Extracts tables for calculations

---

## 💬 Example Queries

### Data Analysis Queries (Calculations)
```
✓ What is the average Total_Sales?
✓ What is the sum of sales by region?
✓ How many orders are there?
✓ Show me the top 10 products
✓ What is the maximum price?
✓ Calculate the median quantity
```

### Document Retrieval Queries (RAG)
```
✓ Summarize the document
✓ Who are the key people mentioned?
✓ What are the main conclusions?
✓ List all the requirements
✓ What is the problem statement?
✓ Explain the methodology
```

---

## 🔍 How to Know Which Mode Was Used

The system automatically chooses:
- **Data Analysis** - For questions with: average, sum, total, count, max, min, top, bottom, calculate
- **Document Retrieval** - For all other questions

Check the response for `"mode"` field:
```json
{
  "mode": "data_analysis"  // or "document_retrieval"
}
```

---

## 📊 View Cached Tables

Extracted tables are saved as CSV:
```
data/tabular_cache/
  ├── filename_table_0.csv
  ├── filename_table_1.csv
  └── filename_tables.pkl
```

Open CSV files to see extracted data!

---

## 🧪 Testing

### Quick Test
```bash
python test_hybrid_system.py
```

### API Test (server must be running)
```bash
python test_api.py
```

---

## ⚡ Quick Tips

1. **For best table extraction**:
   - Use well-formatted PDFs
   - Tables should have clear headers
   - Avoid scanned images (OCR required)

2. **For accurate calculations**:
   - Use exact column names
   - Check `data/tabular_cache/*.csv` for available columns
   - System will suggest columns if not found

3. **For better document answers**:
   - Ask specific questions
   - Upload relevant documents only
   - Use clear, direct language

---

## 🎯 Common Issues

### "No tables found"
→ PDF may contain images, not actual tables
→ Solution: Convert image tables to actual tables

### "Column not found"
→ Check available columns in error message
→ Use exact column name from CSV cache

### Server not starting
→ Check if Ollama is running: `ollama serve`
→ Check if port 5000 is available

---

## 📞 Need Help?

1. Check [HYBRID_SYSTEM_COMPLETE.md](HYBRID_SYSTEM_COMPLETE.md) for detailed documentation
2. Run tests to verify system status
3. Check server logs for error details

---

**Happy analyzing! 🎉**
