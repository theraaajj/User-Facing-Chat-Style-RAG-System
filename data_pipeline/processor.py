## data_pipeline/processor.py


"""
processor.py

This script processes raw JSON files downloaded by the downloader.
It extracts the required fields and saves them in a structured format.
"""

import os                # For file path and directory operations
import json              # To read and write JSON files
import asyncio           # To manage asynchronous execution
import aiofiles          # For non-blocking file read/write

# Directory containing raw JSON data downloaded from the API
RAW_DATA_DIR = "data_pipeline/raw_data"

# Directory where cleaned, processed data will be stored
PROCESSED_DATA_DIR = "data_pipeline/processed_data"

# Ensure the processed data directory exists
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

async def process_file(file_path):
    """
    Process a single JSON file:
    - Loads raw data from the Federal Register API.
    - Extracts required fields: document_id, title, summary, publication_date, topics, and raw_json.
    - Skips any record missing the required 'document_number' or where it's empty/whitespace.
    - Saves the processed data as a JSON file in the processed data directory.

    Args:
        file_path (str): Path to the raw JSON file.

    Returns:
        None
    """
    print(f"Processing {file_path}...")

    # Asynchronously open the raw JSON file for reading
    async with aiofiles.open(file_path, mode="r") as f:
        raw_content = await f.read()

    # Parse the JSON content into a Python dictionary
    raw_data = json.loads(raw_content)

    # Extract the list of documents from the API response (key: 'results')
    documents = raw_data.get("results", [])

    # List to hold processed documents
    processed_documents = []

    # Iterate through each document and extract required fields
    for doc in documents:
        # Extract the document ID; skip if missing or empty
        doc_id = (doc.get("document_number") or "").strip()
        if not doc_id:
            print(f"⚠️ Skipping document with missing or empty 'document_number'.")
            continue

        # Construct a dictionary with required fields
        processed_doc = {
            "document_id": doc_id,
            "title": doc.get("title"),
            "summary": doc.get("summary", ""),  # Default to empty string if summary is missing
            "publication_date": doc.get("publication_date"),
            "topics": ", ".join(doc.get("topics", [])),  # Convert list of topics to a single comma-separated string
            "raw_json": json.dumps(doc)  # Store the entire raw document as a JSON string
        }

        # Append the processed document to the list
        processed_documents.append(processed_doc)

    # Construct the filename for the processed JSON file (same name as the raw file)
    filename = os.path.basename(file_path)
    processed_file_path = os.path.join(PROCESSED_DATA_DIR, filename)

    # Asynchronously write the processed documents to the processed file
    async with aiofiles.open(processed_file_path, mode="w") as f:
        await f.write(json.dumps(processed_documents, indent=2))

    print(f"✅ Processed data saved to {processed_file_path}")

async def process_all_files():
    """
    Process all JSON files found in the RAW_DATA_DIR.
    - Calls process_file() for each JSON file concurrently.
    - Prints a message if no raw data files are found.

    Returns:
        None
    """
    # Get a list of all JSON files in the raw data directory
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".json")]

    if not files:
        print("⚠️ No raw data files found to process.")
        return

    # Create a list of tasks to process all files asynchronously
    tasks = []
    for file_name in files:
        file_path = os.path.join(RAW_DATA_DIR, file_name)
        tasks.append(process_file(file_path))

    # Execute all tasks concurrently using asyncio.gather()
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Entry point for standalone execution
    # Starts the asynchronous processing of all files
    asyncio.run(process_all_files())


# This script processes all raw JSON files downloaded by the downloader.
# It extracts the required fields and saves them in a structured format