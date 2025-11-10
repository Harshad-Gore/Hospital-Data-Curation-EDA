"""
data loading and ingestion utilities
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional

try:
    from config import RAW_DATA_DIR, DATA_FILES
    from utils import setup_logging, standardize_column_names, get_data_summary
except ImportError:
    from . import config
    from . import utils
    RAW_DATA_DIR = config.RAW_DATA_DIR
    DATA_FILES = config.DATA_FILES
    setup_logging = utils.setup_logging
    standardize_column_names = utils.standardize_column_names
    get_data_summary = utils.get_data_summary

logger = setup_logging()

class DataLoader:
    """
    handles data ingestion from various sources
    """
    
    def __init__(self, data_dir: Path = RAW_DATA_DIR):
        self.data_dir = data_dir
        self.datasets = {}
        
    def load_csv(self, filename: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        load csv file with error handling
        """
        file_path = self.data_dir / filename
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"successfully loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            logger.error(f"file not found: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"error loading {filename}: {str(e)}")
            return pd.DataFrame()
    
    def load_excel(self, filename: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        load excel file
        """
        file_path = self.data_dir / filename
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"successfully loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"error loading {filename}: {str(e)}")
            return pd.DataFrame()
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        load all hospital datasets
        """
        for dataset_name, filename in DATA_FILES.items():
            df = self.load_csv(filename)
            if not df.empty:
                # standardize column names
                df = standardize_column_names(df)
                self.datasets[dataset_name] = df
                logger.info(f"loaded {dataset_name}: {len(df)} rows")
            else:
                logger.warning(f"failed to load {dataset_name} from {filename}")
        
        return self.datasets
    
    def get_dataset(self, name: str) -> Optional[pd.DataFrame]:
        """
        retrieve a specific dataset
        """
        return self.datasets.get(name)
    
    def generate_metadata_report(self) -> pd.DataFrame:
        """
        generate metadata report for all loaded datasets
        """
        metadata = []
        
        for name, df in self.datasets.items():
            file_path = self.data_dir / DATA_FILES[name]
            summary = get_data_summary(df, name)
            
            metadata.append({
                'dataset_name': name,
                'file_name': DATA_FILES[name],
                'file_path': str(file_path),
                'rows': summary['rows'],
                'columns': summary['columns'],
                'memory_mb': round(summary['memory_usage_mb'], 2),
                'total_missing': sum(summary['missing_values'].values()),
                'duplicates': summary['duplicates'],
                'column_list': ', '.join(summary['column_names'][:5]) + '...' if len(summary['column_names']) > 5 else ', '.join(summary['column_names'])
            })
        
        metadata_df = pd.DataFrame(metadata)
        logger.info(f"generated metadata report for {len(metadata)} datasets")
        return metadata_df
    
    def validate_required_columns(self, dataset_name: str, required_columns: list) -> bool:
        """
        validate that dataset has required columns
        """
        df = self.get_dataset(dataset_name)
        if df is None:
            logger.error(f"dataset {dataset_name} not found")
            return False
        
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.error(f"{dataset_name} missing required columns: {missing_columns}")
            return False
        
        logger.info(f"{dataset_name} has all required columns")
        return True
