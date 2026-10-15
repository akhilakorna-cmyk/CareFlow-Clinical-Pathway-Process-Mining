
import pandas as pd


def prepare_event_log(df):
    """Sort events into chronological order within each case."""
    result = df.dropna(
        subset=["case_id", "activity", "timestamp"]
    ).copy()

    return result.sort_values(
        ["case_id", "timestamp"]
    ).reset_index(drop=True)


def calculate_case_durations(df):
    """Calculate elapsed time between first and last event per case."""
    cases = (
        prepare_event_log(df)
        .groupby("case_id")["timestamp"]
        .agg(start_time="min", end_time="max")
        .reset_index()
    )

    cases["duration_hours"] = (
        cases["end_time"] - cases["start_time"]
    ).dt.total_seconds() / 3600

    return cases


def summarize_activities(df):
    """Count events and cases associated with each activity."""
    clean = prepare_event_log(df)

    return (
        clean.groupby("activity")
        .agg(
            event_count=("activity", "size"),
            case_count=("case_id", "nunique"),
        )
        .sort_values("event_count", ascending=False)
        .reset_index()
    )


def get_case_sequences(df):
    """Reconstruct the observed activity sequence for each case."""
    clean = prepare_event_log(df)

    return (
        clean.groupby("case_id")["activity"]
        .agg(list)
        .reset_index(name="activity_sequence")
    )
