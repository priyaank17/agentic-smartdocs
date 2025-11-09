"""Extract structured data from PDF(s) using Landing AI Agentic-Document-Analysis."""

from __future__ import annotations

import json
import os
import pathlib
import time
import concurrent.futures as cf
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------------------------- #
VA_API_KEY: str = os.getenv("VA_API_KEY", "")
HEADERS = {"Authorization": f"Basic {VA_API_KEY}"}
BASE_URL = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"

CONNECT_TIMEOUT = 10  # seconds
READ_TIMEOUT = 300  # seconds per chunk
MAX_RETRIES = 3
POLL_INTERVAL = 15  # seconds

OUTPUT_DIR = pathlib.Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------------------- #
def extract_one(pdf_path: pathlib.Path, schema: Dict[str, Any]) -> pathlib.Path:
    """Submit one PDF and poll until Landing AI returns extracted_schema."""
    files = {"pdf": (pdf_path.name, pdf_path.open("rb"), "application/pdf")}
    payload = {"fields_schema": json.dumps(schema)}

    # First request ----------------------------------------------------------------
    try:
        resp = requests.post(
            BASE_URL,
            headers=HEADERS,
            files=files,
            data=payload,
            timeout=(CONNECT_TIMEOUT, None),
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Initial request failed for {pdf_path.name}: {exc}"
        ) from exc

    # 202 Accepted  →  async job; Location header gives polling URL
    if resp.status_code == 202:
        status_url = resp.headers["Location"]
    else:
        status_url = None

    # 206 Partial or 200 Success can arrive immediately
    if resp.status_code in (200, 206):
        body = resp.json()
    else:
        # Unexpected
        raise RuntimeError(
            f"{pdf_path.name}: HTTP {resp.status_code} – {resp.text[:300]}"
        )
    # ↓↓↓ add these two lines ↓↓↓
    if resp.status_code == 206 and "data" in body and "status" not in body:
        body["status"] = "partial"

    if "status" not in body:
        debug_file = OUTPUT_DIR / f"{pdf_path.stem}_error.json"
        debug_file.write_text(json.dumps(body, indent=2, ensure_ascii=False))
        err_msg = body.get("error", {}).get("message", "<no message>")
        raise RuntimeError(
            f"{pdf_path.name}: unexpected response ({resp.status_code}) – {err_msg}\n"
            f"Full payload saved to {debug_file}"
        )

    # Poll loop if needed ----------------------------------------------------------
    retries = 0
    while status_url and body.get("status") == "processing":
        time.sleep(POLL_INTERVAL)
        try:
            body = requests.get(
                status_url,
                headers=HEADERS,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            ).json()
        except requests.RequestException as exc:
            retries += 1
            if retries > MAX_RETRIES:
                raise RuntimeError(f"{pdf_path.name}: polling failed – {exc}") from exc
            time.sleep(POLL_INTERVAL * retries)  # exponential back-off
            continue

    # Final verification -----------------------------------------------------------
    if body.get("status") not in ("success", "partial"):
        raise RuntimeError(f"{pdf_path.name}: extractor returned {body.get('status')}")

    # >>> INSIGHT PRINT BLOCK (add here)
    run_logs = body.get("logs") or body.get("data", {}).get("logs")
    if run_logs:
        print(f"— Landing-AI run-logs for {pdf_path.name} —")
        for line in run_logs:
            print("   ", line)
        print("— end logs —\n")
    # <<<

    extracted = body.get("data", {}).get("extracted_schema", {})

    out_file = OUTPUT_DIR / f"{pdf_path.stem}_extracted.json"
    out_file.write_text(json.dumps(extracted, indent=2, ensure_ascii=False))
    print(f"✔ {pdf_path.name} → {out_file.name}  ({len(extracted)} top-level keys)")
    return out_file


# --------------------------------------------------------------------- #
# --------------------------------------------------------------------- #
def extract_many(pdf_paths: List[pathlib.Path], schema_path: pathlib.Path) -> None:
    """Run extraction on a list of PDFs using a thread pool."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    with cf.ThreadPoolExecutor(max_workers=min(4, len(pdf_paths))) as pool:
        futures = {pool.submit(extract_one, path, schema): path for path in pdf_paths}

        for fut in cf.as_completed(futures):
            pdf = futures[fut]
            try:
                fut.result()
            except Exception as err:  # pylint: disable=broad-except
                print(f"✖ {pdf.name}: {err}")


# --------------------------------------------------------------------- #
#   4.  Entry-point                                                      #
# --------------------------------------------------------------------- #
if __name__ == "__main__":
    schema = json.loads(
        open("data/schemas/water_tank_schema.json", encoding="utf-8").read()
    )
    extract_one(
        pathlib.Path("data/document_5a847846-368e-4f7a-a107-ec130083d6ce.pdf"), schema
    )
