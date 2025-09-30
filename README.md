<h2>Ecom Summarisation API</h2>

This API enables users to upload a CSV dataset file, which then allows them to query it in order to get summary statistics (max, min and mean) for a specific user's transactions within specified dates.

To use:  
Change directory to ecom_api.  
Run: uvicorn app.main:app --reload

<h3>Endpoints:</h3>

**POST /upload**
Upload a csv file

Response: 200 { "file_id": "\<uuid>", "filename": "original_name.csv" }

**POST /summary** (json body with file_id, user_id, start and end)

Calculates the "max", "min", and "mean" "transaction_amount" for a specified "user_id" between the specified "start" and "end" dates.

Request example:
```json
{
  "file_id": "47eaa002-e9d9-4800-922b-cb3502e84e82",
  "user_id": "316",
  "start": "2023-09-28",
  "end": "2025-09-28"
}
```

Response:
```json
{
  "user_id": "316",
  "max_amount": 499.56,
  "min_amount": 7.17,
  "mean_amount": 248.86684523809518
}
```

**Requirements:**

Python 3.10+
venv
fastapi
uvicorn
pandas
python-multipart
pytest

**Expected CSV schema:**

Required:  
user_id  
timestamp  
transaction_amount

Optional:  
transaction_id  
product_id

**Timestamp Formatting:**

csv data timestamp format: dd/mm/yyyy 00:00:00  
API query start/end dates - ISO format: yyyy-mm-dd

**Notes:**

Uploaded files are saved in an uploads directory as "uuid.csv".
