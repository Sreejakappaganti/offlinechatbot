"""
Ingestion Script - Process documents and build vector store
Run this script to index documents from the data/documents folder
"""
import sys
from pathlib import Path

import config
from document_processor import DocumentProcessor
from vector_store_nomic import NomicVectorStore as VectorStore


def main():
    """Main ingestion function"""
    print("="*60)
    print("OFFLINE AI CHATBOT - DOCUMENT INGESTION")
    print("="*60)
    
    # Check if documents directory exists and has files
    if not config.DOCUMENTS_DIR.exists():
        print(f"\n[ERROR] Documents directory not found: {config.DOCUMENTS_DIR}")
        print("Creating directory...")
        config.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created: {config.DOCUMENTS_DIR}")
        print("\nPlease add PDF, DOCX, or PPTX files to this directory and run again.")
        return
    
    # Count supported files
    supported_extensions = ['.pdf', '.docx', '.pptx', '.txt']
    files = [f for f in config.DOCUMENTS_DIR.iterdir() 
             if f.suffix.lower() in supported_extensions]
    
    if not files:
        print(f"\n[ERROR] No documents found in: {config.DOCUMENTS_DIR}")
        print("Supported formats: PDF, DOCX, PPTX, TXT")
        print("\nPlease add documents and run again.")
        return
    
    print(f"\nFound {len(files)} documents to process:")
    for f in files:
        print(f"  - {f.name}")
    
    # Initialize components
    print("\n" + "="*60)
    print("Initializing components...")
    print("="*60)
    
    processor = DocumentProcessor()
    vector_store = VectorStore()
    
    # Process documents
    print("\n" + "="*60)
    print("Processing documents...")
    print("="*60 + "\n")
    
    results = processor.process_directory(str(config.DOCUMENTS_DIR))
    
    if not results:
        print("\n[ERROR] No documents were successfully processed.")
        return
    
    # Add to vector store
    print("\n" + "="*60)
    print("Building vector store...")
    print("="*60 + "\n")
    
    total_chunks = 0
    for filename, chunks in results.items():
        print(f"Adding {len(chunks)} chunks from '{filename}'...")
        vector_store.add_documents(chunks, source=filename)
        total_chunks += len(chunks)
    
    # Save vector store
    print("\n" + "="*60)
    print("Saving vector store...")
    print("="*60 + "\n")
    
    vector_store.save()
    
    # Summary
    print("\n" + "="*60)
    print("INGESTION COMPLETE")
    print("="*60)
    print(f"Documents processed: {len(results)}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Vector store location: {config.VECTOR_STORE_DIR}")
    print("\nYou can now run the chatbot:")
    print("  python app.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nIngestion cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
