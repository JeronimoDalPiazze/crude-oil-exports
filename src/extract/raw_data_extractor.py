import os
import logging
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Dict

import pandas as pd
import requests

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("crude_oil_exports_extract")

# Paths configuration
RAW_PATH = Path(os.getenv("RAW_DATA_PATH", "./data/raw"))
DOCS_PATH = Path(os.getenv("DOCS_DATA_PATH", "./data/docs"))

RAW_PATH.mkdir(parents=True, exist_ok=True)
DOCS_PATH.mkdir(parents=True, exist_ok=True)

# Files to download (url + target location)
# target: "raw" -> data/raw, "docs" -> data/docs
FILES: Dict[str, Dict[str, str]] = {
    "crude-oil-exports-by-destination-annual.csv": {
        "url": "https://www.cer-rec.gc.ca/open/imports-exports/crude-oil-exports-by-destination-annual.csv",
        "target": "raw",
    },
    "crude-oil-exports-by-destination-monthly.csv": {
        "url": "https://www.cer-rec.gc.ca/open/imports-exports/crude-oil-exports-by-destination-monthly.csv",
        "target": "raw",
    },
    "crude-oil-exports-by-type-annual.csv": {
        "url": "https://www.cer-rec.gc.ca/open/imports-exports/crude-oil-exports-by-type-annual.csv",
        "target": "raw",
    },
    "crude-oil-exports-by-type-monthly.csv": {
        "url": "https://www.cer-rec.gc.ca/open/imports-exports/crude-oil-exports-by-type-monthly.csv",
        "target": "raw",
    },
    "crude-oil-exports-data-dictionary.csv": {
        "url": "https://www.cer-rec.gc.ca/open/imports-exports/crude-oil-exports-data-dictionary.csv",
        "target": "docs",
    },
}

# Helper functions
def get_output_dir(target: str) -> Path:
    """Map logical target name to actual directory Path."""
    if target == "docs":
        return DOCS_PATH
    return RAW_PATH


def download_csv(name: str, url: str, out_dir: Path) -> None:
    """
    Download a CSV file, validate with pandas, add ingestion_timestamp
    and save to the given directory.
    """
    logger.info(f"Starting download | file={name} | url={url} | out_dir={out_dir}")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while downloading file={name} | url={url} | error={e}")
        # Logs error details including full traceback
        logger.exception("RequestException details")
        return

    try:
        df = pd.read_csv(StringIO(resp.text))
    except Exception as e:
        logger.error(f"Error parsing CSV with pandas | file={name} | error={e}")
        logger.exception("Pandas read_csv error details")
        return

    # Basic validation
    if df.empty:
        logger.warning(f"Downloaded CSV is empty | file={name} | url={url}")
    else:
        logger.info(
            "CSV loaded successfully | file=%s | rows=%d | cols=%d",
            name,
            len(df),
            len(df.columns),
        )

    # Add technical metadata column
    ingestion_ts = datetime.now(timezone.utc).isoformat()
    df["ingestion_timestamp"] = ingestion_ts

    out_path = out_dir / name

    try:
        df.to_csv(out_path, index=False)
    except Exception as e:
        logger.error(f"Error saving CSV to disk | file={name} | path={out_path} | error={e}")
        logger.exception("Error while writing CSV to disk")
        return

    logger.info(
        "File saved successfully | file=%s | path=%s | ingestion_timestamp=%s",
        name,
        out_path,
        ingestion_ts,
    )


def main() -> None:
    logger.info("Starting crude oil exports raw data extraction process")

    for name, meta in FILES.items():
        url = meta["url"]
        target = meta.get("target", "raw")
        out_dir = get_output_dir(target)

        try:
            download_csv(name, url, out_dir)
        except Exception as e:
            # final safety net: prevents the loop from breaking
            logger.error(
                "Unexpected error in download step | file=%s | url=%s | error=%s",
                name,
                url,
                e,
            )
            logger.exception("Unexpected error details")

    logger.info("Finished crude oil exports raw data extraction process")


if __name__ == "__main__":
    main()
