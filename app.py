
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="CareFlow", layout="wide")

st.title("CareFlow: Clinical Pathway Process Mining")
st.warning("DEMO ONLY — This dashboard uses synthetic data, not real patient records.")

data_file = Path(__file__).parent / "data" / "synthetic_clinical_events.csv"

if not data_file.exists():
    st.error("Dataset not found. Check the data folder and CSV filename.")
    st.stop()

df = pd.read_csv(data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["case_id", "activity", "timestamp"])
df = df.sort_values(["case_id", "timestamp"])

case_count = df["case_id"].nunique()
event_count = len(df)
activity_count = df["activity"].nunique()

case_durations = (
    df.groupby("case_id")["timestamp"].agg(["min", "max"])
)
case_durations["hours"] = (
    case_durations["max"] - case_durations["min"]
).dt.total_seconds() / 3600

a, b, c, d = st.columns(4)
a.metric("Total Cases", case_count)
b.metric("Total Events", event_count)
c.metric("Unique Activities", activity_count)
d.metric("Average Case Duration", f"{case_durations['hours'].mean():.2f} hours")

st.subheader("Activity Frequency")
st.bar_chart(df["activity"].value_counts())

left, right = st.columns(2)

with left:
    st.subheader("Case Duration (Hours)")
    st.bar_chart(case_durations["hours"])

with right:
    st.subheader("Clinical Activity Sequences")
    for case_id, group in df.groupby("case_id"):
        sequence = " → ".join(group["activity"].astype(str))
        st.write(f"**{case_id}:** {sequence}")

st.subheader("Synthetic Event Log")
st.dataframe(df, use_container_width=True)

st.download_button(
    "Download CSV",
    df.to_csv(index=False),
    "synthetic_clinical_events.csv",
    "text/csv"
)
