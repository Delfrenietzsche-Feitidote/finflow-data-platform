import json
from pathlib import Path


def write_rejected_transactions(
    rejected_transactions: list[dict],
    output_path: str,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(rejected_transactions, file, indent=2)