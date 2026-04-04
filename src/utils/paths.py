# src/utils/paths.py

from pathlib import Path

def get_pipeline_log_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    log_path = repo_root / "logs" / "pipeline.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return log_path