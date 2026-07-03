import pytest
import os
from backend.evaluation.datasets import load_dataset, PatientCase

def test_load_json_dataset():
    # Use the mock dataset generated earlier
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    json_path = os.path.join(base_dir, "data", "eval", "mock_dataset.json")
    
    if os.path.exists(json_path):
        cases = load_dataset(json_path)
        assert len(cases) == 50
        assert isinstance(cases[0], PatientCase)
        assert cases[0].patient_id is not None
        assert isinstance(cases[0].symptoms, list)

def test_load_csv_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    csv_path = os.path.join(base_dir, "data", "eval", "mock_dataset.csv")
    
    if os.path.exists(csv_path):
        cases = load_dataset(csv_path)
        assert len(cases) == 50
        assert isinstance(cases[0], PatientCase)
        assert cases[0].patient_id is not None
        assert isinstance(cases[0].symptoms, list)

def test_load_dataset_invalid_extension():
    with pytest.raises(ValueError):
        load_dataset("invalid_file.txt")
