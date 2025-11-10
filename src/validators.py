"""
data validation using pytest and great expectations
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List

try:
    from config import MAX_AGE, MIN_AGE, MAX_LOS_DAYS, MIN_LOS_DAYS, ICD10_PATTERN, LOGS_DIR
    from utils import setup_logging, validate_icd10_code
except ImportError:
    from . import config
    from . import utils
    MAX_AGE = config.MAX_AGE
    MIN_AGE = config.MIN_AGE
    MAX_LOS_DAYS = config.MAX_LOS_DAYS
    MIN_LOS_DAYS = config.MIN_LOS_DAYS
    ICD10_PATTERN = config.ICD10_PATTERN
    LOGS_DIR = config.LOGS_DIR
    setup_logging = utils.setup_logging
    validate_icd10_code = utils.validate_icd10_code

logger = setup_logging()

class DataValidator:
    """
    validate data quality and business rules
    """
    
    def __init__(self):
        self.validation_results = []
    
    def validate_patients(self, df: pd.DataFrame) -> Dict:
        """
        validate patients dataset
        """
        logger.info("validating patients data...")
        results = {
            'dataset': 'patients',
            'checks': []
        }
        
        # check for unique patient_id
        if 'patient_id' in df.columns:
            is_unique = df['patient_id'].is_unique
            results['checks'].append({
                'test': 'unique_patient_id',
                'passed': is_unique,
                'message': 'all patient ids are unique' if is_unique else f"found {df['patient_id'].duplicated().sum()} duplicate patient ids"
            })
        
        # check age range
        if 'age' in df.columns:
            valid_age = df['age'].between(MIN_AGE, MAX_AGE).all()
            results['checks'].append({
                'test': 'valid_age_range',
                'passed': valid_age,
                'message': f'all ages are between {MIN_AGE} and {MAX_AGE}' if valid_age else f"found {(~df['age'].between(MIN_AGE, MAX_AGE)).sum()} invalid ages"
            })
        
        # check for missing critical fields
        critical_fields = ['patient_id']
        for field in critical_fields:
            if field in df.columns:
                no_missing = df[field].notna().all()
                results['checks'].append({
                    'test': f'no_missing_{field}',
                    'passed': no_missing,
                    'message': f'no missing values in {field}' if no_missing else f"found {df[field].isna().sum()} missing values in {field}"
                })
        
        self.validation_results.append(results)
        logger.info(f"patients validation completed: {sum(1 for c in results['checks'] if c['passed'])}/{len(results['checks'])} checks passed")
        return results
    
    def validate_visits(self, df: pd.DataFrame) -> Dict:
        """
        validate visits dataset
        """
        logger.info("validating visits data...")
        results = {
            'dataset': 'visits',
            'checks': []
        }
        
        # check for unique visit_id
        if 'visit_id' in df.columns:
            is_unique = df['visit_id'].is_unique
            results['checks'].append({
                'test': 'unique_visit_id',
                'passed': is_unique,
                'message': 'all visit ids are unique' if is_unique else f"found {df['visit_id'].duplicated().sum()} duplicate visit ids"
            })
        
        # check discharge date after admission date
        if 'admission_date' in df.columns and 'discharge_date' in df.columns:
            valid_dates = (df['discharge_date'] >= df['admission_date']).all()
            results['checks'].append({
                'test': 'discharge_after_admission',
                'passed': valid_dates,
                'message': 'all discharge dates are after admission dates' if valid_dates else f"found {(df['discharge_date'] < df['admission_date']).sum()} invalid date sequences"
            })
        
        # check length of stay range
        if 'length_of_stay' in df.columns:
            valid_los = df['length_of_stay'].between(MIN_LOS_DAYS, MAX_LOS_DAYS).all()
            results['checks'].append({
                'test': 'valid_length_of_stay',
                'passed': valid_los,
                'message': f'all length of stay values are between {MIN_LOS_DAYS} and {MAX_LOS_DAYS} days' if valid_los else f"found {(~df['length_of_stay'].between(MIN_LOS_DAYS, MAX_LOS_DAYS)).sum()} invalid los values"
            })
        
        self.validation_results.append(results)
        logger.info(f"visits validation completed: {sum(1 for c in results['checks'] if c['passed'])}/{len(results['checks'])} checks passed")
        return results
    
    def validate_diagnoses(self, df: pd.DataFrame) -> Dict:
        """
        validate diagnoses dataset
        """
        logger.info("validating diagnoses data...")
        results = {
            'dataset': 'diagnoses',
            'checks': []
        }
        
        # check icd-10 code format
        if 'icd_code' in df.columns:
            valid_codes = df['icd_code'].apply(lambda x: validate_icd10_code(x, ICD10_PATTERN)).all()
            results['checks'].append({
                'test': 'valid_icd10_format',
                'passed': valid_codes,
                'message': 'all icd-10 codes are valid' if valid_codes else f"found {(~df['icd_code'].apply(lambda x: validate_icd10_code(x, ICD10_PATTERN))).sum()} invalid icd-10 codes"
            })
        
        # check for missing visit_id
        if 'visit_id' in df.columns:
            no_missing = df['visit_id'].notna().all()
            results['checks'].append({
                'test': 'no_missing_visit_id',
                'passed': no_missing,
                'message': 'no missing visit ids' if no_missing else f"found {df['visit_id'].isna().sum()} missing visit ids"
            })
        
        self.validation_results.append(results)
        logger.info(f"diagnoses validation completed: {sum(1 for c in results['checks'] if c['passed'])}/{len(results['checks'])} checks passed")
        return results
    
    def validate_referential_integrity(self, patients_df: pd.DataFrame, visits_df: pd.DataFrame) -> Dict:
        """
        validate referential integrity between datasets
        """
        logger.info("validating referential integrity...")
        results = {
            'dataset': 'referential_integrity',
            'checks': []
        }
        
        # check if all patient_ids in visits exist in patients
        if 'patient_id' in patients_df.columns and 'patient_id' in visits_df.columns:
            valid_patients = visits_df['patient_id'].isin(patients_df['patient_id']).all()
            orphaned = (~visits_df['patient_id'].isin(patients_df['patient_id'])).sum()
            results['checks'].append({
                'test': 'visits_patient_id_exists',
                'passed': valid_patients,
                'message': 'all patient ids in visits exist in patients table' if valid_patients else f"found {orphaned} orphaned patient ids in visits"
            })
        
        self.validation_results.append(results)
        logger.info(f"referential integrity validation completed: {sum(1 for c in results['checks'] if c['passed'])}/{len(results['checks'])} checks passed")
        return results
    
    def generate_validation_report(self, output_file: Path = None) -> str:
        """
        generate comprehensive validation report
        """
        if output_file is None:
            output_file = LOGS_DIR / 'validation_report.txt'
        
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("DATA VALIDATION REPORT")
        report_lines.append("="*80)
        report_lines.append("")
        
        total_checks = 0
        passed_checks = 0
        
        for result in self.validation_results:
            report_lines.append(f"\nDataset: {result['dataset']}")
            report_lines.append("-"*80)
            
            for check in result['checks']:
                total_checks += 1
                status = "✓ PASS" if check['passed'] else "✗ FAIL"
                if check['passed']:
                    passed_checks += 1
                
                report_lines.append(f"{status} | {check['test']}")
                report_lines.append(f"       {check['message']}")
                report_lines.append("")
        
        report_lines.append("="*80)
        report_lines.append(f"SUMMARY: {passed_checks}/{total_checks} checks passed ({passed_checks/total_checks*100:.1f}%)")
        report_lines.append("="*80)
        
        report_text = "\n".join(report_lines)
        
        # save to file with UTF-8 encoding to support Unicode characters
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"validation report saved to {output_file}")
        return report_text
