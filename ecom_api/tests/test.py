import sys
from pathlib import Path
import pandas as pd
import pytest
from fastapi import HTTPException

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.crud.csv_process import summarise, UPLOAD_DIR

#test csv paths
TESTS_DIR = Path(__file__).parent
VALID_FILE = TESTS_DIR / "valid.csv"
EMPTY_FILE = TESTS_DIR / "empty.csv"

#valid CSV test
def test_valid_csv():
    data = [
        {"transaction_id": "aaa1", "user_id": 1, "product_id": 3, "timestamp": "10/09/2025 01:00:00", "transaction_amount": 123.1},
        {"transaction_id": "aaa2", "user_id": 1, "product_id": 4, "timestamp": "14/09/2025 23:00:00", "transaction_amount": 999.0}]
    pd.DataFrame(data).to_csv(VALID_FILE, index=False)

    result = summarise(str(VALID_FILE), user_id=1, start_date="2025-09-10", end_date="2025-09-14")
    assert result["max_amount"] == 999.0
    assert result["min_amount"] == 123.1
    assert result["mean_amount"] == 561.05
    print (result)

#empty CSV test
def test_empty_csv():
    pd.DataFrame(columns=["transaction_id", "user_id", "product_id", "timestamp", "transaction_amount"]).to_csv(EMPTY_FILE, index=False)

    result = summarise(str(EMPTY_FILE), user_id=1, start_date="2025-09-10", end_date="2025-09-14")
    assert result["max_amount"] is None
    assert result["min_amount"] is None
    assert result["mean_amount"] is None

#invalid query test (invalid date)
def test_invalid_date():
    data = [{"transaction_id": "aaa1", "user_id": 1, "product_id": 99,
             "timestamp": "10/09/2025 01:00:00", "transaction_amount": 42}]
    pd.DataFrame(data).to_csv(VALID_FILE, index=False)

    with pytest.raises(HTTPException) as e:
        summarise(str(VALID_FILE), user_id=1, start_date="abcdefg", end_date="14/09/2025")
    assert e.value.status_code == 400
    assert "Invalid date format" in e.value.detail