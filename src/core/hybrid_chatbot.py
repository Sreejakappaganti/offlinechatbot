"""
Enhanced Chatbot with Hybrid RAG + Data Analysis
Combines document retrieval with table-based data analysis
"""
from pathlib import Path
import pandas as pd
from typing import Dict, Optional, List

from .config import (
    SYSTEM_PROMPT, TABULAR_DATA_DIR,
    get_rag_prompt, get_data_analysis_prompt, 
    create_table_info_context, classify_query_type
)
from .table_extractor import TableExtractor
from .query_router import QueryRouter
from .data_analyzer import DataAnalyzer


class HybridChatbot:
    """Chatbot with both RAG and Data Analysis capabilities"""
    
    def __init__(self, vector_store=None, llm_client=None):
        """
        Initialize hybrid chatbot
        
        Args:
            vector_store: FAISS vector store instance
            llm_client: Ollama LLM client instance
        """
        # RAG components
        self.vector_store = vector_store
        self.llm = llm_client
        
        # Data analysis components
        self.table_extractor = TableExtractor(TABULAR_DATA_DIR)
        self.query_router = QueryRouter()
        self.current_dataframe = None
        self.current_document_name = None
        self.available_tables = {}  # Store all extracted tables
    
    def load_document(self, file_path: str) -> Dict:
        """
        Load document - handles both text and tabular data
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with loading status and information
        """
        file_path = Path(file_path)
        self.current_document_name = file_path.name
        
        result = {
            'filename': file_path.name,
            'has_text': False,
            'has_tables': False,
            'tables_count': 0,
            'table_info': []
        }
        
        # For PDFs, try to extract tables
        if file_path.suffix.lower() == '.pdf':
            print(f"Checking for tables in {file_path.name}...")
            tables = self.table_extractor.extract_tables(str(file_path))
            
            if tables:
                # Store all tables
                self.available_tables[file_path.name] = tables
                
                # Check if tables can be combined (same columns)
                if len(tables) > 1:
                    # Check if all tables have the same columns
                    first_cols = set(tables[0].columns)
                    if all(set(df.columns) == first_cols for df in tables):
                        # Combine tables into one DataFrame
                        print(f"  Found {len(tables)} tables with matching columns - combining...")
                        self.current_dataframe = pd.concat(tables, ignore_index=True)
                        print(f"✓ Combined {len(tables)} tables into {len(self.current_dataframe)} total rows")
                    else:
                        # Different columns - use the largest table
                        print(f"  Found {len(tables)} tables with different columns - using largest")
                        self.current_dataframe = max(tables, key=len)
                else:
                    self.current_dataframe = tables[0]
                
                result['has_tables'] = True
                result['tables_count'] = len(tables)
                result['table_info'] = [{
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist()
                } for df in tables]
                
                print(f"✓ Loaded tabular data: {len(self.current_dataframe)} rows, "
                      f"{len(self.current_dataframe.columns)} columns")
                print(f"  Columns: {', '.join(self.current_dataframe.columns)}")
                
                # Show ID range if Order_ID column exists
                if 'Order_ID' in self.current_dataframe.columns:
                    id_min = self.current_dataframe['Order_ID'].min()
                    id_max = self.current_dataframe['Order_ID'].max()
                    id_count = self.current_dataframe['Order_ID'].nunique()
                    print(f"  Order_ID range: {id_min} to {id_max} ({id_count} unique IDs)")
            else:
                self.current_dataframe = None
                print("  No tables found - document retrieval only")
        
        # For CSV/Excel files, load directly
        elif file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
            try:
                if file_path.suffix.lower() == '.csv':
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                self.current_dataframe = df
                self.available_tables[file_path.name] = [df]
                
                result['has_tables'] = True
                result['tables_count'] = 1
                result['table_info'] = [{
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist()
                }]
                
                print(f"✓ Loaded tabular data from {file_path.suffix}: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"  Error loading tabular data: {e}")
        
        return result
    
    def query(self, user_query: str, rag_function=None) -> Dict:
        """
        Main query method - routes to appropriate mode
        
        Args:
            user_query: User's question
            rag_function: Function to perform RAG (for document retrieval)
            
        Returns:
            Dictionary with answer and metadata
        """
        # Classify query type - pass whether we have tabular data
        has_tabular_data = self.current_dataframe is not None
        query_type = self.query_router.classify_query(user_query, has_tabular_data)
        
        print(f"🎯 Query Type: {query_type} (Has tabular data: {has_tabular_data})")
        
        if query_type == 'data_analysis' and has_tabular_data:
            return self._handle_data_analysis(user_query)
        else:
            # Fallback to document retrieval
            if rag_function:
                return rag_function(user_query)
            else:
                return {
                    'answer': 'RAG function not provided',
                    'error': 'no_rag_function'
                }
    
    def _handle_data_analysis(self, query: str) -> Dict:
        """Handle data analysis queries (MODE 2)"""
        
        # Check if we have tabular data
        if self.current_dataframe is None:
            return {
                'answer': ("This question requires structured tabular data for accurate calculation. "
                          "The current document contains only narrative text. "
                          "Please upload a document with tables or a CSV/Excel file."),
                'mode': 'data_analysis',
                'error': 'no_tabular_data'
            }
        
        try:
            # Perform calculation using DataAnalyzer
            analyzer = DataAnalyzer(self.current_dataframe)
            result = analyzer.analyze(query)
            
            # Format the result
            formatted_answer = self._format_data_analysis_result(result, query)
            
            return {
                'answer': formatted_answer,
                'mode': 'data_analysis',
                'calculation_result': result,
                'dataframe_info': {
                    'rows': len(self.current_dataframe),
                    'columns': self.current_dataframe.columns.tolist()
                }
            }
            
        except Exception as e:
            return {
                'answer': f"Error performing calculation: {str(e)}",
                'mode': 'data_analysis',
                'error': str(e)
            }
    
    def _format_data_analysis_result(self, result: dict, query: str) -> str:
        """Format data analysis results for display"""
        
        if 'error' in result:
            error_msg = f"❌ Error: {result['error']}"
            if 'suggestion' in result:
                error_msg += f"\n\n💡 Suggestion: {result['suggestion']}"
            if 'available_columns' in result:
                error_msg += f"\n\nAvailable columns: {', '.join(result['available_columns'])}"
            return error_msg
        
        output = f"\n{'='*60}\n"
        output += f"🔢 DATA ANALYSIS RESULT\n"
        output += f"{'='*60}\n\n"
        
        output += f"Operation: {result.get('operation', 'N/A')}\n"
        
        # For specific row lookups, format differently
        if result.get('query_type') == 'specific_row':
            output += f"\n✓ Found specific record!\n\n"
            if 'details' in result:
                for key, val in result['details'].items():
                    output += f"  • {key}: {val}\n"
            output += f"\n➡️ Answer: {result.get('column', 'Value')} = {result.get('result', 'N/A')}\n"
        
        # For group analysis results
        elif 'group_by' in result:
            if 'answer' in result:
                output += f"\n✓ {result['answer']}\n\n"
            
            if 'results' in result:
                output += f"Results by {result.get('group_by', 'Category')}:\n"
                for key, val in result['results'].items():
                    output += f"  • {key}: {val}\n"
            elif 'all_groups' in result:
                output += f"All Results:\n"
                for key, val in sorted(result['all_groups'].items(), key=lambda x: x[1], reverse=True):
                    output += f"  • {key}: {val}\n"
        
        else:
            # Normal calculation results
            output += f"Column: {result.get('column', 'N/A')}\n\n"
            
            if 'result' in result:
                output += f"✓ Result: {result['result']}\n"
            
            if 'sample_size' in result:
                output += f"Sample Size: {result['sample_size']} records\n"
            
            if 'calculation' in result:
                output += f"Calculation: {result['calculation']}\n"
            
            if 'total_count' in result:
                output += f"Total Count: {result['total_count']}\n"
            
            if 'unique_count' in result:
                output += f"Unique Count: {result['unique_count']}\n"
            
            if 'frequency' in result:
                output += f"Frequency: {result['frequency']}\n"
            
            if 'percentage' in result:
                output += f"Percentage: {result['percentage']}%\n"
            
            if 'details' in result and result.get('query_type') != 'specific_row':
                output += f"\nDetails:\n"
                for key, val in result['details'].items():
                    output += f"  • {key}: {val}\n"
            
            if 'results' in result:
                output += f"\nResults:\n"
                if isinstance(result['results'], list):
                    for i, item in enumerate(result['results'][:10], 1):
                        if isinstance(item, dict):
                            output += f"{i}. " + ", ".join([f"{k}: {v}" for k, v in item.items()]) + "\n"
                        else:
                            output += f"{i}. {item}\n"
                    if len(result['results']) > 10:
                        output += f"... and {len(result['results']) - 10} more\n"
                elif isinstance(result['results'], dict):
                    for key, val in result['results'].items():
                        output += f"  • {key}: {val}\n"
            
            if 'statistics' in result:
                output += f"\nStatistics:\n"
                for key, val in result['statistics'].items():
                    output += f"  • {key}: {val}\n"
        
        output += f"\n📊 Source: Calculated from {self.current_document_name or 'uploaded data'}\n"
        output += f"{'='*60}\n"
        
        return output
    
    def get_table_info(self) -> Optional[str]:
        """Get information about currently loaded table"""
        if self.current_dataframe is None:
            return None
        
        return create_table_info_context(self.current_dataframe)
    
    def has_tables(self) -> bool:
        """Check if tables are currently available"""
        return self.current_dataframe is not None
