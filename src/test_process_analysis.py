
import pandas as pd

from src.process_analysis import (
    calculate_durations,
    summarize_activities,
    reconstruct_journeys,
    detect_delays,
)


def sample_events():
    """Create a small, predictable dataset for testing."""
    return pd.DataFrame({
        "case_id": ["C001", "C001", "C001", "C002", "C002"],
        "activity": [
            "Registration",
            "Lab Test",
            "Discharge",
            "Registration",
            "Discharge",
        ],
        "timestamp": [
            "2026-09-01 08:00:00",
            "2026-09-01 09:00:00",
            "2026-09-01 12:00:00",
            "2026-09-02 08:00:00",
            "2026-09-02 10:00:00",
        ],
    })


def test_calculate_durations():
    events, durations = calculate_durations(sample_events())

    assert len(events) == 5
    assert len(durations) == 2

    case_1 = durations.loc[
        durations["case_id"] == "C001",
        "case_duration_hours",
    ].iloc[0]

    assert case_1 == 4.0


def test_summarize_activities():
    events, _ = calculate_durations(sample_events())
    summary = summarize_activities(events)

    assert "activity" in summary.columns
    assert "event_count" in summary.columns
    assert summary["event_count"].sum() == 5


def test_reconstruct_journeys():
    events, _ = calculate_durations(sample_events())
    journeys = reconstruct_journeys(events)

    assert len(journeys) == 2
    assert "Registration" in journeys.iloc[0]["activity_sequence"]
    assert "Lab Test" in journeys.iloc[0]["activity_sequence"]
    assert "Discharge" in journeys.iloc[0]["activity_sequence"]
    
def test_detect_delays():
    events, _ = calculate_durations(sample_events())
    delays = detect_delays(events, threshold_hours=2.0)

    assert not delays.empty
    assert (delays["gap_hours"] >= 2.0).all()

