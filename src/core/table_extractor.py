"""
Table Extraction Module
Extracts structured data from PDFs for data analysis
"""
import pandas as pd
from pathlib import Path
import pickle
from typing import List, Optional, Tuple

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False


class TableExtractor:
    """Extract tables from PDFs and cache them for fast access"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_tables(self, pdf_path: str) -> List[pd.DataFrame]:
        """
        Extract all tables from PDF using available methods
        Returns list of DataFrames
        """
        # DISABLE CACHE - Always extract fresh
        cache_key = Path(pdf_path).stem
        cache_path = self.cache_dir / f"{cache_key}_tables.pkl"
        
        # Delete old cache if exists to force fresh extraction
        if cache_path.exists():
            cache_path.unlink()
            print(f"[CACHE] Deleted old cache for {cache_key} - forcing fresh extraction")
        
        # Try extraction methods in order
        tables = []
        
        # Method 1: tabula-py (fastest, good for most PDFs)
        if TABULA_AVAILABLE and not tables:
            try:
                print("Attempting table extraction with tabula...")
                tables = tabula.read_pdf(
                    pdf_path,
                    pages='all',
                    multiple_tables=True,
                    silent=True
                )
                if tables and len(tables) > 0:
                    print(f"✓ Extracted {len(tables)} table(s) with tabula")
            except Exception as e:
                print(f"Tabula extraction failed: {e}")
        
        # Method 2: pdfplumber (more flexible)
        if PDFPLUMBER_AVAILABLE and not tables:
            try:
                print("Attempting table extraction with pdfplumber...")
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_tables = page.extract_tables()
                        for table in page_tables:
                            if table and len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                tables.append(df)
                if tables:
                    print(f"✓ Extracted {len(tables)} table(s) with pdfplumber")
            except Exception as e:
                print(f"PDFPlumber extraction failed: {e}")
        
        # Method 3: camelot (most accurate but slower)
        if CAMELOT_AVAILABLE and not tables:
            try:
                print("Attempting table extraction with camelot...")
                camelot_tables = camelot.read_pdf(pdf_path, pages='all')
                tables = [table.df for table in camelot_tables]
                if tables:
                    print(f"✓ Extracted {len(tables)} table(s) with camelot")
            except Exception as e:
                print(f"Camelot extraction failed: {e}")
        
        if tables:
            # Clean tables (NO CACHING)
            cleaned_tables = [self._clean_dataframe(df) for df in tables]
            
            print(f"✓ Extracted and cleaned {len(cleaned_tables)} table(s) - NO CACHE")
            
            return cleaned_tables
        
        print("⚠️ No tables found in PDF")
        return []
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean extracted dataframe"""
        # Remove empty rows/columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Strip whitespace from string values
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        # Try to convert numeric columns
        for col in df.columns:
            try:
                # Remove common non-numeric characters
                if df[col].dtype == 'object':
                    cleaned = df[col].str.replace(',', '').str.replace('$', '').str.replace('%', '')
                    df[col] = pd.to_numeric(cleaned, errors='ignore')
            except:
                pass
        
        # Try to convert date columns
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        for col in date_cols:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
        
        return df
    
    def has_tables(self, pdf_path: str) -> bool:
        """Check if PDF has extractable tables"""
        tables = self.extract_tables(pdf_path)
        return len(tables) > 0
    
    def get_largest_table(self, pdf_path: str) -> Optional[pd.DataFrame]:
        """Get the largest table from PDF (by row count)"""
        tables = self.extract_tables(pdf_path)
        if not tables:
            return None
        return max(tables, key=len)
