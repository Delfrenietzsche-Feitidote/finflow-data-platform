from finflow.common.config import settings
from finflow.ingestion.pipeline import run_ingestion


def test_run_ingestion(tmp_path, monkeypatch):
    raw_path = tmp_path / "raw"
    rejected_path = tmp_path / "rejected"

    monkeypatch.setattr(
        settings.storage,
        "raw_path",
        f"{raw_path}/",
    )

    monkeypatch.setattr(
        settings.storage,
        "rejected_path",
        f"{rejected_path}/",
    )

    run_ingestion(10)

    output_file = (
        raw_path
        / "transactions"
        / str(settings.pipeline.batch_date)
        / "transactions.json"
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0