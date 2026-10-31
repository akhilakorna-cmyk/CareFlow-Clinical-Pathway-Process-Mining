
from pathlib import Path
import pandas as pd

# Project configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "synthetic_clinical_events.csv"

# Required columns for clinical event logs
REQUIRED_COLUMNS = {"case_id", "activity", "timestamp"}


def load_event_log(path=DATA_FILE):
    """
    Load and preprocess the clinical event log.
    """

    df = pd.read_csv(path)

    # Check required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Clean case IDs and activity names
    df["case_id"] = df["case_id"].astype("string").str.strip()
    df["activity"] = df["activity"].astype("string").str.strip()

    # Convert timestamp column into datetime format
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    return df


def validate_event_log(df):
    """
    Validate the clinical event log and identify
    common data-quality issues.
    """

    # Check required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Calculate missing values
    missing_case_ids = (
        df["case_id"].isna()
        | df["case_id"].astype("string").str.strip().eq("")
    )

    missing_activities = (
        df["activity"].isna()
        | df["activity"].astype("string").str.strip().eq("")
    )

    # Validate timestamps
    timestamps = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Generate data-quality report
    results = {
        "row_count": len(df),
        "missing_case_ids": int(missing_case_ids.sum()),
        "missing_activities": int(missing_activities.sum()),
        "invalid_timestamps": int(timestamps.isna().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "case_count": int(df["case_id"].nunique()),
        "activity_count": int(df["activity"].nunique()),
        "out_of_order_events": 0,
    }

    # Check event ordering within each case
    valid_cases = (
        df["case_id"].notna()
        & df["case_id"].astype("string").str.strip().ne("")
    )

    ordered_data = pd.DataFrame({
        "case_id": df.loc[valid_cases, "case_id"],
        "timestamp": timestamps.loc[valid_cases],
    }).dropna()

    for _, group in ordered_data.groupby("case_id", sort=False):
        if not group["timestamp"].is_monotonic_increasing:
            results["out_of_order_events"] += 1

    # Overall validation status
    results["valid"] = (
        results["row_count"] > 0
        and results["missing_case_ids"] == 0
        and results["missing_activities"] == 0
        and results["invalid_timestamps"] == 0
        and results["duplicate_rows"] == 0
    )

    return results
