"""Output boundary: save results without performing any analysis or calibration.

These are small file-writing services, not servers. Raw input stays in data/;
new products go to output/. The finite snapshot writers replace their target.
"""
import json
import csv
from pathlib import Path
from typing import Union
from records import FIELDS


# Union[dict, list] means a dictionary or a list, without Python 3.10 union syntax.
def save_json(path: Path, data: Union[dict, list]) -> None:
    """WORKED EXAMPLE: write a readable JSON snapshot and create its parent folder."""
    # Serialise first: a non-serialisable value must not truncate an existing file.
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")


def save_csv(path: Path, readings: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(readings)



def save_jsonl(path: Path, readings: list[dict]) -> None:
    text = ""
    for row in readings:
        text += json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    
    
