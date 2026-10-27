
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="CareFlow | Clinical Pathway Process Mining",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#0B1220"
PANEL = "#111C30"
TEAL = "#14B8A6"
MUTED = "#9AAAC0"
BORDER = "#2A3A52"
DELAY_THRESHOLD = 2.0

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}
    .stApp {{
        background: radial-gradient(ellipse at top left,
        rgba(20,184,166,0.09), transparent 38%), #0B1220;
        color: #F1F5F9;
    }}
    [data-testid="stHeader"] {{ background: #0B1220; }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #111C30, #0B1220);
        border-right: 1px solid {BORDER};
    }}
    [data-testid="stSidebar"] * {{ color: #F1F5F9; }}
    .brand {{
        font-size: 29px; font-weight: 800; color: white;
    }}
    .brand-sub {{
        color: {MUTED}; font-size: 10px;
        letter-spacing: 1.6px; margin-bottom: 18px;
    }}
    .eyebrow {{
        color: {TEAL}; font-size: 11px;
        font-weight: 800; letter-spacing: 2px;
    }}
    .page-title {{
        color: #F8FAFC; font-size: 32px;
        font-weight: 800; margin: 4px 0;
    }}
    .page-subtitle {{ color: {MUTED}; font-size: 14px; }}
    .demo-banner {{
        background: rgba(251,191,36,0.08);
        border: 1px solid #705A2C; color: #FDE68A;
        padding: 12px 16px; border-radius: 10px;
        font-size: 12px; margin: 16px 0 24px;
    }}
    .section-title {{
        color: #F1F5F9; font-size: 19px;
        font-weight: 700; margin: 8px 0;
    }}
    .section-note {{
        color: {MUTED}; font-size: 12px;
        margin-bottom: 12px;
    }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, #17263D, {PANEL});
        border: 1px solid {BORDER}; border-radius: 14px;
        padding: 18px; min-height: 105px;
    }}
    div[data-testid="stMetricLabel"] p {{ color: #A8B7CA; }}
    div[data-testid="stMetricValue"] {{
        color: #F8FAFC; font-weight: 800;
    }}
    div[data-testid="stPlotlyChart"] {{
        background: {PANEL}; border: 1px solid {BORDER};
        border-radius: 14px; padding: 8px;
    }}
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER}; border-radius: 11px;
    }}
    .stDownloadButton > button {{
        background: {TEAL}; color: #062A2A;
        border-radius: 9px; font-weight: 700;
    }}
    .footer {{
        color: #8492A6; font-size: 11px;
        text-align: center; padding: 24px 0 8px;
    }}
    hr {{ border-color: {BORDER}; }}
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# DATA LOADING
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "synthetic_clinical_events.csv"


@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required = {"case_id", "activity", "timestamp"}
    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            "Missing columns: " + ", ".join(sorted(missing))
        )

    data["timestamp"] = pd.to_datetime(
        data["timestamp"], errors="coerce"
    )
    data["case_id"] = data["case_id"].astype("string").str.strip()
    data["activity"] = data["activity"].astype("string").str.strip()

    return data.sort_values(
        ["case_id", "timestamp"], na_position="last"
    ).reset_index(drop=True)


if not DATA_FILE.exists():
    st.error(f"Dataset not found: {DATA_FILE}")
    st.info("Put synthetic_clinical_events.csv in the data folder.")
    st.stop()

try:
    df = load_data(str(DATA_FILE))
except Exception as error:
    st.error(f"Could not load data: {error}")
    st.stop()

valid_events = df.dropna(
    subset=["case_id", "activity", "timestamp"]
).copy()

valid_events = valid_events[
    valid_events["case_id"].ne("")
    & valid_events["activity"].ne("")
].copy()

valid_events = valid_events.sort_values(
    ["case_id", "timestamp"]
).reset_index(drop=True)

if valid_events.empty:
    st.error("No valid events are available.")
    st.stop()


# HELPER FUNCTIONS
def style_chart(fig, height=330):
    fig.update_layout(
        height=height,
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(family="DM Sans", color="#F1F5F9", size=12),
        margin=dict(l=18, r=24, t=48, b=22),
        title_font=dict(size=15, color="#F8FAFC"),
        legend=dict(font=dict(color="#D7E2F0")),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER)
    fig.update_yaxes(gridcolor="#25344A")
    return fig


