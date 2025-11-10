"""
utility functions for hospital data curation
"""
import pandas as pd
import numpy as np
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

try:
    from config import LOG_FORMAT, LOG_FILE, COLUMN_CASE
except ImportError:
    from . import config
    LOG_FORMAT = config.LOG_FORMAT
    LOG_FILE = config.LOG_FILE
    COLUMN_CASE = config.COLUMN_CASE

def setup_logging(log_file: Path = LOG_FILE, level=logging.INFO):
    """
    setup logging configuration
    """
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def convert_to_snake_case(column_name: str) -> str:
    """
    convert column name to snake_case
    """
    # replace spaces and special characters with underscore
    column_name = re.sub(r'[^\w\s]', '', column_name)
    column_name = re.sub(r'\s+', '_', column_name)
    # convert camelCase to snake_case
    column_name = re.sub(r'(?<!^)(?=[A-Z])', '_', column_name)
    return column_name.lower()

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    standardize all column names to snake_case
    """
    df.columns = [convert_to_snake_case(col) for col in df.columns]
    return df

def parse_dates(df: pd.DataFrame, date_columns: List[str], date_format: str = None) -> pd.DataFrame:
    """
    parse date columns to datetime format
    """
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
    return df

def calculate_age(dob: pd.Series, reference_date: pd.Series = None) -> pd.Series:
    """
    calculate age from date of birth
    """
    if reference_date is None:
        reference_date = pd.Timestamp.now()
    
    age = (reference_date - dob).dt.days / 365.25
    return age.astype(int)

def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """
    detect outliers using interquartile range method
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    return (series < lower_bound) | (series > upper_bound)

def save_dataframe(df: pd.DataFrame, file_path: Path, index: bool = False):
    """
    save dataframe to csv file
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=index)
    logging.info(f"saved dataframe to {file_path}")

def load_dataframe(file_path: Path) -> pd.DataFrame:
    """
    load dataframe from csv file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    logging.info(f"loaded dataframe from {file_path}: {len(df)} rows, {len(df.columns)} columns")
    return df

def get_data_summary(df: pd.DataFrame, name: str = "dataset") -> Dict:
    """
    generate summary statistics for a dataframe
    """
    summary = {
        'name': name,
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'missing_values': df.isnull().sum().to_dict(),
        'duplicates': df.duplicated().sum(),
        'dtypes': df.dtypes.astype(str).to_dict()
    }
    return summary

def create_age_groups(age_series: pd.Series, bins: List[Tuple[int, int, str]]) -> pd.Series:
    """
    create age group categories
    bins: list of tuples (min_age, max_age, label)
    """
    def assign_group(age):
        for min_age, max_age, label in bins:
            if min_age <= age <= max_age:
                return label
        return 'unknown'
    
    return age_series.apply(assign_group)

def validate_icd10_code(code: str, pattern: str) -> bool:
    """
    validate icd-10 code format
    """
    if pd.isna(code):
        return False
    return bool(re.match(pattern, str(code)))

def generate_report_timestamp() -> str:
    """
    generate timestamp for report filenames
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def print_section_header(title: str, width: int = 80):
    """
    print formatted section header
    """
    print("\n" + "="*width)
    print(f"{title:^{width}}")
    print("="*width + "\n")
