
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "synthetic_clinical_events.csv"

REQUIRED_COLUMNS = {"case_id", "activity", "timestamp"}


def load_event_log(path=DATA_FILE):
    """Load the clinical event log."""
    df = pd.read_csv(path)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )
    return df


def validate_event_log(df):
    """Check the event log for basic data-quality issues."""
    results = {
        "row_count": len(df),
        "missing_case_ids": int(df["case_id"].isna().sum()),
        "missing_activities": int(df["activity"].isna().sum()),
        "invalid_timestamps": int(df["timestamp"].isna().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "case_count": int(df["case_id"].nunique()),
        "activity_count": int(df["activity"].nunique()),
    }

    results["valid"] = (
        results["row_count"] > 0
        and results["missing_case_ids"] == 0
        and results["missing_activities"] == 0
        and results["invalid_timestamps"] == 0
    )
    return results


