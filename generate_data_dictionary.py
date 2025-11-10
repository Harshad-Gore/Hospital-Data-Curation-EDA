"""
generate comprehensive data dictionary for hospital data curation project
"""
import pandas as pd
from pathlib import Path
import sys
import os

# add src directory to python path
script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
src_dir = script_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# import project modules
import config
import utils

# use imported modules
LOGS_DIR = config.LOGS_DIR
PREPROCESSED_DATA_DIR = config.PREPROCESSED_DATA_DIR
load_dataframe = utils.load_dataframe

# data dictionary entries
data_dictionary = []

# patients dataset
data_dictionary.extend([
    {
        'dataset': 'patients',
        'column_name': 'patient_id',
        'data_type': 'string',
        'description': 'unique identifier for each patient',
        'example': 'P12345',
        'constraints': 'primary key, not null, unique'
    },
    {
        'dataset': 'patients',
        'column_name': 'date_of_birth',
        'data_type': 'date',
        'description': 'patient date of birth',
        'example': '1985-03-15',
        'constraints': 'not null, must be in past'
    },
    {
        'dataset': 'patients',
        'column_name': 'age',
        'data_type': 'integer',
        'description': 'patient age calculated from date of birth',
        'example': '45',
        'constraints': '0 <= age <= 120'
    },
    {
        'dataset': 'patients',
        'column_name': 'gender',
        'data_type': 'string',
        'description': 'patient gender',
        'example': 'Male',
        'constraints': 'values: Male, Female, Other, Unknown'
    },
    {
        'dataset': 'patients',
        'column_name': 'age_group',
        'data_type': 'string',
        'description': 'age category for demographic analysis',
        'example': '36-60',
        'constraints': 'values: 0-18, 19-35, 36-60, 60+'
    }
])

# visits dataset
data_dictionary.extend([
    {
        'dataset': 'visits',
        'column_name': 'visit_id',
        'data_type': 'string',
        'description': 'unique identifier for each hospital visit',
        'example': 'V98765',
        'constraints': 'primary key, not null, unique'
    },
    {
        'dataset': 'visits',
        'column_name': 'patient_id',
        'data_type': 'string',
        'description': 'reference to patient who made the visit',
        'example': 'P12345',
        'constraints': 'foreign key to patients.patient_id'
    },
    {
        'dataset': 'visits',
        'column_name': 'admission_date',
        'data_type': 'date',
        'description': 'date and time of hospital admission',
        'example': '2023-06-15',
        'constraints': 'not null, must be <= discharge_date'
    },
    {
        'dataset': 'visits',
        'column_name': 'discharge_date',
        'data_type': 'date',
        'description': 'date and time of hospital discharge',
        'example': '2023-06-23',
        'constraints': 'must be >= admission_date'
    },
    {
        'dataset': 'visits',
        'column_name': 'length_of_stay',
        'data_type': 'integer',
        'description': 'number of days between admission and discharge',
        'example': '8',
        'constraints': '0 <= los <= 365'
    },
    {
        'dataset': 'visits',
        'column_name': 'admission_type',
        'data_type': 'string',
        'description': 'type of hospital admission',
        'example': 'Emergency',
        'constraints': 'values: Emergency, Scheduled, Transfer'
    },
    {
        'dataset': 'visits',
        'column_name': 'los_category',
        'data_type': 'string',
        'description': 'categorical length of stay classification',
        'example': 'medium_stay',
        'constraints': 'values: short_stay, medium_stay, long_stay, extended_stay'
    }
])

# diagnoses dataset
data_dictionary.extend([
    {
        'dataset': 'diagnoses',
        'column_name': 'visit_id',
        'data_type': 'string',
        'description': 'reference to hospital visit',
        'example': 'V98765',
        'constraints': 'foreign key to visits.visit_id'
    },
    {
        'dataset': 'diagnoses',
        'column_name': 'icd_code',
        'data_type': 'string',
        'description': 'icd-10 diagnostic code',
        'example': 'E11.9',
        'constraints': 'format: [A-Z][0-9][0-9A-Z](.[0-9A-Z]{1,4})?'
    },
    {
        'dataset': 'diagnoses',
        'column_name': 'primary_diagnosis',
        'data_type': 'string',
        'description': 'primary icd-10 code for the visit',
        'example': 'E11.9',
        'constraints': 'one per visit'
    },
    {
        'dataset': 'diagnoses',
        'column_name': 'diagnosis_count',
        'data_type': 'integer',
        'description': 'total number of diagnoses for the visit',
        'example': '3',
        'constraints': '>= 0'
    }
])

