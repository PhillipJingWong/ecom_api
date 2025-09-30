# Approach Documentation
This document outlines the approaches taken during development and suggestions for improvements:

As the project is a small prototype, I've used a file type structure rather than a feature/domain-based structure - which would be preferred for scaling.

Uploaded CSVs are saved in an uploads folder with a uuid as the filename, which is then used to select data for analysis.

CSVs are broken down and processed in chunks so prevent loading large files in memory.

Pydantic models are used to validate query parameters and responses (UploadCSV, SummaryQuery, SummaryResult).

Simple validation and error handling has been added such as to check the uploaded file extension and required columns.

Simple tests with pytest have been implemented to test a CSV with valid data, an empty CSV and a CSV with invalid data.

For concurrent requests, the upload endpoint is async and uses await, so while clients are sending, the worker isn't CPU blocked. Multiple upload requests can be accepted concurrently.

Used a virtual environment to isolate the project from the system python for reliability and consistent testing.

Code is separated into modules for easier reading and future scalability.

Endpoints return meaningful status codes for debugging such as 400 for bad inputs and 500 for internal errors.

## Future improvements:
Support different date formatting for CSV files uploaded, start and end date format querying etc.

Set a max upload size

Once uploaded, possibly preprocess and store.

Add more test cases for edge cases, invalid, valid and borderline data.

Improve concurrency by using a thread pool.