# 🕸️ Chat-Style RAG Agent

A fully local Retrieval-Augmented Generation (RAG) system for querying U.S. Federal Register documents using a local LLM (via Ollama), automated data ingestion pipeline, and FastAPI interface.

---

## 🔍 Project Objective

Enable users to ask natural language questions about U.S. Federal Register content and receive accurate, contextual answers powered by a local LLM with tool-calling capability.

---

## 📦 Features

* ✅ Automated **Data Pipeline** (Downloader → Processor → Uploader to MySQL)
* ✅ Local **LLM Integration** using **Ollama** (tested with `qwen:0.5b`, `phi3`, `mistral`\*)
* ✅ **FastAPI** server exposing a `/chat` endpoint
* ✅ Tool-based LLM responses:

  * By President & Month
  * By Topic Keyword
  * By Date Range
  * Latest N documents

> ⚠️ Note: Some models (like `qwen:0.5b`) may not support tool-calling. `phi3` works but requires at least \~5GB RAM.

---

## 🗂️ Project Structure

```
├── core/
│   ├── agent.py              # LLM interface + tool handling
│   └── tool_functions.py     # MySQL tool functions
├── data_pipeline/
│   ├── downloader.py         # Fetches latest federal documents
│   ├── processor.py          # Structures/cleans JSON
│   └── uploader.py           # Uploads to MySQL
├── api.py                    # FastAPI server
├── requirements.txt          # Python dependencies
└── .env                      # Env variables (excluded from repo)
```

---

## ⚙️ Setup Instructions

### 1. Clone Repo & Create Virtual Environment

```bash
git clone https://github.com/theraaajj/User-Facing-Chat-Style-RAG-System.git
cd spiderweb-rag-agent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

Include:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_database
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=ollama
```

### 4. Prepare MySQL DB

Ensure your MySQL server is running. Manually create a table:

```sql
```

### 5. Run Ollama Model

Ensure you have enough RAM (\~5GB for `phi3`).

```bash
ollama pull phi3
ollama run phi3
```

### 6. Run the Data Pipeline

```bash
python data_pipeline/downloader.py
python data_pipeline/processor.py
python data_pipeline/uploader.py
```

### 7. Start FastAPI Server

```bash
uvicorn api:app --reload
```

### 8. Test with Postman

Send a POST request:

```
POST http://localhost:8000/chat
Content-Type: application/json
{
  "query": "Tell me about documents signed by President Biden in 2023-01"
}
```

---

## 🛠️ Tech Stack

* Python 3.10+
* FastAPI
* MySQL
* Ollama (Local LLM runner)
* Pydantic, dotenv, mysql-connector-python

---

## 📌 Notes

* Avoid Swagger UI if you're using Postman. (Swagger UI code, commented out!)
* No front-end included (headless API project).
* Ensure system RAM is sufficient for chosen model.

---

## 📃 Deliverables

* ✅ Data pipeline scripts for ingestion into MySQL
* ✅ Agent implementation with tool calling via LLM
* ✅ FastAPI-based backend exposing a `/chat` endpoint
* ✅ Tested with Postman

---

## 📬 Contact

**Raj Aryan**
📧 [theraaajj@gmail.com](mailto:theraaajj@gmail.com)