# medications dataset
data_dictionary.extend([
    {
        'dataset': 'medications',
        'column_name': 'visit_id',
        'data_type': 'string',
        'description': 'reference to hospital visit',
        'example': 'V98765',
        'constraints': 'foreign key to visits.visit_id'
    },
    {
        'dataset': 'medications',
        'column_name': 'medication_name',
        'data_type': 'string',
        'description': 'name of prescribed medication',
        'example': 'Metformin',
        'constraints': 'not null, standardized generic names'
    },
    {
        'dataset': 'medications',
        'column_name': 'medication_count',
        'data_type': 'integer',
        'description': 'total number of medications prescribed',
        'example': '5',
        'constraints': '>= 0'
    }
])

# staff dataset
data_dictionary.extend([
    {
        'dataset': 'staff',
        'column_name': 'staff_id',
        'data_type': 'string',
        'description': 'unique identifier for hospital staff member',
        'example': 'S45678',
        'constraints': 'primary key, not null, unique'
    },
    {
        'dataset': 'staff',
        'column_name': 'staff_name',
        'data_type': 'string',
        'description': 'full name of staff member',
        'example': 'Dr. Jane Smith',
        'constraints': 'not null'
    },
    {
        'dataset': 'staff',
        'column_name': 'role',
        'data_type': 'string',
        'description': 'staff role or position',
        'example': 'Physician',
        'constraints': 'values: Physician, Nurse, Specialist, etc.'
    }
])

# derived/engineered features
data_dictionary.extend([
    {
        'dataset': 'transformed',
        'column_name': 'is_readmitted',
        'data_type': 'boolean',
        'description': 'flag indicating if patient was readmitted within 30 days',
        'example': 'True',
        'constraints': 'values: 0 (no), 1 (yes)'
    },
    {
        'dataset': 'transformed',
        'column_name': 'is_high_risk',
        'data_type': 'boolean',
        'description': 'flag for high-risk patients based on multiple criteria',
        'example': 'True',
        'constraints': 'values: 0 (no), 1 (yes); based on age, los, diagnosis count, medication count'
    },
    {
        'dataset': 'transformed',
        'column_name': 'days_since_last_admission',
        'data_type': 'integer',
        'description': 'number of days since patient\'s previous admission',
        'example': '45',
        'constraints': '>= 0'
    },
    {
        'dataset': 'transformed',
        'column_name': 'is_weekend_admission',
        'data_type': 'boolean',
        'description': 'flag indicating weekend admission (saturday/sunday)',
        'example': 'False',
        'constraints': 'values: 0 (no), 1 (yes)'
    },
    {
        'dataset': 'transformed',
        'column_name': 'admission_month',
        'data_type': 'integer',
        'description': 'month of admission (1-12)',
        'example': '6',
        'constraints': '1 <= month <= 12'
    },
    {
        'dataset': 'transformed',
        'column_name': 'admission_quarter',
        'data_type': 'integer',
        'description': 'quarter of admission (1-4)',
        'example': '2',
        'constraints': '1 <= quarter <= 4'
    }
])

# create dataframe
dd_df = pd.DataFrame(data_dictionary)

# save to csv
output_file = LOGS_DIR / 'data_dictionary.csv'
dd_df.to_csv(output_file, index=False)
print(f"data dictionary saved to: {output_file}")

# save to excel with formatting
excel_file = LOGS_DIR / 'data_dictionary.xlsx'
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    dd_df.to_excel(writer, sheet_name='Data Dictionary', index=False)
    
    # get workbook and worksheet
    workbook = writer.book
    worksheet = writer.sheets['Data Dictionary']
    
    # adjust column widths
    worksheet.column_dimensions['A'].width = 15
    worksheet.column_dimensions['B'].width = 20
    worksheet.column_dimensions['C'].width = 12
    worksheet.column_dimensions['D'].width = 50
    worksheet.column_dimensions['E'].width = 15
    worksheet.column_dimensions['F'].width = 40

print(f"data dictionary (excel) saved to: {excel_file}")
print(f"\ntotal columns documented: {len(dd_df)}")
print(f"datasets covered: {dd_df['dataset'].nunique()}")
