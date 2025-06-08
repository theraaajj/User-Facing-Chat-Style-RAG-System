
## This will fetch data from the Federal Register API for the last week (daily updating).

## data_pipeline/downloader.py

import aiohttp          # Async HTTP client to make non-blocking requests to the API
import asyncio          # For running asynchronous functions and event loop management
import datetime         # To work with dates for filtering data in the API calls
import aiofiles         # For asynchronous file I/O operations, to save data without blocking
import os               # To create directories if they don't exist
import json             # To parse and write JSON data

# Directory to save raw downloaded JSON data
RAW_DATA_DIR = "data_pipeline/raw_data"

# Create the directory if it doesn't exist yet, so saving files won't fail
os.makedirs(RAW_DATA_DIR, exist_ok=True)

async def fetch_data(session, start_date, end_date, page=1):
    """
    Fetch one page of documents from the Federal Register API filtered by date.
    
    Args:
        session: aiohttp ClientSession object for reusing connections.
        start_date: str, start date in 'YYYY-MM-DD' format to filter documents.
        end_date: str, end date in 'YYYY-MM-DD' format.
        page: int, the page number to fetch from the API.

    Returns:
        JSON response parsed into a Python dictionary.
    """
    # Construct the API URL with query parameters for date range and pagination
    url = (
        "https://www.federalregister.gov/api/v1/documents.json"
        f"?conditions[publication_date][gte]={start_date}"
        f"&conditions[publication_date][lte]={end_date}"
        f"&page={page}"
        f"&per_page=100"  # max allowed results per page (helps reduce total requests)
    )
    
    # Make an asynchronous GET request to the API endpoint
    async with session.get(url) as response:
        # Await the response and parse it as JSON
        data = await response.json()
        return data

async def download_all(start_date, end_date):
    """
    Download all pages of data for the given date range and save each page as a JSON file.
    
    Args:
        start_date: str, starting date (YYYY-MM-DD)
        end_date: str, ending date (YYYY-MM-DD)
    """
    # Create a single reusable session for all requests (efficient TCP connection reuse)
    async with aiohttp.ClientSession() as session:
        page = 1  # Start fetching from page 1
        
        while True:
            print(f"Downloading page {page}...")

            # Fetch data for the current page asynchronously
            data = await fetch_data(session, start_date, end_date, page)
            
            # Extract the list of documents in this page from the 'results' field
            results = data.get("results", [])
            
            # If no documents found, end the loop (no more pages)
            if not results:
                print("No more data available. Download complete.")
                break
            
            # Construct the filename for this page's data (e.g., raw_data/data_page_1.json)
            filename = os.path.join(RAW_DATA_DIR, f"data_page_{page}.json")
            
            # Open the file asynchronously in write mode to save the JSON data
            async with aiofiles.open(filename, "w") as f:
                # Write pretty-formatted JSON string to file
                await f.write(json.dumps(data, indent=2))
            
            print(f"Saved page {page} data to {filename}")
            
            # Check if we have reached the last page, stop if yes
            total_pages = data.get("total_pages", page)
            if page >= total_pages:
                print("Reached the last page of data.")
                break
            
            # Move to the next page for next iteration
            page += 1

if __name__ == "__main__":
    # Calculate the date range: last 60 days from today
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=60)
    
    # Convert dates to string format required by API
    start_date_str = start_date.isoformat()  # YYYY-MM-DD
    end_date_str = end_date.isoformat()
    
    # Run the asynchronous download_all function in the event loop
    asyncio.run(download_all(start_date_str, end_date_str))

## This script will download all pages of data from the Federal Register API
## for the last 60 days and save each page as a separate JSON file in the specified directory.




