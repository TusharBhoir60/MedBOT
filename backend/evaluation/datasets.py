import json
import csv
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ReferralDecision(str, Enum):
    ER = "er"
    IMMEDIATE_CLINIC = "immediate_clinic"
    SCHEDULED_VISIT = "scheduled_visit"
    ROUTINE_CHECKUP = "routine_checkup"
    NO_REFERRAL = "no_referral"
    UNKNOWN = "unknown"

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
    expected_referral_decision: ReferralDecision
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientCase":
        return cls(**data)

def _resolve_dataset_path(version_or_path: str) -> str:
    # If it's a direct file path, return it
    if os.path.isfile(version_or_path):
        return version_or_path
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(base_dir), "data", "eval")
    manifest_path = os.path.join(data_dir, "manifest.json")
    
    # Check if a manifest exists
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            
        version = version_or_path
        if version == "latest":
            version = manifest.get("latest", "v1")
            
        if version in manifest.get("versions", {}):
            rel_path = manifest["versions"][version]["path"]
            return os.path.join(data_dir, rel_path)
            
    # Fallback to directory based version
    fallback_path = os.path.join(data_dir, version_or_path, "mock_dataset.json")
    if os.path.exists(fallback_path):
        return fallback_path
        
    raise FileNotFoundError(f"Dataset version or path not found: {version_or_path}")

def load_json_dataset(filepath: str) -> List[PatientCase]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [PatientCase.from_dict(case) for case in data]

def load_csv_dataset(filepath: str) -> List[PatientCase]:
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
                expected_referral_decision=ReferralDecision(row['expected_referral_decision'])
            )
            cases.append(case)
    return cases

def load_dataset(version_or_path: str = "latest") -> List[PatientCase]:
    filepath = _resolve_dataset_path(version_or_path)
    
    if filepath.endswith('.json'):
        return load_json_dataset(filepath)
    elif filepath.endswith('.csv'):
        return load_csv_dataset(filepath)
    else:
        raise ValueError("Unsupported file format. Must be .json or .csv")