def section_header(title, note=None):
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )
    if note:
        st.markdown(
            f'<div class="section-note">{note}</div>',
            unsafe_allow_html=True,
        )


def make_case_durations(data):
    result = data.groupby("case_id")["timestamp"].agg(
        start_time="min", end_time="max"
    ).reset_index()

    result["duration_hours"] = (
        result["end_time"] - result["start_time"]
    ).dt.total_seconds() / 3600

    return result


def add_gaps(data):
    result = data.sort_values(["case_id", "timestamp"]).copy()
    result["previous_activity"] = (
        result.groupby("case_id")["activity"].shift(1)
    )
    result["previous_timestamp"] = (
        result.groupby("case_id")["timestamp"].shift(1)
    )
    result["gap_hours"] = (
        result["timestamp"] - result["previous_timestamp"]
    ).dt.total_seconds() / 3600
    return result


# SHARED FILTERS
with st.sidebar:
    st.markdown(
        '<div class="brand">CareFlow<span style="color:#14B8A6">.</span></div>'
        '<div class="brand-sub">INFOTACT SOLUTIONS</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**ONE-PAGE DASHBOARD**")
    st.caption("Scroll the page to see every section.")
    st.markdown("---")

    all_cases = sorted(valid_events["case_id"].unique().tolist())
    all_activities = sorted(valid_events["activity"].unique().tolist())

    selected_cases = st.multiselect(
        "Clinical cases", all_cases, default=all_cases
    )
    selected_activities = st.multiselect(
        "Activities", all_activities, default=all_activities
    )

    min_date = valid_events["timestamp"].min().date()
    max_date = valid_events["timestamp"].max().date()

    date_range = st.date_input(
        "Event date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.markdown("---")
    st.caption("Synthetic demonstration data only.")

events = valid_events.copy()

events = events[events["case_id"].isin(selected_cases)]
events = events[events["activity"].isin(selected_activities)]

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start = pd.Timestamp(date_range[0])
    end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    events = events[
        (events["timestamp"] >= start)
        & (events["timestamp"] < end)
    ]

events = events.sort_values(
    ["case_id", "timestamp"]
).reset_index(drop=True)

durations = make_case_durations(events)

activity_summary = (
    events.groupby("activity")
    .agg(
        event_count=("activity", "size"),
        case_count=("case_id", "nunique"),
    )
    .reset_index()
    .sort_values("event_count", ascending=False)
)

gaps = add_gaps(events)

# =========================================================
# DASHBOARD HEADER
# =========================================================

st.markdown(
    '<div class="eyebrow">CAREFLOW / INFOTACT SOLUTIONS</div>'
    '<div class="page-title">Clinical Pathway Process Mining</div>'
    '<div class="page-subtitle">One-page clinical pathway overview, '
    'journeys, delays, data quality, and event records.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="demo-banner">
    <strong>DEMO ONLY</strong> — Synthetic data, not real patient records.
    Findings are illustrative and must not be used for clinical decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

if events.empty:
    st.warning("No events match the current filters. Change the sidebar filters.")

# =========================================================
# 01. EXECUTIVE OVERVIEW
# =========================================================

st.markdown("---")
section_header(
    "01 · Executive Overview",
    "Summary metrics and process indicators.",
)

avg_duration = (
    durations["duration_hours"].mean()
    if not durations.empty else 0
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Cases", f"{events['case_id'].nunique():,}")
c2.metric("Total Events", f"{len(events):,}")
c3.metric("Unique Activities", f"{events['activity'].nunique():,}")
c4.metric("Average Case Duration", f"{avg_duration:.2f} h")

left, right = st.columns(2)

with left:
    section_header("Activity Volume", "Recorded events per activity.")
    if not activity_summary.empty:
        fig = px.bar(
            activity_summary.sort_values("event_count"),
            x="event_count",
            y="activity",
            orientation="h",
            text="event_count",
            color_discrete_sequence=[TEAL],
            labels={"event_count": "Events", "activity": "Activity"},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False)
        st.plotly_chart(
            style_chart(fig, 340), use_container_width=True
        )
    else:
        st.info("No activity data available.")

with right:
    section_header("Case Duration", "Elapsed time per case.")
    if not durations.empty:
        fig = px.bar(
            durations,
            x="case_id",
            y="duration_hours",
            text="duration_hours",
            color_discrete_sequence=[TEAL],
            labels={
                "case_id": "Case",
                "duration_hours": "Hours",
            },
        )
        fig.update_traces(
            texttemplate="%{text:.2f} h",
            textposition="outside",
            cliponaxis=False,
        )
        st.plotly_chart(
            style_chart(fig, 340), use_container_width=True
        )
    else:
        st.info("No case durations available.")

overview_delays = gaps[gaps["gap_hours"] >= DELAY_THRESHOLD]
longest_gap = (
    overview_delays["gap_hours"].max()
    if not overview_delays.empty else 0
)

d1, d2 = st.columns(2)
d1.metric("Potential Delay Gaps (≥ 2 h)", len(overview_delays))
d2.metric("Longest Gap", f"{longest_gap:.2f} h")

if not overview_delays.empty:
    st.dataframe(
        overview_delays[
            ["case_id", "previous_activity", "activity", "gap_hours", "timestamp"]
        ].rename(columns={
            "case_id": "Case ID",
            "previous_activity": "Previous Activity",
            "activity": "Current Activity",
            "gap_hours": "Gap (hours)",
            "timestamp": "Current Event Time",
        }),
        use_container_width=True,
        hide_index=True,
    )

# =========================================================
# 02. PATHWAY EXPLORER
# =========================================================

st.markdown("---")
section_header(
    "02 · Pathway Explorer",
    "View the chronological events for a selected case.",
)

if not events.empty:
    selected_case = st.selectbox(
        "Choose a case",
        sorted(events["case_id"].unique().tolist()),
        key="pathway_case",
    )

    case_events = events[
        events["case_id"] == selected_case
    ].sort_values("timestamp").copy()

    case_duration = (
        case_events["timestamp"].max()
        - case_events["timestamp"].min()
    ).total_seconds() / 3600

    p1, p2, p3 = st.columns(3)
    p1.metric("Case ID", selected_case)
    p2.metric("Recorded Events", len(case_events))
    p3.metric("Case Duration", f"{case_duration:.2f} h")

    timeline = case_events.copy()
    timeline["step"] = range(1, len(timeline) + 1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline["timestamp"],
        y=timeline["step"],
        mode="lines+markers+text",
        text=timeline["activity"],
        textposition="top center",
        line=dict(color=TEAL, width=3),
        marker=dict(color=TEAL, size=12),
        hovertemplate="%{text}<br>%{x}<extra></extra>",
    ))
    fig.update_yaxes(showticklabels=False, title="")
    fig.update_xaxes(title="Event timestamp")

    st.plotly_chart(
        style_chart(fig, 380), use_container_width=True
    )

    st.markdown("**Journey Sequence**")
    st.markdown(" → ".join(case_events["activity"].astype(str)))

    st.dataframe(
        case_events[["case_id", "timestamp", "activity"]].rename(
            columns={
                "case_id": "Case ID",
                "timestamp": "Timestamp",
                "activity": "Activity",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No journeys available for the current filters.")

# =========================================================
# 03. DELAY ANALYSIS
# =========================================================

st.markdown("---")
section_header(
    "03 · Delay Analysis",
    "Elapsed gaps between consecutive recorded activities. "
    "A gap alone does not prove a clinical delay.",
)

threshold = st.slider(
    "Potential delay threshold (hours)",
    min_value=0.5,
    max_value=12.0,
    value=DELAY_THRESHOLD,
    step=0.5,
)

delay_events = gaps[gaps["gap_hours"] >= threshold].copy()

a1, a2, a3 = st.columns(3)
a1.metric("Potential Delay Gaps", len(delay_events))
a2.metric("Cases With Gaps", delay_events["case_id"].nunique())
a3.metric(
    "Longest Gap",
    f"{delay_events['gap_hours'].max():.2f} h"
    if not delay_events.empty else "0.00 h",
)

if not delay_events.empty:
    fig = px.bar(
        delay_events.sort_values("gap_hours"),
        x="gap_hours",
        y="case_id",
        color="activity",
        orientation="h",
        text="gap_hours",
        labels={
            "gap_hours": "Gap (hours)",
            "case_id": "Case",
            "activity": "Current activity",
        },
        color_discrete_sequence=[
            TEAL, "#60A5FA", "#A78BFA", "#FBBF24", "#F472B6"
        ],
    )
    fig.update_traces(
        texttemplate="%{text:.2f} h",
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(
        style_chart(fig, 340), use_container_width=True
    )

    delay_table = delay_events[
        [
            "case_id",
            "previous_activity",
            "activity",
            "previous_timestamp",
            "timestamp",
            "gap_hours",
        ]
    ].rename(columns={
        "case_id": "Case ID",
        "previous_activity": "Previous Activity",
        "activity": "Current Activity",
        "previous_timestamp": "Previous Timestamp",
        "timestamp": "Current Timestamp",
        "gap_hours": "Gap (hours)",
    })

    st.dataframe(
        delay_table, use_container_width=True, hide_index=True
    )
    st.download_button(
        "Download Delay Report",
        delay_table.to_csv(index=False).encode("utf-8"),
        file_name="careflow_delay_report.csv",
        mime="text/csv",
    )
else:
    st.success(f"No gaps of {threshold:.1f} hours or more found.")

# =========================================================
# 04. DATA QUALITY
# =========================================================

st.markdown("---")
section_header(
    "04 · Data Quality",
    "Validation checks use the full dataset, regardless of dashboard filters.",
)

missing_ids = int(df["case_id"].isna().sum())
missing_activities = int(df["activity"].isna().sum())
invalid_timestamps = int(df["timestamp"].isna().sum())
duplicate_rows = int(df.duplicated().sum())
invalid_rows = len(df) - len(valid_events)

q1, q2, q3 = st.columns(3)
q1.metric("Total Rows", len(df))
q2.metric("Valid Events", len(valid_events))
q3.metric("Rows Excluded", invalid_rows)

quality_checks = pd.DataFrame([
    {
        "Check": "Missing case IDs",
        "Issues Found": missing_ids,
        "Status": "Pass" if missing_ids == 0 else "Review",
    },
    {
        "Check": "Missing activities",
        "Issues Found": missing_activities,
        "Status": "Pass" if missing_activities == 0 else "Review",
    },
    {
        "Check": "Invalid timestamps",
        "Issues Found": invalid_timestamps,
        "Status": "Pass" if invalid_timestamps == 0 else "Review",
    },
    {
        "Check": "Duplicate rows",
        "Issues Found": duplicate_rows,
        "Status": "Pass" if duplicate_rows == 0 else "Review",
    },
])

st.dataframe(
    quality_checks, use_container_width=True, hide_index=True
)

if quality_checks["Issues Found"].sum() == 0 and invalid_rows == 0:
    st.success("All displayed data-quality checks passed.")
else:
    st.warning("Some data-quality issues need review.")

full_activity_summary = (
    valid_events.groupby("activity")
    .agg(case_count=("case_id", "nunique"))
    .reset_index()
    .sort_values("case_count")
)

if not full_activity_summary.empty:
    fig = px.bar(
        full_activity_summary,
        x="case_count",
        y="activity",
        orientation="h",
        text="case_count",
        color_discrete_sequence=[TEAL],
        labels={"case_count": "Number of cases", "activity": "Activity"},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(showlegend=False)
    st.plotly_chart(
        style_chart(fig, 330), use_container_width=True
    )

st.markdown("**Dataset Preview**")
st.dataframe(
    df.head(100), use_container_width=True, hide_index=True
)
st.download_button(
    "Download Loaded Dataset",
    df.to_csv(index=False).encode("utf-8"),
    file_name="careflow_dataset.csv",
    mime="text/csv",
)

# =========================================================
# 05. EVENT LOG
# =========================================================

st.markdown("---")
section_header(
    "05 · Event Log",
    "Inspect and export the event records matching the shared filters.",
)

e1, e2, e3 = st.columns(3)
e1.metric("Filtered Events", len(events))
e2.metric("Filtered Cases", events["case_id"].nunique())
e3.metric("Activities", events["activity"].nunique())

if not events.empty:
    st.dataframe(
        events, use_container_width=True, hide_index=True
    )
    st.download_button(
        "Download Filtered Event Log",
        events.to_csv(index=False).encode("utf-8"),
        file_name="careflow_filtered_event_log.csv",
        mime="text/csv",
    )
else:
    st.info("No event records match the selected filters.")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.markdown(
    """
    <div class="footer">
        CAREFLOW · CLINICAL PATHWAY PROCESS MINING<br>
        INFOTACT SOLUTIONS · Educational demonstration using synthetic data
    </div>
    """,
    unsafe_allow_html=True,
)
