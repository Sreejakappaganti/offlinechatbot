"""
Data Analysis Engine
Performs calculations on structured data
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, Any, Optional


def convert_to_python_type(value):
    """Convert numpy/pandas types to native Python types for JSON serialization"""
    if isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif pd.isna(value):
        return None
    return value


class DataAnalyzer:
    """Handles all data analysis queries on structured datasets"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Main analysis method - routes to specific operations
        """
        query_lower = query.lower()
        
        # Apply filters first (for specific ID queries, regions, etc.)
        df_filtered = self._apply_filters(query)
        
        # Check if filtering resulted in no records
        if len(df_filtered) == 0:
            return {
                'error': 'No records found matching the specified criteria',
                'suggestion': 'Please check the ID or filter values and try again'
            }
        
        # Check if query is asking for a specific row's value
        # This must be checked BEFORE other operations
        import re
        id_pattern_found = re.search(r'(order\s*id|oeder\s*id|order\s+\d+|oeder\s+\d+|\bid\s*\d+|row\s+\d+)', query_lower)
        
        if id_pattern_found and len(df_filtered) == 1:
            # This is definitely a specific row query - return that row's value
            column = self._identify_column(query)
            if column:
                value = df_filtered.iloc[0][column]
                return {
                    'operation': 'VALUE LOOKUP',
                    'result': convert_to_python_type(value),
                    'column': column,
                    'details': {k: convert_to_python_type(v) for k, v in df_filtered.iloc[0].to_dict().items()},
                    'query_type': 'specific_row'
                }
        
        # If we filtered to a single record but didn't match ID pattern, still treat as lookup
        if len(df_filtered) == 1 and len(df_filtered) < len(self.df):
            column = self._identify_column(query)
            if column:
                value = df_filtered.iloc[0][column]
                return {
                    'operation': 'VALUE LOOKUP',
                    'result': convert_to_python_type(value),
                    'column': column,
                    'details': {k: convert_to_python_type(v) for k, v in df_filtered.iloc[0].to_dict().items()},
                    'query_type': 'specific_row'
                }
        
        # Identify target column for aggregation operations
        column = self._identify_column(query)
        if not column:
            return {
                'error': 'Could not identify which column to analyze',
                'available_columns': self.df.columns.tolist()
            }
        
        # Check for \"which/what/who X has most/highest/sold Y\" queries FIRST
        # This catches patterns like: "which region has most sales", "who sold highest", "what category has lowest"
        if any(kw in query_lower for kw in ['which', 'what', 'who']) and any(kw in query_lower for kw in ['most', 'highest', 'best', 'sold', 'lowest', 'worst', 'least']):
            return self._find_group_with_most(column, df_filtered, query)
        
        # Check for group by / aggregation queries (e.g., "average sales of each product")
        if any(phrase in query_lower for phrase in ['each ', 'every ', 'per ', 'by ']):
            # This is likely a group by query
            group_col = self._identify_group_column(query)
            if group_col:
                return self._group_analysis(column, df_filtered, query, group_col)
        
        # Route to appropriate operation
        if any(kw in query_lower for kw in ['average', 'mean']):
            return self._calculate_average(column, df_filtered, query)
        
        elif any(kw in query_lower for kw in ['sum', 'total']):
            # Check if asking for "most" (e.g., "which region has the most sales")
            if any(kw in query_lower for kw in ['most', 'highest', 'top']):
                return self._find_group_with_most(column, df_filtered, query)
            return self._calculate_sum(column, df_filtered, query)
        
        elif any(kw in query_lower for kw in ['count', 'how many']):
            return self._calculate_count(column, df_filtered, query)
        
        elif any(kw in query_lower for kw in ['max', 'maximum', 'highest']):
            return self._find_max(column, df_filtered, query)
        
        elif any(kw in query_lower for kw in ['min', 'minimum', 'lowest']):
            return self._find_min(column, df_filtered, query)
        
        elif any(kw in query_lower for kw in ['median']):
            return self._calculate_median(column, df_filtered, query)
        
        elif any(kw in query_lower for kw in ['mode', 'most common', 'most frequent']):
            return self._calculate_mode(column, df_filtered, query)
        
        elif any(kw in query_lower for kw in ['top', 'bottom']):
            return self._get_top_bottom(column, df_filtered, query)
        
        elif 'group by' in query_lower or any(f'by {col.lower()}' in query_lower for col in self.df.columns):
            return self._group_analysis(column, df_filtered, query)
        
        else:
            # General statistics
            return self._get_statistics(column, df_filtered)
    
    def _identify_column(self, query: str) -> Optional[str]:
        """Identify which column the query is asking about"""
        query_lower = query.lower()
        
        # For specific ID queries, exclude ID columns from consideration
        # e.g., "total sales of orderID 2" should look for "sales", not "orderID"
        import re
        id_columns = []
        filter_columns = []
        
        if re.search(r'(order\s*id|order\s+\d+|\bid\s*\d+)', query_lower):
            # Identify ID columns to exclude
            for col in self.df.columns:
                if 'id' in col.lower():
                    id_columns.append(col.lower())
        
        # For "which/what/who X has most/highest/sold Y" queries, exclude X (grouping column)
        # e.g., "which region has most sales" -> exclude "region", keep "sales"
        # e.g., "which salesperson sold highest sales" -> exclude "salesperson", keep "sales"
        if any(kw in query_lower for kw in ['which', 'what', 'who']) and any(kw in query_lower for kw in ['most', 'highest', 'top', 'maximum', 'best', 'sold', 'lowest', 'worst', 'least']):
            # Identify categorical columns that are likely grouping columns
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                col_lower = col.lower()
                # If categorical column appears early in query (before "has/have/sold"), it's the grouping column
                if col_lower in query_lower:
                    # Find position of column and action words
                    col_pos = query_lower.find(col_lower)
                    has_pos = -1
                    for word in ['has', 'have', 'with', 'sold', 'generated', 'made', 'produced']:
                        pos = query_lower.find(word)
                        if pos > col_pos:
                            has_pos = pos
                            break
                    if has_pos > col_pos:
                        filter_columns.append(col_lower)
        
        # Identify filter columns (e.g., "in the North region", "by region", "for region")
        # These are columns used for filtering or grouping, not the target of calculation
        for col in self.df.columns:
            col_lower = col.lower()
            # Check if column appears in filter/grouping context
            if any(phrase in query_lower for phrase in [
                f'in the {col_lower}',
                f'in {col_lower}',
                f'for the {col_lower}',
                f'from the {col_lower}',
                f'by {col_lower}',
                f'each {col_lower}',
                f'every {col_lower}',
                f'per {col_lower}',
            ]):
                filter_columns.append(col_lower)
        
        # Also check if specific values from categorical columns are mentioned
        for col in self.df.select_dtypes(include=['object']).columns:
            for value in self.df[col].unique():
                value_str = str(value).lower()
                if value_str in query_lower and len(value_str) > 2:
                    filter_columns.append(col.lower())
                    break
        
        # Try exact match (case-insensitive), excluding ID and filter columns
        for col in self.df.columns:
            if col.lower() in id_columns or col.lower() in filter_columns:
                continue
            if col.lower() in query_lower:
                return col
        
        # Try partial match with underscores/spaces
        for col in self.df.columns:
            if col.lower() in id_columns or col.lower() in filter_columns:
                continue
            col_variants = [
                col.lower(),
                col.lower().replace('_', ' '),
                col.lower().replace('_', ''),
            ]
            for variant in col_variants:
                if variant in query_lower:
                    return col
        
        # Try matching key words from the query to column names
        query_words = set(query_lower.split())
        # Remove filter-related and common words
        remove_words = {'order', 'id', 'orderid', 'in', 'the', 'by', 'for', 'from', 'of', 'is', 'what', 'are'}
        query_words = query_words - remove_words
        
        for col in self.df.columns:
            if col.lower() in id_columns or col.lower() in filter_columns:
                continue
            col_words = set(col.lower().replace('_', ' ').split())
            if col_words & query_words:  # If there's any intersection
                return col
        
        # Try partial match with common synonyms
        synonyms = {
            'sales': ['sale', 'revenue', 'amount', 'total'],
            'price': ['cost', 'rate'],
            'quantity': ['qty', 'count', 'number'],
            'date': ['when', 'time'],
            'product': ['item', 'goods'],
        }
        
        for col in self.df.columns:
            if col.lower() in id_columns or col.lower() in filter_columns:
                continue
            col_lower = col.lower()
            for key, syn_list in synonyms.items():
                if key in col_lower:
                    if any(syn in query_lower for syn in syn_list + [key]):
                        return col
        
        # Default to first numeric column if asking for calculation (excluding ID columns)
        for col in self.numeric_columns:
            if col.lower() not in id_columns and col.lower() not in filter_columns:
                return col
        
        return None
    
    def _find_id_column(self) -> Optional[str]:
        """Find the primary ID column in the dataset"""
        for col in self.df.columns:
            if 'id' in col.lower():
                return col
        return self.df.columns[0] if len(self.df.columns) > 0 else None
    
    def _apply_filters(self, query: str) -> pd.DataFrame:
        """Apply filters based on query"""
        df = self.df.copy()
        query_lower = query.lower()
        
        # Check for specific ID filters (e.g., "orderID 2", "order 2", "ID 5")
        import re
        
        # Pattern for "orderID X" or "order X" or "ID X" (including common typos like "oederID")
        id_patterns = [
            r'o[re]der\s*id\s*(\d+)',  # Matches orderID, oederID
            r'o[re]der\s+(\d+)',        # Matches order 2, oeder 2
            r'\bid\s+(\d+)',
            r'row\s+(\d+)',
        ]
        
        id_requested = None
        for pattern in id_patterns:
            match = re.search(pattern, query_lower)
            if match:
                id_requested = int(match.group(1))
                break
        
        if id_requested is not None:
            # Try to find matching column (Order_ID, OrderID, ID, etc.)
            for col in self.df.columns:
                if 'id' in col.lower() or col.lower() == 'order':
                    try:
                        filtered = df[df[col] == id_requested]
                        if len(filtered) > 0:
                            print(f"[Filter] Found {len(filtered)} record(s) with {col} = {id_requested}")
                            return filtered
                    except:
                        pass
            
            # If we reach here, the ID was requested but not found
            print(f"[Filter] ⚠️ No records found with ID = {id_requested}")
            print(f"[Filter] Available ID range: {self.df[self._find_id_column()].min()} to {self.df[self._find_id_column()].max()}")
            # Return empty DataFrame to trigger proper error handling
            return pd.DataFrame()
        
        # Check for "first X", "top X", "last X" patterns
        top_patterns = [
            (r'first\s+(\d+)', 'head'),
            (r'top\s+(\d+)', 'head'),
            (r'last\s+(\d+)', 'tail'),
            (r'bottom\s+(\d+)', 'tail'),
        ]
        
        for pattern, method in top_patterns:
            match = re.search(pattern, query_lower)
            if match:
                n = int(match.group(1))
                if method == 'head':
                    df = df.head(n)
                    print(f"[Filter] Selected first {n} records")
                else:
                    df = df.tail(n)
                    print(f"[Filter] Selected last {n} records")
                return df
        
        # Check for range queries: "between X and Y", "from X to Y"
        range_patterns = [
            r'between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)',
            r'from\s+(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)',
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, query_lower)
            if match:
                lower_bound = float(match.group(1))
                upper_bound = float(match.group(2))
                
                # Find the numeric column being filtered
                filter_col = None
                for col in self.numeric_columns:
                    if col.lower() in query_lower:
                        filter_col = col
                        break
                
                if not filter_col and len(self.numeric_columns) > 0:
                    # Use first numeric column as default
                    filter_col = self.numeric_columns[0]
                
                if filter_col:
                    df = df[(df[filter_col] >= lower_bound) & (df[filter_col] <= upper_bound)]
                    print(f"[Filter] Range filter: {filter_col} between {lower_bound} and {upper_bound} ({len(df)} records)")
                    return df
        
        # Filter by categorical columns (improved matching)
        for col in self.df.select_dtypes(include=['object']).columns:
            # Skip ID columns
            if 'id' in col.lower():
                continue
            
            for value in self.df[col].unique():
                value_str = str(value).lower().strip()
                
                # Try exact match first
                if value_str in query_lower and len(value_str) > 2:
                    filtered = df[df[col] == value]
                    if len(filtered) < len(df) and len(filtered) > 0:
                        print(f"[Filter] Filtered by {col} = {value}: {len(filtered)} records")
                        df = filtered
                        break
                
                # Try partial match for product names (e.g., "t-shirt" matches "T-Shirt")
                # Split on spaces and hyphens
                import re
                query_words = re.findall(r'\b\w+\b', query_lower)
                value_words = re.findall(r'\b\w+\b', value_str)
                
                # Check if all value words appear in query (case insensitive)
                if len(value_words) > 0 and all(word in query_words for word in value_words):
                    filtered = df[df[col] == value]
                    if len(filtered) < len(df) and len(filtered) > 0:
                        print(f"[Filter] Filtered by {col} = {value}: {len(filtered)} records")
                        df = filtered
                        break
        
        return df
    
    def _calculate_average(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        if column not in self.numeric_columns:
            return {'error': f'{column} is not numeric'}
        
        avg = float(df[column].mean())  # Convert to native Python float
        return {
            'operation': 'AVERAGE',
            'result': round(avg, 2),
            'column': column,
            'sample_size': int(len(df)),  # Convert to native Python int
            'calculation': f'Sum of {len(df)} values ÷ {len(df)}'
        }
    
    def _calculate_sum(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        if column not in self.numeric_columns:
            return {'error': f'{column} is not numeric'}
        
        total = float(df[column].sum())  # Convert to native Python float
        return {
            'operation': 'SUM',
            'result': round(total, 2),
            'column': column,
            'sample_size': int(len(df)),  # Convert to native Python int
            'calculation': f'Sum of {len(df)} values'
        }
    
    def _calculate_count(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        return {
            'operation': 'COUNT',
            'total_count': int(len(df)),  # Convert to native Python int
            'unique_count': int(df[column].nunique()),  # Convert to native Python int
            'column': column
        }
    
    def _find_max(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        if column not in self.numeric_columns:
            return {'error': f'{column} is not numeric'}
        
        max_idx = df[column].idxmax()
        max_row = df.loc[max_idx]
        
        # Convert all types to native Python types
        details = {k: convert_to_python_type(v) for k, v in max_row.to_dict().items()}
        
        return {
            'operation': 'MAXIMUM',
            'result': convert_to_python_type(max_row[column]),
            'details': details,
            'column': column
        }
    
    def _find_min(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        if column not in self.numeric_columns:
            return {'error': f'{column} is not numeric'}
        
        min_idx = df[column].idxmin()
        min_row = df.loc[min_idx]
        
        # Convert all types to native Python types
        details = {k: convert_to_python_type(v) for k, v in min_row.to_dict().items()}
        
        return {
            'operation': 'MINIMUM',
            'result': convert_to_python_type(min_row[column]),
            'details': details,
            'column': column
        }
    
    def _calculate_median(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        if column not in self.numeric_columns:
            return {'error': f'{column} is not numeric'}
        
        return {
            'operation': 'MEDIAN',
            'result': float(df[column].median()),  # Convert to native Python float
            'column': column,
            'sample_size': int(len(df))  # Convert to native Python int
        }
    
    def _calculate_mode(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        mode_val = df[column].mode()
        if len(mode_val) > 0:
            mode_val = mode_val[0]
            frequency = int((df[column] == mode_val).sum())
            
            return {
                'operation': 'MODE',
                'result': convert_to_python_type(mode_val),
                'frequency': frequency,
                'percentage': round(float(frequency / len(df) * 100), 1),
                'column': column
            }
        return {'error': 'Could not determine mode'}
    
    def _get_top_bottom(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        # Extract N
        n = 5
        numbers = re.findall(r'\d+', query)
        if numbers:
            n = int(numbers[0])
        
        if 'top' in query.lower():
            result_df = df.nlargest(n, column)
            op = f'TOP {n}'
        else:
            result_df = df.nsmallest(n, column)
            op = f'BOTTOM {n}'
        
        # Convert to dict and ensure all values are JSON serializable
        results = result_df.to_dict('records')
        results = [{k: convert_to_python_type(v) for k, v in record.items()} for record in results]
        
        return {
            'operation': op,
            'results': results,
            'count': len(result_df),
            'column': column
        }
    
    def _group_analysis(self, column: str, df: pd.DataFrame, query: str, group_col: str = None) -> Dict:
        # Identify grouping column if not provided
        if not group_col:
            for col in self.df.columns:
                if f'by {col.lower()}' in query.lower():
                    group_col = col
                    break
        
        if not group_col:
            return {'error': 'Could not identify grouping column'}
        
        # Ensure we have a numeric column for aggregation
        # If column is same as group_col or not numeric, use Total_Sales or first numeric column
        if column == group_col or column not in self.numeric_columns:
            if 'Total_Sales' in self.numeric_columns:
                column = 'Total_Sales'
            else:
                column = self.numeric_columns[0]
        
        # Determine aggregation
        if 'sum' in query.lower() or 'total' in query.lower():
            grouped = df.groupby(group_col)[column].sum().to_dict()
            agg = 'SUM'
        elif 'average' in query.lower() or 'mean' in query.lower():
            grouped = df.groupby(group_col)[column].mean().to_dict()
            agg = 'AVERAGE'
        elif 'count' in query.lower():
            grouped = df.groupby(group_col)[column].count().to_dict()
            agg = 'COUNT'
        else:
            grouped = df.groupby(group_col)[column].sum().to_dict()
            agg = 'SUM'
        
        # Convert all values to native Python types
        grouped = {str(k): convert_to_python_type(v) for k, v in grouped.items()}
        
        return {
            'operation': f'{agg} by {group_col}',
            'results': grouped,
            'column': column,
            'group_by': group_col
        }
    
    def _get_statistics(self, column: str, df: pd.DataFrame) -> Dict:
        if column not in self.numeric_columns:
            return {'error': f'{column} is not numeric'}
        
        stats = df[column].describe().to_dict()
        # Convert all stats to native Python types
        stats = {k: convert_to_python_type(v) for k, v in stats.items()}
        
        return {
            'operation': 'STATISTICS',
            'statistics': stats,
            'column': column
        }
    
    def _identify_group_column(self, query: str) -> Optional[str]:
        """Identify which column to group by (e.g., 'each product', 'per region')"""
        query_lower = query.lower()
        
        # Look for patterns like "each X", "every X", "per X", "by X"
        for col in self.df.columns:
            col_lower = col.lower()
            # Remove underscores and check
            col_clean = col_lower.replace('_', ' ')
            
            if any(pattern.format(col_clean) in query_lower for pattern in [
                'each {}', 'every {}', 'per {}', 'by {}',
                'each {}', 'every {}', 'per {}', 'by {}'
            ]):
                return col
            
            # Check for column name appearing after these keywords
            import re
            patterns = [
                r'each\s+(\w+)',
                r'every\s+(\w+)', 
                r'per\s+(\w+)',
                r'for\s+each\s+(\w+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    word = match.group(1)
                    if word in col_lower or col_lower in word:
                        return col
        
        return None
    
    def _find_group_with_most(self, column: str, df: pd.DataFrame, query: str) -> Dict:
        """Find which group has the most/highest/lowest value (e.g., 'which region has most sales', 'who sold highest')"""
        
        query_lower = query.lower()
        
        # Identify the grouping column from the query
        group_col = None
        for col in df.select_dtypes(include=['object']).columns:
            if col.lower() in query_lower:
                group_col = col
                break
        
        if not group_col:
            # Try common grouping columns
            for col in df.columns:
                if any(word in col.lower() for word in ['region', 'category', 'product', 'type', 'group', 'person', 'salesperson']):
                    group_col = col
                    break
        
        if not group_col or column not in self.numeric_columns:
            return self._calculate_sum(column, df, query)
        
        # Determine if we want highest or lowest
        ascending = any(kw in query_lower for kw in ['lowest', 'worst', 'least', 'minimum'])
        
        # Group and sum
        grouped = df.groupby(group_col)[column].sum().sort_values(ascending=ascending)
        
        top_group = grouped.index[0]
        top_value = float(grouped.iloc[0])
        
        # Convert to dict with native Python types
        all_groups = {str(k): float(v) for k, v in grouped.items()}
        
        # Generate appropriate answer text
        superlative = 'lowest' if ascending else 'highest'
        
        return {
            'operation': 'GROUP ANALYSIS',
            'result': top_group,
            'value': top_value,
            'column': column,
            'group_by': group_col,
            'all_groups': all_groups,
            'answer': f'{top_group} has the {superlative} {column} with {top_value}',
            'superlative': superlative
        }

