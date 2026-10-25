
import streamlit as st
import pandas as pd
from pathlib import Path

from src.process_analysis import (
    calculate_durations,
    summarize_activities,
    detect_delays,
)

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="CareFlow: Clinical Pathway Process Mining",
    layout="wide",
)

st.title("CareFlow: Clinical Pathway Process Mining")

st.warning(
    "DEMO ONLY — This dashboard uses synthetic data, "
    "not real patient records."
)

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------
data_file = (
    Path(__file__).parent
    / "data"
    / "synthetic_clinical_events.csv"
)

if not data_file.exists():
    st.error(
        "Dataset not found. Check the data folder "
        "and CSV filename."
    )
    st.stop()

try:
    df = pd.read_csv(data_file)
except (OSError, pd.errors.ParserError) as error:
    st.error(f"Could not read the dataset: {error}")
    st.stop()

# Check required columns before analysis
required_columns = {"case_id", "activity", "timestamp"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(
        f"Missing required columns: {sorted(missing_columns)}"
    )
    st.stop()

# Preserve original data for quality checks
raw_df = df.copy()

# Validate timestamps and required values
df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce",
)

missing_ids = int(df["case_id"].isna().sum())
missing_activities = int(df["activity"].isna().sum())
invalid_timestamps = int(df["timestamp"].isna().sum())
duplicate_rows = int(raw_df.duplicated().sum())

# Remove invalid events for subsequent analysis
df = df.dropna(
    subset=["case_id", "activity", "timestamp"]
).copy()

df = df.sort_values(
    ["case_id", "timestamp"]
).reset_index(drop=True)

if df.empty:
    st.error(
        "No valid events are available for analysis. "
        "Please check the dataset."
    )
    st.stop()

# --------------------------------------------------
# 3. OVERALL METRICS
# --------------------------------------------------
case_count = df["case_id"].nunique()
event_count = len(df)
activity_count = df["activity"].nunique()

case_durations = (
    df.groupby("case_id")["timestamp"]
    .agg(start_time="min", end_time="max")
)

case_durations["hours"] = (
    case_durations["end_time"]
    - case_durations["start_time"]
).dt.total_seconds() / 3600

average_duration = case_durations["hours"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Cases", case_count)
col2.metric("Total Events", event_count)
col3.metric("Unique Activities", activity_count)
col4.metric(
    "Average Case Duration",
    f"{average_duration:.2f} hours",
)

# --------------------------------------------------
# 4. ACTIVITY FREQUENCY
# --------------------------------------------------
st.subheader("Activity Frequency")

activity_frequency = (
    df["activity"]
    .value_counts()
    .rename_axis("Activity")
    .to_frame("Event Count")
)

st.bar_chart(activity_frequency)

# --------------------------------------------------
# 5. CASE DURATIONS AND ACTIVITY SEQUENCES
# --------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Case Duration (Hours)")
    st.bar_chart(case_durations["hours"])

with right:
    st.subheader("Clinical Activity Sequences")

    for case_id, group in df.groupby("case_id"):
        sequence = " → ".join(
            group["activity"].astype(str)
        )
        st.write(f"**{case_id}:** {sequence}")

# --------------------------------------------------
# 6. DATA QUALITY CHECKS
# --------------------------------------------------
st.subheader("Data Quality Checks")

q1, q2, q3, q4 = st.columns(4)

q1.metric("Missing Case IDs", missing_ids)
q2.metric("Missing Activities", missing_activities)
q3.metric("Invalid Timestamps", invalid_timestamps)
q4.metric("Duplicate Rows", duplicate_rows)

if (
    missing_ids == 0
    and missing_activities == 0
    and invalid_timestamps == 0
    and duplicate_rows == 0
):
    st.success("Data quality check passed!")
else:
    st.warning(
        "Data quality issues detected. "
        "Invalid events are excluded from the analysis."
    )

# --------------------------------------------------
# 7. CLINICAL PATHWAY INSIGHTS
# --------------------------------------------------
st.subheader("Clinical Pathway Insights")

st.caption(
    "Demo analysis based on synthetic data. "
    "Potential delays are time gaps, not proof of "
    "clinical problems."
)

events, duration_summary = calculate_durations(df)
activity_summary = summarize_activities(events)

left, right = st.columns(2)

with left:
    st.markdown("**Longest Case Duration**")

    longest_case = duration_summary.loc[
        duration_summary["case_duration_hours"].idxmax()
    ]

    st.metric(
        "Case ID",
        str(longest_case["case_id"]),
    )

    st.write(
        "Duration: "
        f"{longest_case['case_duration_hours']:.2f} hours"
    )

with right:
    st.markdown("**Average Gap Between Events**")

    average_gap = events["gap_hours"].mean()

    if pd.notna(average_gap):
        st.metric(
            "Average Event Gap",
            f"{average_gap:.2f} hours",
        )
    else:
        st.metric("Average Event Gap", "Not available")

# Activity summary
st.markdown("**Activity Summary**")

st.dataframe(
    activity_summary,
    width="stretch",
    hide_index=True,
)

# --------------------------------------------------
# 8. POTENTIAL DELAY DETECTION
# --------------------------------------------------
st.markdown("**Potential Delay Detection**")

threshold_hours = st.slider(
    "Delay threshold (hours)",
    min_value=1.0,
    max_value=24.0,
    value=2.0,
    step=0.5,
)

delays = detect_delays(
    events,
    threshold_hours=threshold_hours,
)

if delays.empty:
    st.info(
        f"No event gaps of {threshold_hours:.1f} hours "
        "or longer were found in this synthetic dataset."
    )
else:
    st.write(f"Potential delays detected: {len(delays)}")

    st.dataframe(
    delays,
    width="stretch",
    hide_index=True,
)
# --------------------------------------------------
# 9. SYNTHETIC EVENT LOG AND CSV DOWNLOAD
# --------------------------------------------------
st.subheader("Synthetic Event Log")

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)

st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="synthetic_clinical_events.csv",
    mime="text/csv",
)
