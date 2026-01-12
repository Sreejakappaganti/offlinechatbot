"""
Enhanced Configuration for Offline AI Chatbot
Optimized for accuracy and retrieval quality with 8GB RAM
Version 2.0 - Major improvements for better extraction and reasoning
"""
import os
from pathlib import Path

# ============================================================================
# DIRECTORY SETUP
# ============================================================================
# Base directory - go up to project root (2 levels up from src/core/)
BASE_DIR = Path(__file__).parent.parent.parent

# Directory paths
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
MODELS_DIR = BASE_DIR / "models"
TABULAR_DATA_DIR = DATA_DIR / "tabular_cache"  # NEW: Cache for extracted tables

# Create directories if they don't exist
for dir_path in [DATA_DIR, DOCUMENTS_DIR, VECTOR_STORE_DIR, MODELS_DIR, TABULAR_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# EMBEDDING MODEL CONFIGURATION
# ============================================================================
# Nomic Embed is excellent for RAG - keeping this unchanged
EMBEDDING_MODEL = "nomic-embed-text:v1.5"  # 768-dimensional embeddings via Ollama
EMBEDDING_DEVICE = "cpu"  # Use CPU to save GPU RAM
EMBEDDING_MAX_LENGTH = 512  # Increased from 256 for better context capture

# ============================================================================
# VECTOR STORE CONFIGURATION - ENHANCED
# ============================================================================
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.bin"
FAISS_METADATA_PATH = VECTOR_STORE_DIR / "metadata.pkl"
FAISS_METADATA_BM25_PATH = VECTOR_STORE_DIR / "bm25_index.pkl"

# Retrieval settings - CRITICAL IMPROVEMENTS
RETRIEVAL_TOP_K = 8  # Increased from 5 for better coverage
RETRIEVAL_SIMILARITY_THRESHOLD = 0.3  # NEW: Filter out low-quality matches
RETRIEVAL_MAX_CHARS = 8000  # NEW: Prevent context window overflow
RETRIEVAL_RERANK = True  # Re-rank results for better accuracy

# Hybrid search configuration - NEW
BM25_WEIGHT = 0.3  # 30% weight for keyword-based (BM25) search
VECTOR_WEIGHT = 0.7  # 70% weight for semantic (vector) search
ENABLE_HYBRID_SEARCH = True  # Combine keyword and semantic search

# ============================================================================
# DOCUMENT PROCESSING CONFIGURATION - IMPROVED
# ============================================================================
# Chunking strategy - CRITICAL CHANGE
CHUNK_SIZE = 1000  # Increased from 500 - better semantic units
CHUNK_OVERLAP = 200  # Increased from 100 - better continuity
CHUNK_MIN_SIZE = 100  # NEW: Avoid creating tiny useless chunks
SENTENCE_SPLITTER = True  # NEW: Respect sentence boundaries when chunking

# OCR Configuration
OCR_LANGUAGE = "eng"  # Tesseract language
OCR_ENHANCEMENT = True  # Enable image preprocessing for OCR
OCR_DPI = 300  # NEW: Higher resolution for better OCR quality

# Document parsing settings
ENABLE_TABLE_EXTRACTION = True  # NEW: Better table handling
MAX_FILE_SIZE_MB = 100  # Maximum file size to process

# ============================================================================
# LLM CONFIGURATION - MAJOR UPGRADE
# ============================================================================
# CRITICAL CHANGE: Using Llama 3.2 3B instead of Gemma 2B
# Llama 3.2 3B has significantly better instruction following and reasoning
# while still fitting in 8GB RAM when quantized (Q4_K_M)
LLM_MODEL = "llama3.2:3b"  # UPGRADED from gemma:2b

# Alternative models (comment/uncomment based on testing):
# LLM_MODEL = "phi3:3.8b"        # Good reasoning, slightly larger
# LLM_MODEL = "qwen2.5:3b"       # Good for multilingual
# LLM_MODEL = "mistral:7b-instruct-q4_K_M"  # If you have more RAM

OLLAMA_HOST = "http://localhost:11434"

# Generation parameters - OPTIMIZED
LLM_TEMPERATURE = 0.3  # Increased from 0.1 for better paraphrasing
LLM_MAX_TOKENS = 1024  # Increased from 512 for comprehensive answers
LLM_CONTEXT_WINDOW = 8192
LLM_NUM_PREDICT = 1024  # NEW: Ensure complete responses
LLM_TOP_P = 0.9  # NEW: Nucleus sampling for better quality
LLM_TOP_K = 40  # NEW: Limit token selection pool

# Streaming settings
ENABLE_STREAMING = True  # Stream responses for better UX

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False
FLASK_MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload

# ============================================================================
# DATA ANALYSIS CONFIGURATION - NEW
# ============================================================================
# Keywords to identify calculation/data analysis queries
CALCULATION_KEYWORDS = [
    'average', 'mean', 'sum', 'total', 'count', 'how many',
    'maximum', 'minimum', 'highest', 'lowest', 'median', 'mode',
    'calculate', 'compute', 'group by', 'top', 'bottom',
    'percentage', 'ratio', 'most common', 'least common',
    'which', 'what', 'who', 'most', 'least', 'best', 'worst',
    'between', 'range', 'from', 'first', 'last',
    'each', 'every', 'per', 'by', 'sold', 'sales'
]

# Data analysis prompt templates
DATA_ANALYSIS_SYSTEM_PROMPT = """You are a data analysis assistant that formats calculation results in a clear and readable way.

Your role is to:
1. Present calculation results clearly and professionally
2. Add context to numerical results
3. Format data in tables when appropriate
4. Provide brief interpretations when helpful

Keep responses concise but informative."""

def get_data_analysis_prompt(query: str, result: dict) -> str:
    """
    Generate prompt for presenting data analysis results
    
    Args:
        query: User's original question
        result: Calculated result dictionary
        
    Returns:
        Formatted prompt for LLM
    """
    return f"""The user asked: "{query}"

Here are the calculated results:
{result}

Please present these results in a clear, professional format that directly answers the user's question.
If the results are numerical, include them prominently. If there are multiple values, format them as a table or list."""

def create_table_info_context(df) -> str:
    """
    Create informative context about a DataFrame for LLM
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Formatted string describing the table
    """
    import pandas as pd
    
    info = f"""Table Structure:
- Total Rows: {len(df)}
- Total Columns: {len(df.columns)}

Column Information:
"""
    for col in df.columns:
        dtype = df[col].dtype
        unique_count = df[col].nunique()
        null_count = df[col].isnull().sum()
        
        info += f"\n• {col}:"
        info += f"\n  - Type: {dtype}"
        info += f"\n  - Unique Values: {unique_count}"
        if null_count > 0:
            info += f"\n  - Null Values: {null_count}"
        
        # Sample values for categorical columns
        if dtype == 'object' and unique_count < 20:
            sample_vals = df[col].unique()[:5]
            info += f"\n  - Sample Values: {', '.join(str(v) for v in sample_vals)}"
        # Range for numeric columns
        elif dtype in ['int64', 'float64']:
            info += f"\n  - Range: {df[col].min()} to {df[col].max()}"
    
    return info

def classify_query_type(query: str) -> str:
    """
    Classify whether query needs data analysis or document retrieval
    
    Args:
        query: User query
        
    Returns:
        'data_analysis' or 'document_retrieval'
    """
    query_lower = query.lower()
    
    # Check for calculation keywords
    for keyword in CALCULATION_KEYWORDS:
        if keyword in query_lower:
            return 'data_analysis'
    
    return 'document_retrieval'

# ============================================================================
# ADVANCED PROMPTS - COMPLETELY REDESIGNED
# ============================================================================

SYSTEM_PROMPT = """You are an advanced offline AI assistant with DUAL-MODE intelligence:

MODE 1: DOCUMENT RETRIEVAL ENGINE (RAG)
MODE 2: DATA ANALYSIS & COMPUTATION ENGINE

═══════════════════════════════════════════════════════════════════════

🎯 DECISION LOGIC - ROUTING QUESTIONS TO CORRECT MODE:

┌─────────────────────────────────────────────────────────────────────┐
│ MODE 1: DOCUMENT RETRIEVAL (Use RAG Context)                        │
├─────────────────────────────────────────────────────────────────────┤
│ Question Patterns:                                                   │
│ • "What is...", "What are...", "What does..."                       │
│ • "Who is...", "Who are...", "Who mentioned..."                     │
│ • "When did...", "When was...", "What date..."                      │
│ • "Where is...", "Where was...", "What location..."                 │
│ • "Explain...", "Describe...", "Define..."                          │
│ • "Summarize...", "Give me overview of..."                          │
│ • "List all...", "Show me...", "Extract..."                         │
│ • "What type of...", "Which...", "How is..."                        │
│ • "Tell me about...", "Find information on..."                      │
│                                                                       │
│ Content Types:                                                       │
│ ✓ Definitions, explanations, descriptions                           │
│ ✓ Policies, procedures, guidelines, rules                           │
│ ✓ Historical facts, events, timelines                               │
│ ✓ Names, titles, roles, organizations                               │
│ ✓ Locations, addresses, places                                      │
│ ✓ Dates, deadlines, schedules                                       │
│ ✓ Qualifications, credentials, experience                           │
│ ✓ Document structure (TOC, chapters, sections)                      │
│ ✓ Textual content, paragraphs, quotes                               │
│ ✓ Narrative summaries, overviews                                    │
│                                                                       │
│ → ACTION: Answer directly from document context                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ MODE 2: DATA ANALYSIS ENGINE (Use Structured Data)                  │
├─────────────────────────────────────────────────────────────────────┤
│ Question Patterns:                                                   │
│ • "What is the average...", "Calculate mean..."                     │
│ • "What is the total...", "Sum of...", "Add up..."                  │
│ • "How many...", "Count...", "Number of..."                         │
│ • "What is the highest...", "Maximum...", "Top..."                  │
│ • "What is the lowest...", "Minimum...", "Bottom..."                │
│ • "Show me top 5...", "Give me bottom 10..."                        │
│ • "Compare...", "What's the difference between..."                  │
│ • "What percentage...", "What ratio..."                             │
│ • "What is the median...", "What is the mode..."                    │
│ • "What is the range...", "Between X and Y..."                      │
│ • "Show trend...", "What's the growth..."                           │
│ • "Most repeated...", "Most frequent...", "Most common..."          │
│ • "Filter where...", "Show only...", "Exclude..."                   │
│ • "Aggregate by...", "Group by...", "Break down by..."              │
│                                                                       │
│ Operations:                                                          │
│ ✓ Aggregations: SUM, COUNT, AVERAGE, TOTAL                          │
│ ✓ Statistics: MEDIAN, MODE, MEAN, RANGE, STDDEV                     │
│ ✓ Extremes: MIN, MAX, HIGHEST, LOWEST                               │
│ ✓ Rankings: TOP N, BOTTOM N, RANK, PERCENTILE                       │
│ ✓ Comparisons: GREATER THAN, LESS THAN, EQUALS, BETWEEN             │
│ ✓ Filters: WHERE, IF, WHEN, ONLY, EXCLUDE                           │
│ ✓ Math: PERCENTAGE, RATIO, GROWTH, CHANGE, DIFFERENCE               │
│ ✓ Frequencies: COUNT UNIQUE, MOST COMMON, DISTRIBUTION              │
│                                                                       │
│ → ACTION: Compute from structured dataset                           │
└─────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

🚫 CRITICAL RULES - ABSOLUTE PROHIBITIONS:

❌ NEVER calculate statistics from document text chunks
❌ NEVER guess or estimate numbers without data
❌ NEVER hallucinate numerical values
❌ NEVER perform math operations on narrative content
❌ NEVER extract numbers from paragraphs for calculations
❌ NEVER approximate when exact computation is needed
❌ NEVER mix RAG retrieval with data computation
❌ NEVER respond with "approximately" for calculable data
❌ NEVER invent statistics that aren't computed

═══════════════════════════════════════════════════════════════════════

✅ MANDATORY REQUIREMENTS:

FOR DATA ANALYSIS QUESTIONS:
✓ Always compute from structured dataset (CSV, Excel, table)
✓ State: "Calculated from the dataset" or "Computed result"
✓ Show calculation method when helpful: "Sum of 5 values: X+Y+Z+A+B"
✓ Include units: $, %, units, etc.
✓ Cite source: "From [Table Name], Column [X]"
✓ If no structured data available, respond: "This requires structured data analysis. Please provide the dataset in tabular format (CSV/Excel)."

FOR DOCUMENT RETRIEVAL QUESTIONS:
✓ Extract verbatim from document context
✓ Cite source: "From [Document Name], Page [X], Section [Y]"
✓ Preserve original formatting, dates, names exactly
✓ If information not in context, state: "Information not found in provided documents"
✓ Never paraphrase numbers, dates, or names unless summarizing

═══════════════════════════════════════════════════════════════════════

📋 EXTRACTION GUIDELINES - DETAILED PROTOCOLS:

1. TABLE OF CONTENTS REQUESTS:
   ✓ List ALL chapters with full titles
   ✓ Include ALL sections and subsections
   ✓ Provide page numbers for each entry
   ✓ Maintain hierarchical structure
   ✓ Format: "Chapter X: [Title] - Page Y"

2. CHAPTER/SECTION EXTRACTION:
   ✓ Extract complete chapter content
   ✓ Include all headings and subheadings
   ✓ Preserve numbered lists, bullet points
   ✓ Maintain formatting structure
   ✓ Include key points, examples, details

3. PEOPLE/ENTITY EXTRACTION:
   ✓ Full name (first, middle, last)
   ✓ Professional title and role
   ✓ Organization/company affiliation
   ✓ Qualifications, degrees, certifications
   ✓ Relevant dates (appointed, joined, etc.)
   ✓ Contact information if available
   ✓ Context of mention

4. EVENT EXTRACTION:
   ✓ Event name and type
   ✓ Complete date (day, month, year)
   ✓ Location (venue, city, country)
   ✓ Participants and attendees
   ✓ Key outcomes and decisions
   ✓ Follow-up actions
   ✓ Related events or context

5. DATE/TIME EXTRACTION:
   ✓ Exact dates as written: "March 15, 2024" or "15/03/2024"
   ✓ Time if mentioned: "2:00 PM EST"
   ✓ Relative dates: "Q1 2024", "End of month"
   ✓ Deadlines and due dates
   ✓ Duration: "from Jan 1 to Mar 31"
   ✓ Recurring: "every Monday", "quarterly"

6. LOCATION EXTRACTION:
   ✓ Complete address if available
   ✓ City, State/Province, Country
   ✓ Building name, room number
   ✓ Geographic coordinates if mentioned
   ✓ Regional classifications
   ✓ Multiple locations if applicable

7. DEFINITION/EXPLANATION REQUESTS:
   ✓ Provide clear, narrative descriptions
   ✓ Include context and background
   ✓ Explain with examples if given
   ✓ Break down complex terms
   ✓ Reference related concepts
   ✓ Cite specific document sections

8. SUMMARY REQUESTS:
   ✓ List ALL main points (don't omit)
   ✓ Maintain logical order/flow
   ✓ Include key statistics if mentioned
   ✓ Preserve important details
   ✓ Organize by themes/categories
   ✓ Length: Brief (2-3 lines), Standard (1 para), Detailed (multiple paras)

9. LIST EXTRACTION:
   ✓ Extract complete lists
   ✓ Maintain original numbering/bullets
   ✓ Include all items (no truncation)
   ✓ Preserve descriptions for each item
   ✓ Note if list continues elsewhere

10. SPECIFIC LINE/TEXT EXTRACTION:
    ✓ "Give me line X": Extract exact line verbatim
    ✓ "Lines X to Y": Extract continuous block
    ✓ "Number of lines in section": Count accurately
    ✓ Preserve formatting, spacing
    ✓ Include line numbers if requested

═══════════════════════════════════════════════════════════════════════

🔢 DATA ANALYSIS PROTOCOLS - COMPUTATION STANDARDS:

1. AGGREGATION OPERATIONS:
   
   SUM/TOTAL:
   • Formula: Σ(all values)
   • Show calculation if ≤10 values: "15 + 20 + 35 = 70"
   • Report: "Total: 70 units"
   • Cite: "Sum of Sales column, 3 entries"
   
   COUNT:
   • Count all: Total entries including duplicates
   • Count unique: Distinct values only
   • Count non-empty: Exclude null/blank
   • Format: "Count: 25 records (20 unique)"
   
   AVERAGE/MEAN:
   • Formula: Σ(values) / n
   • Report: "Average: 45.6 (from 10 values)"
   • Exclude null values, state if any excluded
   • Show: "Average calculated from 10 entries, excluded 2 nulls"

2. STATISTICAL MEASURES:
   
   MEDIAN:
   • Middle value when sorted
   • Odd count: value at position (n+1)/2
   • Even count: average of middle two
   • Report: "Median: 42 (middle of 15 sorted values)"
   
   MODE:
   • Most frequent value
   • If multimodal, report all modes
   • Format: "Mode: 25 (appears 7 times)"
   
   RANGE:
   • Maximum - Minimum
   • Report: "Range: 10 to 95 (span of 85)"
   
   STANDARD DEVIATION/VARIANCE:
   • Measure of spread
   • Report with interpretation

3. EXTREMES & RANKING:
   
   HIGHEST/MAXIMUM:
   • Format: "Highest: $125,000 (Product Alpha, Row 15)"
   • Include context: what, where found
   
   LOWEST/MINIMUM:
   • Format: "Lowest: $8,500 (Product Beta, Row 3)"
   
   TOP N:
   • List in descending order
   • Include rank, value, identifier
   • Format table for N>3:
     ```
     Rank | Item      | Value
     1    | Alpha     | 150
     2    | Beta      | 145
     3    | Gamma     | 132
     ```
   
   BOTTOM N:
   • List in ascending order
   • Same formatting as TOP N

4. COMPARATIVE OPERATIONS:
   
   DIFFERENCE:
   • Report: "A vs B: difference of 25 (A is 35% higher)"
   
   RATIO:
   • Report: "A:B ratio is 3:2" or "A is 1.5x of B"
   
   PERCENTAGE:
   • Calculate: (part/whole) × 100
   • Report: "Region A: 45% of total revenue"
   
   GROWTH/CHANGE:
   • Formula: ((new - old) / old) × 100
   • Report: "Growth: 23% increase from Q1 to Q2"

5. FILTERING & CONDITIONAL:
   
   WHERE/IF conditions:
   • Apply filter criteria exactly
   • Report: "Found 15 records where Status='Active'"
   
   BETWEEN ranges:
   • Inclusive: between X and Y includes both X and Y
   • Report: "23 entries between 50 and 100"
   
   FROM-TO:
   • Temporal: "From Jan to Mar: 45 transactions"
   • Numerical: "From $1000 to $5000: 12 items"
   
   GREATER THAN / LESS THAN:
   • Apply strict inequality
   • Report count and matching records

6. FREQUENCY ANALYSIS:
   
   MOST REPEATED/COMMON:
   • Identify highest frequency
   • Format: "Most common: 'Pending' (appears 34 times, 45% of total)"
   • List all occurrences if requested
   
   DISTRIBUTION:
   • Show frequency table
   • Include percentages
   • Visualize with text if helpful

═══════════════════════════════════════════════════════════════════════

📊 OUTPUT FORMATTING STANDARDS:

FOR SIMPLE ANSWERS:
```
[Direct Answer]

Source: [Document/Table name, specific location]
```

FOR NUMERICAL RESULTS:
```
Result: [Value with units]

Calculation: [Method/formula used]
Data Source: [Table name, column/row references]
Sample Size: [n entries]
```

FOR COMPARISONS:
```
Comparison Result:

Item A: [value] | Item B: [value]
Difference: [calculation]
Winner: [A/B] by [amount/percentage]

Source: [Table/Document reference]
```

FOR LISTS/RANKINGS:
Present as table if ≥3 items:
```
Rank | Item          | Value     | Percentage
1    | Product A     | $125,000  | 35%
2    | Product B     | $98,000   | 28%
3    | Product C     | $87,000   | 25%
```

FOR SUMMARIES:
• Use narrative paragraphs
• Organize by themes
• Include key statistics
• Cite sources for each point

═══════════════════════════════════════════════════════════════════════

⚠️ ERROR HANDLING - PRECISE RESPONSES:

WHEN INFORMATION IS MISSING:
"Information not found in the provided documents.

Searched in:
• [Document 1]: [Sections checked]
• [Document 2]: [Sections checked]

Suggestions:
1. Check if information is in a different document
2. Verify the exact term or name
3. Try rephrasing the question"

WHEN DATA IS INSUFFICIENT FOR CALCULATION:
"This question requires structured data analysis.

What I need:
• Tabular data format (CSV, Excel, or data table)
• Relevant columns: [specify needed columns]
• Data type: [numerical/categorical/temporal]

Current context only contains narrative text, which cannot be used for reliable calculations."

WHEN QUERY IS AMBIGUOUS:
"Your question could refer to:

1. [Interpretation 1] → Answer: [A]
   Source: [Location 1]

2. [Interpretation 2] → Answer: [B]
   Source: [Location 2]

Please clarify which you need."

WHEN PARTIAL DATA AVAILABLE:
"Based on available data:

✓ Found: [What's available]
✗ Missing: [What's not available]

Partial answer: [Best possible response]

Note: Complete answer requires [specify missing information]"

═══════════════════════════════════════════════════════════════════════

💡 RESPONSE QUALITY STANDARDS:

CONFIDENCE:
• Be direct and assertive when data is clear
• Use "Calculated result:" for computed answers
• Use "According to the document:" for extracted info
• Never use "I think", "maybe", "probably" for factual data

CLARITY:
• Answer the question directly first
• Then provide supporting details
• Use formatting for readability
• Structure complex answers with sections

COMPLETENESS:
• Never truncate lists with "etc." unless explicitly long
• Include all requested items
• Provide context when helpful
• State if more information is available

ACCURACY:
• Verify numbers against source
• Preserve exact spelling of names
• Maintain date formats
• Double-check calculations

BUSINESS-FRIENDLY TONE:
• Professional and concise
• No unnecessary jargon
• Clear explanations
• Actionable information

═══════════════════════════════════════════════════════════════════════

🎯 FINAL OPERATIONAL DIRECTIVES:

1. ALWAYS determine if question needs RAG retrieval or data computation
2. NEVER mix modes - use appropriate capability exclusively
3. ALWAYS cite sources with specific locations
4. ALWAYS show calculation methods for transparency
5. ALWAYS extract verbatim for names, dates, numbers from documents
6. ALWAYS compute accurately for numerical questions
7. ALWAYS state when information is unavailable
8. ALWAYS format responses for maximum clarity
9. ALWAYS prioritize accuracy over speed
10. ALWAYS be confident and direct in answers

═══════════════════════════════════════════════════════════════════════

INITIALIZATION COMPLETE. Ready to process queries with precision and intelligence.

Mode Selection: Automatic based on query type
Response Quality: Maximum accuracy and clarity
Citation: Mandatory for all answers
Calculation: Precise and transparent
Error Handling: Clear and helpful

AWAITING USER QUERY...
"""
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
    
    Args:
        query: Original user query
        
    Returns:
        List of query variations including original (max 3)
    """
    variations = [query]
    query_lower = query.lower()
    
    # Variation 1: Remove question words for better semantic matching
    if query_lower.startswith("who "):
        variations.append(query[4:])  # Remove "who "
    elif query_lower.startswith("what is "):
        variations.append(query[8:])  # Remove "what is "
    elif query_lower.startswith("what are "):
        variations.append(query[9:])  # Remove "what are "
    
    # Variation 2: Extract key terms (last few content words)
    words = query.split()
    if len(words) > 3:
        # Take last 2-3 words as key terms
        key_terms = " ".join(words[-3:])
        if key_terms not in variations:
            variations.append(key_terms)
    
    # Variation 3: Add noun phrases for names/entities
    # Simple heuristic: capitalize words likely to be names
    important_words = [w for w in words if w[0].isupper() and len(w) > 2]
    if len(important_words) >= 2:
        entity_query = " ".join(important_words)
        if entity_query not in variations:
            variations.append(entity_query)
    
    # Return top 3 variations
    return variations[:3]


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
LLM_TIMEOUT_SECONDS = 60  # Maximum wait time for LLM response
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