# crude-oil-exports
Data Engineering project with ingestion in Python, storage in DuckDB, modeling in dbt Core, and orchestration with Prefect. It transforms crude oil export data and delivers structured analytical models for use in Metabase dashboards.

---

## 📥 Extract Layer (Current Stage)

The Extract layer implements the ingestion pipeline responsible for downloading all raw datasets from the Canada Energy Regulator (CER).  
It organizes the data into structured folders (`data/raw` and `data/docs`) and attaches technical metadata to ensure traceability.

### 🔹 What this stage does
- Downloads 5 public CSV datasets from CER:
  - Annual exports by destination  
  - Monthly exports by destination  
  - Annual exports by type  
  - Monthly exports by type  
  - Official data dictionary  
- Validates and loads each CSV using `pandas`
- Adds an `ingestion_timestamp` column
- Saves raw datasets into `data/raw/`
- Saves data dictionary into `data/docs/`
- Implements structured logging for observability and debugging

### 🔹 How to run the Extract pipeline

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Create a .env file in the project root:
    ```bash
    RAW_DATA_PATH="data/raw"
    DOCS_DATA_PATH="data/docs"
    ```

3. Run the extractor:
    ```bash
    python -m src.extract.raw_data_extractor
    ```

## 📁 Project Structure

```graphql
crude-oil-exports/
├── data/
│   ├── raw/                   # Raw datasets downloaded from CER
│   └── docs/                  # Official data dictionary and metadata
│
├── src/
│   ├── config.py              # Loads environment variables and resolves paths
│   └── extract/
│       ├── __init__.py
│       └── raw_data_extractor.py   # Main ingestion script (Extract Layer)
│
├── warehouse/                 # DuckDB database (Load Layer)
│
├── dbt/                       # Transformation Layer (dbt Core)
│   ├── models/
│   ├── profiles/
│   └── dbt_project.yml
│
├── .env
├── .env.example
├── requirements.txt
└── README.md
```


## 🧰 Tech Stack

This project follows a modern ELT architecture using:

### **Extract**
- Python  
- pandas  
- requests  
- Structured logging  
- Environment configuration via `.env`

### **Load**
- DuckDB (local analytical warehouse)

### **Transform**
- dbt Core (DuckDB adapter)

### **Orchestration (future)**
- Prefect

### **Visualization**
- Metabase (reading directly from DuckDB)

---

## 🚀 Roadmap

### ✔️ **Extract Layer (Current)**
Raw data ingestion and storage.

### 🔄 **Transform Layer (Next)**
- Build dbt staging models  
- Clean and standardize column names  
- Cast data types  
- Implement tests (`unique`, `not_null`, `accepted_values`)  
- Create `dim` and `fact` models  

### 📦 **Load Layer**
- Generate DuckDB file in `warehouse/`  
- Optimize table formats and indexes  

### 📊 **Analytics & Visualization**
- Connect Metabase directly to DuckDB  
- Build dashboards:
  - Monthly export trends  
  - Top destinations  
  - Export volumes by type  
  - Year-over-year comparisons  
