import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from io import BytesIO
import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.core.config import UPLOAD_DIR

#import pydantic models to validate requests/responses
from app.models.csv_models import UploadCSV, SummaryQuery, SummaryResult

#import crud functions
from app.crud.csv_process import save_csv, summarise

router=APIRouter()

#logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger=logging.getLogger(__name__)

#upload file
#ensures the file is a .csv, uploads with a uuid and returns it.
#data streamed in chunks for performance and reliability.
#first row parsed to validate it.
@router.post("/upload", response_model=UploadCSV)
async def upload(file:UploadFile=File(...)):
    
    suffix = Path(file.filename).suffix.lower()
    if suffix != ".csv":
        logger.warning("Invalid file uploaded: wrong extension: %s", file.filename)
        raise HTTPException(status_code=400, detail="Invalid file uploaded: must be .csv")

    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}.csv"
    save_path = UPLOAD_DIR / stored_filename
    
    try:
        with save_path.open("wb") as output:
            while chunk:=await file.read(1024*1024):
                output.write(chunk)
        
        #validate the csv file is valid by reading it
        try:
            pd.read_csv(save_path, nrows=1)
        except Exception:
            #remove the file
            save_path.unlink(missing_ok=True)
            logger.warning("Invalid file uploaded")
            raise HTTPException(status_code=400, detail="Invalid file uploaded")        
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    logger.info(f"{file.filename} uploaded as {stored_filename}")
    return UploadCSV(file_id=file_id, filename=file.filename)

#return summary statistics (max, min and mean) for a user's transactions in a given date range from an uploaded csv.
@router.post("/summary", response_model = SummaryResult)
def summary_get(query: SummaryQuery):
    
    output=summarise(filename=f"{query.file_id}.csv", user_id=query.user_id, start_date=query.start, end_date=query.end)
    
    #dict converted to pydantic model for validation
    return SummaryResult(**output)
        
#test route
@router.get("/hello")
async def hello():
    return {"message": "Hello world!"}