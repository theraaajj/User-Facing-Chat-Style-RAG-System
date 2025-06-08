## data_pipeline/constants.py

BASE_API_URL = "https://www.federalregister.gov/api/v1/documents.json"
PARAMS = {
    "per_page": 100,
    "order": "newest",
    "conditions[publication_date][gte]": "2025-01-01",
    "conditions[publication_date][lte]": "2025-12-31",
    "fields[]": [
        "title", "document_number", "publication_date",
        "type", "agency_names", "html_url"
    ]
}
