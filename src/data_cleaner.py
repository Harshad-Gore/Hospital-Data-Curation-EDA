"""
data cleaning and preprocessing functions
"""
import pandas as pd
import numpy as np
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
from fuzzywuzzy import fuzz

try:
    from config import MAX_AGE, MIN_AGE, MAX_LOS_DAYS, MIN_LOS_DAYS, ICD10_PATTERN
    from utils import setup_logging, calculate_age, validate_icd10_code, detect_outliers_iqr
except ImportError:
    from . import config
    from . import utils
    MAX_AGE = config.MAX_AGE
    MIN_AGE = config.MIN_AGE
    MAX_LOS_DAYS = config.MAX_LOS_DAYS
    MIN_LOS_DAYS = config.MIN_LOS_DAYS
    ICD10_PATTERN = config.ICD10_PATTERN
    setup_logging = utils.setup_logging
    calculate_age = utils.calculate_age
    validate_icd10_code = utils.validate_icd10_code
    detect_outliers_iqr = utils.detect_outliers_iqr

logger = setup_logging()

class DataCleaner:
    """
    comprehensive data cleaning operations
    """
    
    def __init__(self):
        self.cleaning_report = []
    
    def clean_patients_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        clean patients dataset
        """
        logger.info("cleaning patients data...")
        initial_rows = len(df)
        
        # handle missing values in critical columns
        df = self._handle_missing_patient_info(df)
        
        # standardize gender values
        df = self._standardize_gender(df)
        
        # validate and fix date of birth
        df = self._clean_date_of_birth(df)
        
        # calculate age from dob
        if 'date_of_birth' in df.columns:
            df['age'] = calculate_age(pd.to_datetime(df['date_of_birth'], errors='coerce'))
            df = df[(df['age'] >= MIN_AGE) & (df['age'] <= MAX_AGE)]
            logger.info(f"filtered records with invalid age (not in range {MIN_AGE}-{MAX_AGE})")
        
        # remove duplicate patients
        df = self._remove_duplicate_patients(df)
        
        final_rows = len(df)
        self.cleaning_report.append({
            'dataset': 'patients',
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': initial_rows - final_rows
        })
        
        logger.info(f"patients data cleaned: {initial_rows} -> {final_rows} rows")
        return df
    
    def clean_visits_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        clean visits dataset
        """
        logger.info("cleaning visits data...")
        initial_rows = len(df)
        
        # parse date columns
        if 'admission_date' in df.columns:
            df['admission_date'] = pd.to_datetime(df['admission_date'], errors='coerce')
        if 'discharge_date' in df.columns:
            df['discharge_date'] = pd.to_datetime(df['discharge_date'], errors='coerce')
        
        # remove records where discharge is before admission
        if 'admission_date' in df.columns and 'discharge_date' in df.columns:
            invalid_dates = df['discharge_date'] < df['admission_date']
            df = df[~invalid_dates]
            logger.info(f"removed {invalid_dates.sum()} records with discharge before admission")
        
        # calculate length of stay
        if 'admission_date' in df.columns and 'discharge_date' in df.columns:
            df['length_of_stay'] = (df['discharge_date'] - df['admission_date']).dt.days
            # remove invalid length of stay
            invalid_los = (df['length_of_stay'] < MIN_LOS_DAYS) | (df['length_of_stay'] > MAX_LOS_DAYS)
            df = df[~invalid_los]
            logger.info(f"removed {invalid_los.sum()} records with invalid length of stay")
        
        # remove duplicate visit records
        if 'visit_id' in df.columns:
            duplicates = df.duplicated(subset=['visit_id'], keep='first')
            df = df[~duplicates]
            logger.info(f"removed {duplicates.sum()} duplicate visit records")
        
        final_rows = len(df)
        self.cleaning_report.append({
            'dataset': 'visits',
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': initial_rows - final_rows
        })
        
        logger.info(f"visits data cleaned: {initial_rows} -> {final_rows} rows")
        return df
    
    def clean_diagnoses_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        clean diagnoses dataset
        """
        logger.info("cleaning diagnoses data...")
        initial_rows = len(df)
        
        # validate icd-10 codes
        if 'icd_code' in df.columns:
            df['icd_code'] = df['icd_code'].astype(str).str.strip().str.upper()
            valid_codes = df['icd_code'].apply(lambda x: validate_icd10_code(x, ICD10_PATTERN))
            invalid_count = (~valid_codes).sum()
            # mark invalid codes rather than removing them
            df['icd_code_valid'] = valid_codes
            logger.info(f"found {invalid_count} invalid icd-10 codes")
        
        # remove duplicates
        if 'visit_id' in df.columns and 'icd_code' in df.columns:
            duplicates = df.duplicated(subset=['visit_id', 'icd_code'], keep='first')
            df = df[~duplicates]
            logger.info(f"removed {duplicates.sum()} duplicate diagnosis records")
        
        final_rows = len(df)
        self.cleaning_report.append({
            'dataset': 'diagnoses',
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': initial_rows - final_rows
        })
        
        logger.info(f"diagnoses data cleaned: {initial_rows} -> {final_rows} rows")
        return df
    
    def clean_medications_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        clean medications dataset
        """
        logger.info("cleaning medications data...")
        initial_rows = len(df)
        
        # standardize medication names
        if 'medication_name' in df.columns:
            df['medication_name'] = df['medication_name'].str.strip().str.title()
        
        # remove records with missing critical information
        critical_cols = ['visit_id', 'medication_name']
        df = df.dropna(subset=[col for col in critical_cols if col in df.columns])
        
        # remove duplicates
        if 'visit_id' in df.columns and 'medication_name' in df.columns:
            duplicates = df.duplicated(subset=['visit_id', 'medication_name'], keep='first')
            df = df[~duplicates]
            logger.info(f"removed {duplicates.sum()} duplicate medication records")
        
        final_rows = len(df)
        self.cleaning_report.append({
            'dataset': 'medications',
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': initial_rows - final_rows
        })
        
        logger.info(f"medications data cleaned: {initial_rows} -> {final_rows} rows")
        return df
    
    def clean_staff_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        clean staff dataset
        """
        logger.info("cleaning staff data...")
        initial_rows = len(df)
        
        # standardize staff names
        if 'staff_name' in df.columns or 'name' in df.columns:
            name_col = 'staff_name' if 'staff_name' in df.columns else 'name'
            df[name_col] = df[name_col].str.strip().str.title()
        
        # remove duplicates
        if 'staff_id' in df.columns:
            duplicates = df.duplicated(subset=['staff_id'], keep='first')
            df = df[~duplicates]
            logger.info(f"removed {duplicates.sum()} duplicate staff records")
        
        final_rows = len(df)
        self.cleaning_report.append({
            'dataset': 'staff',
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': initial_rows - final_rows
        })
        
        logger.info(f"staff data cleaned: {initial_rows} -> {final_rows} rows")
        return df
    
    def _handle_missing_patient_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        handle missing patient information
        """
        # impute missing gender with 'unknown'
        if 'gender' in df.columns:
            df['gender'].fillna('Unknown', inplace=True)
        
        return df
    
    def _standardize_gender(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        standardize gender values
        """
        if 'gender' in df.columns:
            gender_mapping = {
                'M': 'Male', 'm': 'Male', 'male': 'Male', 'MALE': 'Male',
                'F': 'Female', 'f': 'Female', 'female': 'Female', 'FEMALE': 'Female',
                'O': 'Other', 'o': 'Other', 'other': 'Other', 'OTHER': 'Other'
            }
            df['gender'] = df['gender'].map(gender_mapping).fillna('Unknown')
            logger.info("standardized gender values")
        
        return df
    
    def _clean_date_of_birth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        clean and validate date of birth
        """
        if 'date_of_birth' in df.columns:
            df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
            # remove future dates
            future_dob = df['date_of_birth'] > pd.Timestamp.now()
            df = df[~future_dob]
            logger.info(f"removed {future_dob.sum()} records with future date of birth")
        
        return df
    
    def _remove_duplicate_patients(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        remove duplicate patient records based on patient_id
        """
        if 'patient_id' in df.columns:
            duplicates = df.duplicated(subset=['patient_id'], keep='first')
            df = df[~duplicates]
            logger.info(f"removed {duplicates.sum()} duplicate patient records")
        
        return df
    
    def get_cleaning_report(self) -> pd.DataFrame:
        """
        get comprehensive cleaning report
        """
        return pd.DataFrame(self.cleaning_report)
