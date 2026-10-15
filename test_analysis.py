
from src.data_loader import load_event_log, validate_event_log
from src.analysis import (
    prepare_event_log,
    calculate_case_durations,
    summarize_activities,
    get_case_sequences,
)

df = load_event_log()
checks = validate_event_log(df)
clean = prepare_event_log(df)

print("DATA QUALITY")
print(checks)

print("\nCASE DURATIONS")
print(calculate_case_durations(clean).to_string(index=False))

print("\nACTIVITY SUMMARY")
print(summarize_activities(clean).to_string(index=False))

print("\nCASE SEQUENCES")
print(get_case_sequences(clean).to_string(index=False))
