import json
import csv
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os

class Demographics(BaseModel):
    age: int
    gender: str

class PatientCase(BaseModel):
    patient_id: str
    demographics: Demographics
    symptoms: List[str]
    risk_factors: List[str]
    ground_truth_diagnosis: str
    urgency_label: str
    expected_referral_decision: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientCase":
        return cls(**data)

def load_json_dataset(filepath: str) -> List[PatientCase]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    return [PatientCase.from_dict(case) for case in data]

def load_csv_dataset(filepath: str) -> List[PatientCase]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found: {filepath}")
        
    cases = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            case = PatientCase(
                patient_id=row['patient_id'],
                demographics=Demographics(
                    age=int(row['age']),
                    gender=row['gender']
                ),
                symptoms=[s.strip() for s in row['symptoms'].split('|') if s.strip()],
                risk_factors=[r.strip() for r in row['risk_factors'].split('|') if r.strip()],
                ground_truth_diagnosis=row['ground_truth_diagnosis'],
                urgency_label=row['urgency_label'],
                expected_referral_decision=row['expected_referral_decision']
            )
            cases.append(case)
            
    return cases

def load_dataset(filepath: str) -> List[PatientCase]:
    if filepath.endswith('.json'):
        return load_json_dataset(filepath)
    elif filepath.endswith('.csv'):
        return load_csv_dataset(filepath)
    else:
        raise ValueError("Unsupported file format. Must be .json or .csv")
