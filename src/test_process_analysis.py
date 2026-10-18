
import pandas as pd

from src.process_analysis import (
    calculate_durations,
    summarize_activities,
    reconstruct_journeys,
    detect_delays,
)

DATA_PATH = "data/synthetic_clinical_events.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    events, case_durations = calculate_durations(df)

    print("\n--- CASE DURATIONS (HOURS) ---")
    print(case_durations.round(2).to_string(index=False))

    print("\n--- ACTIVITY SUMMARY ---")
    print(summarize_activities(events).round(2).to_string(index=False))

    print("\n--- CASE JOURNEYS ---")
    print(reconstruct_journeys(events).to_string(index=False))

    print("\n--- POTENTIAL DELAYS (2 HOURS OR MORE) ---")
    delays = detect_delays(events, threshold_hours=2.0)

    if delays.empty:
        print("No transitions meet the selected threshold.")
    else:
       print(
    delays.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)


if __name__ == "__main__":
    main()
