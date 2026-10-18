
import pandas as pd


def prepare_events(df):
    """Validate and sort the clinical event log."""
    required = {"case_id", "activity", "timestamp"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}. "
            f"Available columns: {list(df.columns)}"
        )

    events = df.copy()
    events["timestamp"] = pd.to_datetime(
        events["timestamp"], errors="coerce"
    )

    events = events.dropna(
        subset=["case_id", "activity", "timestamp"]
    )

    events = events.sort_values(
        ["case_id", "timestamp"]
    ).reset_index(drop=True)

    return events


def calculate_durations(df):
    """Calculate time between events and total case duration."""
    events = prepare_events(df)

    # Find the next event within each case
    events["next_timestamp"] = (
        events.groupby("case_id")["timestamp"].shift(-1)
    )

    events["next_activity"] = (
        events.groupby("case_id")["activity"].shift(-1)
    )

    # Calculate the gap between consecutive events
    events["gap_hours"] = (
        events["next_timestamp"] - events["timestamp"]
    ).dt.total_seconds() / 3600

    # Calculate total duration for each case
    case_durations = (
        events.groupby("case_id")["timestamp"]
        .agg(first_event="min", last_event="max")
        .reset_index()
    )

    case_durations["case_duration_hours"] = (
        case_durations["last_event"] - case_durations["first_event"]
    ).dt.total_seconds() / 3600

    return events, case_durations



def summarize_activities(events):
    """Summarize activity frequency and outgoing time gaps."""
    summary = (
        events.groupby("activity")
        .agg(
            event_count=("activity", "size"),
            average_gap_hours=("gap_hours", "mean"),
            maximum_gap_hours=("gap_hours", "max"),
        )
        .reset_index()
    )

    return summary.sort_values(
        "event_count", ascending=False
    )


def reconstruct_journeys(events):
    """Build the ordered activity sequence for every case."""
    journeys = (
        events.groupby("case_id")["activity"]
        .agg(list)
        .reset_index(name="activities")
    )

    journeys["activity_sequence"] = journeys["activities"].apply(
        lambda activities: " → ".join(activities)
    )

    return journeys[["case_id", "activity_sequence"]]



def detect_delays(events, threshold_hours=2.0):
    """Find transitions whose elapsed time meets the threshold."""
    delays = events.loc[
        events["next_timestamp"].notna()
        & (events["gap_hours"] >= threshold_hours)
    ].copy()

    delays["from_activity"] = delays["activity"]
    delays["to_activity"] = delays["next_activity"]

    return delays[
        [
            "case_id",
            "from_activity",
            "to_activity",
            "timestamp",
            "next_timestamp",
            "gap_hours",
        ]
    ].sort_values("gap_hours", ascending=False)
