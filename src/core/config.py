"""
Configuration for Offline AI Chatbot - Hybrid RAG + Data Analysis System
Optimized for 20-30 page documents
"""
import os
from pathlib import Path
from typing import Dict
import pandas as pd

# ============================================================================
# DIRECTORY CONFIGURATION
# ============================================================================

# Base directory - go up to project root (2 levels up from src/core/)
BASE_DIR = Path(__file__).parent.parent.parent

# Directory paths
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
MODELS_DIR = BASE_DIR / "models"
TABULAR_DATA_DIR = DATA_DIR / "vector_store"

# Create directories if they don't exist
for dir_path in [DATA_DIR, DOCUMENTS_DIR, VECTOR_STORE_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LLM CONFIGURATION
# ============================================================================

LLM_MODEL = "gemma:2b"  # Gemma 2B - fast and efficient for 8GB RAM systems
OLLAMA_HOST = "http://localhost:11434"
LLM_TEMPERATURE = 0.1  # Very low for factual extraction
LLM_MAX_TOKENS = 800  # Increased for detailed answers in large docs
LLM_CONTEXT_WINDOW = 4096  # Increased for 20-30 page documents
LLM_TIMEOUT_SECONDS = 180  # 3 minutes timeout

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False

# ============================================================================
# RETRIEVAL CONFIGURATION (Optimized for 20-30 page documents)
# ============================================================================

RETRIEVAL_TOP_K = 5  # Increased from 2 to handle large documents
RETRIEVAL_MAX_CHARS = 6000  # Increased from 4000 for more context
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "nomic-embed-text:v1.5"

# Vector Store Configuration
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.bin"
FAISS_METADATA_PATH = VECTOR_STORE_DIR / "metadata.pkl"
FAISS_METADATA_BM25_PATH = VECTOR_STORE_DIR / "bm25_index.pkl"
RETRIEVAL_RERANK = True

# Document Processing
OCR_LANGUAGE = "eng"
OCR_ENHANCEMENT = True

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT = """You are a precise document assistant. Answer based ONLY on provided context.

RULES:
1. Use ONLY information from the context chunks
2. Be specific with names, dates, numbers, qualifications
3. If information is in context, extract it completely
4. If not in context, say "information not found"
5. NEVER say "unable to extract" or "context does not provide" if data exists
6. Structure answers clearly

Answer directly and completely."""

DATA_ANALYSIS_SYSTEM_PROMPT = """You are a data analysis assistant. Analyze the data and answer the question.

RULES:
1. Use ONLY the provided data
2. Show calculations clearly
3. State units and metrics
4. If data insufficient, say what's missing
5. Be precise with numbers"""

# Calculation keywords for routing
CALCULATION_KEYWORDS = ["sum", "total", "average", "mean", "count", "how many", "maximum", "minimum", 
                        "highest", "lowest", "most", "least", "calculate", "compute"]

# ============================================================================
# HELPER FUNCTIONS FOR SMART PROMPTING
# ============================================================================

def detect_query_type(query: str) -> str:
    """
    Detect the intent of user query to optimize prompt generation
    
    Args:
        query: User's question
        
    Returns:
        Query type: "extraction", "summary", "comparison", or "general"
    """
    query_lower = query.lower()
    
    # Check for summary intent
    if any(word in query_lower for word in ["summarize", "summary", "overview", "main points", "key points"]):
        return "summary"
    
    # Check for comparison intent
    elif any(word in query_lower for word in ["compare", "difference", "similarity", "versus", "vs", "contrast"]):
        return "comparison"
    
    # Check for extraction intent
    elif any(word in query_lower for word in ["who", "what", "when", "where", "list", "extract", "find", "name"]):
        return "extraction"
    
    # Default to general
    else:
        return "general"


def get_rag_prompt(query: str, context: str) -> str:
    """
    Generate optimized RAG prompt based on detected query type
    
    Args:
        query: User's question
        context: Retrieved document chunks
        
    Returns:
        Formatted prompt for LLM
    """
    query_type = detect_query_type(query)
    
    # Base structure
    base = f"""DOCUMENT CONTEXT:
{context}

USER QUESTION: {query}

"""
    
    # Query-specific instructions for better accuracy
    if query_type == "extraction":
        instruction = """TASK: Extract specific information requested in the question.
- Search ALL context chunks thoroughly
- Include ALL relevant details (names, dates, numbers, qualifications)
- Format as structured list if multiple items exist
- State if information is partial or incomplete

ANSWER:"""
    
    elif query_type == "summary":
        instruction = """TASK: Provide comprehensive summary of the documents.
- Identify main topics and key points
- Organize information logically
- Include important dates, names, and numbers
- Capture both high-level themes and specific details

SUMMARY:"""
    
    elif query_type == "comparison":
        instruction = """TASK: Compare and contrast information in the documents.
- List similarities clearly
- List differences clearly  
- Cite specific examples from context
- Note any missing information

COMPARISON:"""
    
    else:  # general
        instruction = """TASK: Answer the question comprehensively using the provided context.
- Extract all relevant information
- Structure your response logically
- Include specific details and citations
- If context is insufficient, state what IS known

ANSWER:"""
    
    return base + instruction


def expand_query(query: str) -> list[str]:
    """
    Generate query variations to improve retrieval coverage
    SIMPLIFIED for faster processing
    
    Args:
        query: Original user query
        
    Returns:
        List of query variations including original (max 2 for speed)
    """
    variations = [query]
    query_lower = query.lower()
    
    # Single variation: Remove question words for better semantic matching
    if query_lower.startswith("who "):
        variations.append(query[4:])  # Remove "who "
    elif query_lower.startswith("what is "):
        variations.append(query[8:])  # Remove "what is "
    elif query_lower.startswith("what are "):
        variations.append(query[9:])  # Remove "what are "
    elif query_lower.startswith("what "):
        variations.append(query[5:])  # Remove "what "
    
    # Return max 2 variations for speed
    return variations[:2]


def format_retrieved_context(chunks: list, include_metadata: bool = True) -> str:
    """
    Format retrieved chunks into readable context for LLM
    
    Args:
        chunks: List of retrieved document chunks with metadata
        include_metadata: Whether to include source information
        
    Returns:
        Formatted context string
    """
    if not chunks:
        return "No relevant context found in documents."
    
    context_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        # Each chunk should have: text, source, page (optional)
        text = chunk.get('text', '')
        source = chunk.get('source', 'Unknown')
        page = chunk.get('page', None)
        
        if include_metadata:
            metadata = f"[Source: {source}"
            if page:
                metadata += f", Page: {page}"
            metadata += "]\n"
            context_parts.append(f"--- Document Chunk {i} ---\n{metadata}{text}\n")
        else:
            context_parts.append(f"--- Chunk {i} ---\n{text}\n")
    
    return "\n".join(context_parts)


def get_data_analysis_prompt(question: str, table_info: str, analysis_result: str) -> str:
    """
    Generate prompt for data analysis questions
    
    Args:
        question: User's question
        table_info: Information about available tables and columns
        analysis_result: Result from data analysis
        
    Returns:
        Formatted prompt for LLM
    """
    return f"""{DATA_ANALYSIS_SYSTEM_PROMPT}

AVAILABLE DATA:
{table_info}

ANALYSIS RESULT:
{analysis_result}

QUESTION: {question}

Based on the analysis result above, provide a clear and concise answer to the question."""


def create_table_info_context(tables: Dict[str, pd.DataFrame]) -> str:
    """
    Create context describing available tables and their structure
    
    Args:
        tables: Dictionary of table name -> DataFrame
        
    Returns:
        Formatted description of tables
    """
    if not tables:
        return "No tabular data available."
    
    parts = []
    for name, df in tables.items():
        parts.append(f"Table: {name}")
        parts.append(f"Columns: {', '.join(df.columns)}")
        parts.append(f"Rows: {len(df)}")
        parts.append("")
    
    return "\n".join(parts)


def classify_query_type(query: str, has_tabular_data: bool = False) -> str:
    """
    Classify query type for routing
    
    Args:
        query: User's question
        has_tabular_data: Whether document has tables
        
    Returns:
        'data_analysis' or 'document_retrieval'
    """
    if not has_tabular_data:
        return 'document_retrieval'
    
    query_lower = query.lower()
    
    # Exclusion words - if these appear, likely document retrieval question
    exclusion_words = ['title', 'name', 'author', 'chapter', 'section', 'project', 'objective', 
                       'introduction', 'conclusion', 'summary', 'about', 'describe', 'explain']
    
    # Check for exclusion words (but not if calculation keywords are also present)
    has_calculation = any(keyword in query_lower for keyword in CALCULATION_KEYWORDS)
    has_exclusion = any(word in query_lower for word in exclusion_words)
    
    if has_exclusion and not has_calculation:
        return 'document_retrieval'
    
    # Check for calculation/data keywords
    if has_calculation:
        return 'data_analysis'
    
    # Check for value lookup patterns (e.g., "what is ORDER_ID of Total_Sales 550000")
    if any(pattern in query_lower for pattern in ['order_id', 'product_id', 'customer_id', 'id of', 'where']):
        return 'data_analysis'
    
    # Default to document retrieval
    return 'document_retrieval'


# ============================================================================
# VALIDATION AND QUALITY SETTINGS
# ============================================================================

# Answer validation
ENABLE_ANSWER_VALIDATION = True  # Check if answer is grounded in context
MIN_ANSWER_OVERLAP = 0.3  # Minimum keyword overlap between answer and context

# Logging and debugging
ENABLE_RETRIEVAL_LOGGING = True  # Log retrieved chunks for debugging
ENABLE_PERFORMANCE_LOGGING = True  # Log response times

# ============================================================================
# OPTIMIZATION FLAGS
# ============================================================================

# Query optimization
ENABLE_QUERY_EXPANSION = True  # Use multiple query variations
MAX_QUERY_VARIATIONS = 3  # Maximum query variations to generate

# Context optimization
ENABLE_CONTEXTUAL_COMPRESSION = False  # Compress context (experimental)
REMOVE_DUPLICATE_CHUNKS = True  # Filter duplicate/very similar chunks

# Response optimization
ENABLE_RESPONSE_CACHING = True  # Cache responses for repeated queries
CACHE_TTL_SECONDS = 3600  # Cache time-to-live (1 hour)

# ============================================================================
# FEATURE FLAGS
# ============================================================================

# Document processing features
ENABLE_PDF_PROCESSING = True
ENABLE_DOCX_PROCESSING = True
ENABLE_PPTX_PROCESSING = True
ENABLE_IMAGE_PROCESSING = True  # OCR from images
ENABLE_TXT_PROCESSING = True

# Advanced features
ENABLE_MULTI_HOP_REASONING = True  # Combine info from multiple chunks
ENABLE_CITATION_GENERATION = True  # Add source citations to answers

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Batch processing
BATCH_SIZE = 32  # Documents to process in one batch
EMBEDDING_BATCH_SIZE = 16  # Embeddings to generate in one batch

# Memory management
MAX_CONTEXT_CHUNKS = 15  # Maximum chunks to include in context
CHUNK_CACHE_SIZE = 1000  # Number of chunks to keep in memory

# Threading
MAX_WORKERS = 4  # Parallel workers for document processing

# ============================================================================
# ERROR HANDLING
# ============================================================================

# Retry settings
MAX_RETRIES = 3  # Maximum retries for failed operations
RETRY_DELAY_SECONDS = 1  # Delay between retries

# Timeouts
LLM_TIMEOUT_SECONDS = 180  # 3 minutes max for LLM (document retrieval only)
EMBEDDING_TIMEOUT_SECONDS = 30  # Maximum wait time for embedding

# ============================================================================
# DEBUGGING AND MONITORING
# ============================================================================

# Debug output
DEBUG_MODE = False  # Enable detailed logging
PRINT_RETRIEVED_CHUNKS = False  # Print chunks to console
PRINT_GENERATED_PROMPTS = False  # Print prompts to console

# Monitoring
TRACK_METRICS = True  # Track accuracy and performance metrics
METRICS_LOG_PATH = DATA_DIR / "metrics.log"

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

# Make key functions available when importing config
__all__ = [
    'detect_query_type',
    'get_rag_prompt', 
    'expand_query',
    'format_retrieved_context',
    'get_data_analysis_prompt',
    'create_table_info_context',
    'classify_query_type',
    'SYSTEM_PROMPT',
    'DATA_ANALYSIS_SYSTEM_PROMPT',
    'CALCULATION_KEYWORDS',
    'TABULAR_DATA_DIR',
    'LLM_MODEL',
    'RETRIEVAL_TOP_K',
    'CHUNK_SIZE',
    'CHUNK_OVERLAP',
]

# ============================================================================
# ADVANCED RETRIEVAL HELPER FUNCTIONS
# ============================================================================

def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute similarity between two text strings using simple word overlap
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0 and 1
    """
    # Normalize texts
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()
    
    # Quick exact match check
    if t1 == t2:
        return 1.0
    
    # If one is significantly shorter, likely different
    len1, len2 = len(t1), len(t2)
    if min(len1, len2) / max(len1, len2) < 0.5:
        return 0.0
    
    # Word overlap-based similarity (Jaccard similarity)
    set1 = set(t1.split())
    set2 = set(t2.split())
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def remove_duplicates(results: list, threshold: float = 0.95) -> list:
    """
    Remove very similar chunks from retrieval results
    
    Args:
        results: List of retrieval results with 'text' field
        threshold: Similarity threshold (0-1), higher = stricter deduplication
        
    Returns:
        List of unique results
    """
    if not results:
        return []
    
    unique = []
    for result in results:
        is_duplicate = False
        for existing in unique:
            similarity = compute_similarity(result['text'], existing['text'])
            if similarity > threshold:
                # Keep the one with better score if available
                if 'score' in result and 'score' in existing:
                    if result['score'] < existing['score']:  # Lower score is better for L2 distance
                        is_duplicate = True
                        break
                else:
                    is_duplicate = True
                    break
        if not is_duplicate:
            unique.append(result)
    
    return unique


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration settings on startup"""
    errors = []
    
    # Check critical paths exist
    if not MODELS_DIR.exists():
        errors.append(f"Models directory not found: {MODELS_DIR}")
    
    # Check LLM parameters are reasonable
    if LLM_TEMPERATURE > 1.0 or LLM_TEMPERATURE < 0:
        errors.append(f"Invalid temperature: {LLM_TEMPERATURE} (must be 0-1)")
    
    if CHUNK_SIZE < 200:
        errors.append(f"Chunk size too small: {CHUNK_SIZE} (min 200)")
    
    if CHUNK_OVERLAP >= CHUNK_SIZE:
        errors.append(f"Chunk overlap ({CHUNK_OVERLAP}) must be less than chunk size ({CHUNK_SIZE})")
    
    if RETRIEVAL_TOP_K > 20:
        errors.append(f"Top-K too large: {RETRIEVAL_TOP_K} (max 20 recommended)")
    
    if errors:
        print("⚠️  Configuration Errors Found:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration validated successfully")
    return True


# Auto-validate on import
if __name__ != "__main__":
    validate_config()

# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
EXAMPLE USAGE:

1. Import configuration:
   from config import get_rag_prompt, expand_query, LLM_MODEL

2. Generate optimized prompt:
   context = retrieve_documents(query)
   prompt = get_rag_prompt(query, context)

3. Use query expansion:
   queries = expand_query("Who is the CEO?")
   # Returns: ["Who is the CEO?", "CEO", "chief executive officer"]

4. Format context:
   formatted = format_retrieved_context(chunks, include_metadata=True)

5. Detect query type:
   qtype = detect_query_type("Summarize the document")
   # Returns: "summary"
"""