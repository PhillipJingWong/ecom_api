import uuid
from pydantic import BaseModel, Field
from datetime import date

class UploadCSV(BaseModel):
    file_id: str
    filename: str

class SummaryQuery(BaseModel):
    file_id: str = Field(..., description="Uploaded CSV file ID")
    user_id: str = Field(..., description="User ID")
    start: date = Field(..., description="Start date formatted YYYY-MM-DD")
    end: date = Field(..., description="End date formatted YYYY-MM-DD")

class SummaryResult(BaseModel):
    user_id: str
    max_amount: float | None
    min_amount: float | None
    mean_amount: float | None