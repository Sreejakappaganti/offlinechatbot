"""
Query Router Module
Routes queries to appropriate mode (RAG or Data Analysis)
"""
from typing import Tuple, Optional
import pandas as pd
from .config import CALCULATION_KEYWORDS


class QueryRouter:
    """Routes queries to RAG or Data Analysis based on intent"""
    
    @staticmethod
    def classify_query(query: str) -> str:
        """
        Classify query as 'data_analysis' or 'document_retrieval'
        """
        query_lower = query.lower()
        
        # Exclude summary/summarize queries (they contain 'sum' but aren't calculations)
        if any(word in query_lower for word in ['summarize', 'summary']):
            return 'document_retrieval'
        
        # Check for calculation keywords
        for keyword in CALCULATION_KEYWORDS:
            if keyword in query_lower:
                return 'data_analysis'
        
        return 'document_retrieval'
    
    @staticmethod
    def should_use_data_analysis(query: str, has_tabular_data: bool) -> bool:
        """
        Determine if query should use data analysis mode
        """
        if not has_tabular_data:
            return False
        
        return QueryRouter.classify_query(query) == 'data_analysis'
