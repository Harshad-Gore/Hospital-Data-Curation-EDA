"""
configuration settings for hospital data curation project
"""
import os
from pathlib import Path

# project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
CLEANED_DATA_DIR = DATA_DIR / 'cleaned'
PREPROCESSED_DATA_DIR = DATA_DIR / 'preprocessed'

# output directories
REPORTS_DIR = PROJECT_ROOT / 'reports'
PROFILING_DIR = REPORTS_DIR / 'profiling'
SWEETVIZ_DIR = REPORTS_DIR / 'sweetviz'
LOGS_DIR = PROJECT_ROOT / 'logs'
MODELS_DIR = PROJECT_ROOT / 'models'
VISUALIZATIONS_DIR = PROJECT_ROOT / 'visualizations'

# ensure directories exist
for directory in [RAW_DATA_DIR, CLEANED_DATA_DIR, PREPROCESSED_DATA_DIR, 
                  PROFILING_DIR, SWEETVIZ_DIR, LOGS_DIR, MODELS_DIR, VISUALIZATIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# data file names
DATA_FILES = {
    'patients': 'patients.csv',
    'visits': 'visits.csv',
    'diagnoses': 'diagnoses.csv',
    'medications': 'medications.csv',
    'staff': 'staff.csv',
    'hospital_info': 'hospital_info.csv'
}

# date format
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# validation thresholds
MAX_AGE = 120
MIN_AGE = 0
MAX_LOS_DAYS = 365  # maximum length of stay in days
MIN_LOS_DAYS = 0

# icd-10 code pattern
ICD10_PATTERN = r'^[A-Z][0-9][0-9A-Z](\.[0-9A-Z]{1,4})?$'

# readmission threshold (days)
READMISSION_THRESHOLD_DAYS = 30

# age groups for bucketing
AGE_GROUPS = [
    (0, 18, '0-18'),
    (19, 35, '19-35'),
    (36, 60, '36-60'),
    (61, 150, '60+')
]

# column naming convention
COLUMN_CASE = 'snake_case'

# random seed for reproducibility
RANDOM_SEED = 42

# logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / 'data_curation.log'
