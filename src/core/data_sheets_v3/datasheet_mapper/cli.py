"""Command-line interface for the Datasheet Mapper."""
import pathlib
import json
import argparse
import datetime
import logging

from .config import load_schema
from .agent import DatasheetMapperAgent

logging.basicConfig(level=logging.INFO)

DEFAULT_RAW = "data/raw_data.json"
DEFAULT_SCHEMA = "data/schemas/water_tank_schema.json"


def main() -> None:
    """Main function to run the Datasheet Mapper CLI."""
    p = argparse.ArgumentParser()
    p.add_argument(
        "raw_json",
        nargs="?",
        default=DEFAULT_RAW,
        help=f"raw tables file (default: {DEFAULT_RAW})",
    )
    p.add_argument(
        "schema_json",
        nargs="?",
        default=DEFAULT_SCHEMA,
        help=f"canonical schema (default: {DEFAULT_SCHEMA})",
    )
    args = p.parse_args()

    raw_tables = json.load(open(args.raw_json, "r", encoding="utf-8"))
    schema = load_schema(pathlib.Path(args.schema_json))

    mapper = DatasheetMapperAgent(schema)
    mapper.run(raw_tables)

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = pathlib.Path("outputs")
    out.mkdir(exist_ok=True)
    out_file = out / f"{pathlib.Path(args.raw_json).stem}_{ts}_canonical.json"
    out_file.write_text(json.dumps(mapper.store.data, indent=2, ensure_ascii=False))
    print("→ canonical JSON saved:", out_file)


if __name__ == "__main__":
    main()
