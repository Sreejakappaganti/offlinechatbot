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
        from .config import classify_query_type
        return classify_query_type(query, has_tabular_data)
    
    @staticmethod
    def should_use_data_analysis(query: str, has_tabular_data: bool) -> bool:
        """
        Determine if query should use data analysis mode
        """
        if not has_tabular_data:
            return False
        
        return QueryRouter.classify_query(query, has_tabular_data) == 'data_analysis'
