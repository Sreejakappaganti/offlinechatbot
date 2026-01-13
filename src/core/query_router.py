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
    def classify_query(query: str, has_tabular_data: bool = False) -> str:
        """
        Classify query as 'data_analysis' or 'document_retrieval'
        
        Args:
            query: User's query string
            has_tabular_data: Whether tabular data is currently loaded
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
    
    @staticmethod
    def should_use_data_analysis(query: str, has_tabular_data: bool) -> bool:
        """
        Determine if query should use data analysis mode
        """
        if not has_tabular_data:
            return False
        
        return QueryRouter.classify_query(query, has_tabular_data) == 'data_analysis'
