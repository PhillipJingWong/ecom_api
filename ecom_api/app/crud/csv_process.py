import pandas as pd
from fastapi import HTTPException
from pathlib import Path
from app.core.config import UPLOAD_DIR, CHUNKSIZE

#save the csv uploaded by the user
def save_csv(file_path: Path, file_contents: bytes):
    #save the uploaded csv locally
    with open(file_path, "wb") as f:
        f.write(file_contents)

#provide summary data for the specified file
def summarise(filename: str, user_id: str, start_date: str, end_date: str, chunk: int=CHUNKSIZE)->dict[str, any]:

    #store totals
    total_sum = 0.0
    total_count = 0
    total_max = None
    total_min = None

    try:
        start_timestamp = pd.to_datetime(start_date, errors="raise")
        end_timestamp = pd.to_datetime(end_date, errors="raise") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format")

    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        chunks = pd.read_csv(file_path, chunksize=chunk)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read CSV")

    #try first chunk to validate
    try:
        first_chunk=next(chunks)
    except StopIteration:
        return{"user_id": user_id, "max_amount": None, "min_amount": None, "mean_amount": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read CSV")

    first_chunk.columns = first_chunk.columns.str.lower().str.strip()
    # validate required columns
    if "user_id" not in first_chunk.columns or "transaction_amount" not in first_chunk.columns or "timestamp" not in first_chunk.columns:
        raise HTTPException(status_code=400, detail="CSV missing required columns")

    #process first chunk and remaining ones
    def process_chunk(df_chunk: pd.DataFrame):
        nonlocal total_sum, total_count, total_max, total_min

        #standardise column names to lowercase and strip spaces
        df_chunk.columns = df_chunk.columns.str.lower().str.strip()

        #convert timestamp
        df_chunk["timestamp"] = pd.to_datetime(df_chunk["timestamp"], dayfirst=True, errors="coerce")
        
        #start with the user mask
        mask = df_chunk["user_id"].astype(str).str.strip().str.lower() == str(user_id).strip().lower()        
        
        #filter out rows with invalid timestamps
        mask &= df_chunk["timestamp"].notna()
        
        # filter by start and end date explicitly
        mask &= df_chunk["timestamp"] >= start_timestamp
        mask &= df_chunk["timestamp"] <= end_timestamp
        
        filtered = pd.to_numeric(df_chunk.loc[mask, "transaction_amount"], errors="coerce").dropna()
        
        #debugging print statements
        #print("first 5 rows:", df_chunk.head())
        #print("rows matching user:", mask.sum())
        #print("transaction amount sum filtered rows", filtered.sum() if not filtered.empty else "empty")
        
        if filtered.empty:
            return

        total_sum += float(filtered.sum())
        total_count += int(filtered.count())

        # update running max/min
        chunk_max = filtered.max()
        chunk_min = filtered.min()
        total_max = float(chunk_max) if total_max is None else max(total_max, float(chunk_max))
        total_min = float(chunk_min) if total_min is None else min(total_min, float(chunk_min))

    # process the already-read first chunk, then the remaining chunks
    process_chunk(first_chunk)
    for each in chunks:
        process_chunk(each)

    # compute mean if any values found
    mean_amount = (total_sum / total_count) if total_count > 0 else None
    
    return {"user_id": user_id, "max_amount": total_max, "min_amount": total_min, "mean_amount": mean_amount}