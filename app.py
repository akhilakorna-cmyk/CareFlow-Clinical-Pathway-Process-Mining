
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# CAREFLOW | CLINICAL PATHWAY INTELLIGENCE
# Academic demonstration using synthetic data only
# ---------------------------------------------------------

st.set_page_config(
    page_title="CareFlow | Clinical Intelligence",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#17324D"
TEAL = "#139C96"
MUTED = "#64748B"
BG = "#F4F7FB"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}
    .stApp {{ background: {BG}; }}
    [data-testid="stSidebar"] {{
        background: {NAVY};
        border-right: 1px solid #284761;
    }}
    [data-testid="stSidebar"] * {{ color: #F4F8FC; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #D8E5F0;
    }}
    .brand {{
        font-size: 27px; font-weight: 700; letter-spacing: -1px;
        color: white; padding: 8px 0 0 0;
    }}
    .brand-sub {{
        color: #B7CBDC; font-size: 11px; letter-spacing: 2px;
        text-transform: uppercase; margin-bottom: 25px;
    }}
    .eyebrow {{
        color: {TEAL}; font-size: 11px; font-weight: 700;
        letter-spacing: 1.8px; text-transform: uppercase;
    }}
    .page-title {{
        color: {NAVY}; font-size: 31px; font-weight: 700;
        letter-spacing: -1px; margin: 0 0 4px 0;
    }}
    .page-subtitle {{ color: {MUTED}; font-size: 14px; }}
    .demo-banner {{
        background: #FFF8E8; border: 1px solid #F1D59A;
        color: #805B13; padding: 11px 15px; border-radius: 9px;
        font-size: 12px; margin: 12px 0 22px 0;
    }}
    .section-title {{
        color: {NAVY}; font-size: 17px; font-weight: 700;
        margin-bottom: 2px;
    }}
    .section-note {{ color: {MUTED}; font-size: 12px; margin-bottom: 12px; }}
    div[data-testid="stMetric"] {{
        background: white; border: 1px solid #E2E8F0;
        padding: 17px 18px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(23,50,77,0.035);
    }}
    div[data-testid="stMetricLabel"] p {{
        color: {MUTED}; font-size: 12px; font-weight: 600;
    }}
    div[data-testid="stMetricValue"] {{
        color: {NAVY}; font-weight: 700;
    }}
    div[data-testid="stPlotlyChart"] {{
        background: white; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 8px;
    }}
    .footer {{
        color: #8492A6; font-size: 11px; text-align: center;
        padding: 24px 0 8px 0;
    }}
    hr {{ border-color: #E2E8F0; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data loading ----------

ROOT = Path(__file__).resolve().parent
DATA_CANDIDATES = [
    ROOT / "data" / "synthetic_clinical_events.csv",
    ROOT / "data" / "clinical_events.csv",
    ROOT / "synthetic_clinical_events.csv",
]

@st.cache_data
def load_events(file_path: str) -> pd.DataFrame:
    data = pd.read_csv(file_path)
    required = {"case_id", "activity", "timestamp"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(
            "Missing required column(s): " + ", ".join(sorted(missing))
        )

    data = data.copy()
    data["case_id"] = data["case_id"].astype("string").str.strip()
    data["activity"] = data["activity"].astype("string").str.strip()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data = data.dropna(subset=["case_id", "activity", "timestamp"])
    data = data.sort_values(["case_id", "timestamp"]).reset_index(drop=True)
    return data

data_path = next((p for p in DATA_CANDIDATES if p.exists()), None)

with st.sidebar:
    st.markdown('<div class="brand">✚ CareFlow</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-sub">Clinical Pathway Intelligence</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        [
            "Executive Overview",
            "Pathway Explorer",
            "Delay Analysis",
            "Data Quality",
            "Event Log",
        ],
        label_visibility="visible",
    )
    st.markdown("---")
    st.caption("INFOTACT SOLUTIONS")
    st.caption("Academic demonstration • Synthetic data")

if data_path is None:
    st.error(
        "Dataset not found. Expected `data/synthetic_clinical_events.csv` "
        "inside your project folder."
    )
    st.stop()

try:
    df = load_events(str(data_path))
except Exception as exc:
    st.error(f"Could not load the event log: {exc}")
    st.stop()

if df.empty:
    st.warning("The dataset has no valid event rows to display.")
    st.stop()

# ---------- Process metrics ----------

case_summary = (
    df.groupby("case_id")
    .agg(
        start_time=("timestamp", "min"),
        end_time=("timestamp", "max"),
        event_count=("activity", "size"),
    )
    .reset_index()
)
case_summary["duration_hours"] = (
    case_summary["end_time"] - case_summary["start_time"]
).dt.total_seconds() / 3600

activity_summary = (
    df.groupby("activity")
    .agg(event_count=("activity", "size"), case_count=("case_id", "nunique"))
    .reset_index()
    .sort_values("event_count", ascending=True)
)

df["previous_activity"] = df.groupby("case_id")["activity"].shift(1)
df["previous_timestamp"] = df.groupby("case_id")["timestamp"].shift(1)
df["gap_hours"] = (
    df["timestamp"] - df["previous_timestamp"]
).dt.total_seconds() / 3600

transitions = df.dropna(subset=["previous_activity"]).copy()
transitions = transitions.rename(
    columns={
        "previous_activity": "from_activity",
        "activity": "to_activity",
    }
)

# ---------- Reusable chart styling ----------

def style_chart(fig, height=330):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="DM Sans, sans-serif", color=NAVY, size=12),
        margin=dict(l=18, r=18, t=38, b=18),
        title_font=dict(size=15, color=NAVY),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(
        gridcolor="#EDF1F6",
        linecolor="rgba(0,0,0,0)",
        zeroline=False,
    )
    return fig

def section_heading(title, note=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)

def page_header(title, subtitle):
    st.markdown('<div class="eyebrow">CAREFLOW ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="demo-banner">⚠ DEMO ENVIRONMENT — Synthetic event data only. '
        'No real patient records are used.</div>',
        unsafe_allow_html=True,
    )

# ---------- Pages ----------

if page == "Executive Overview":
    page_header(
        "Clinical Pathway Overview",
        "A consolidated view of workflow activity, case duration and potential delays.",
    )

    a, b, c, d = st.columns(4)
    a.metric("Total Cases", f"{df['case_id'].nunique():,}")
    b.metric("Total Events", f"{len(df):,}")
    c.metric("Unique Activities", f"{df['activity'].nunique():,}")
    d.metric("Mean Case Duration", f"{case_summary['duration_hours'].mean():.2f} h")

    st.write("")
    left, right = st.columns([1.55, 1])

    with left:
        section_heading(
            "Case Duration Comparison",
            "Elapsed time between the first and last recorded event in each case.",
        )
        duration_fig = px.bar(
            case_summary.sort_values("case_id"),
            x="case_id",
            y="duration_hours",
            text=case_summary.sort_values("case_id")["duration_hours"].map(
                lambda value: f"{value:.2f} h"
            ),
            labels={"case_id": "Case", "duration_hours": "Duration (hours)"},
            color_discrete_sequence=[TEAL],
        )
        duration_fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(style_chart(duration_fig, 340), use_container_width=True)

    with right:
        section_heading(
            "Activity Volume",
            "Recorded event count by clinical activity.",
        )
        activity_fig = px.bar(
            activity_summary,
            x="event_count",
            y="activity",
            orientation="h",
            text="event_count",
            labels={"event_count": "Events", "activity": ""},
            color_discrete_sequence=[NAVY],
        )
        activity_fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(style_chart(activity_fig, 340), use_container_width=True)

    section_heading("Operational Signals", "A quick look at longer gaps between recorded activities.")
    threshold = st.slider("Flag gaps of at least (hours)", 0.5, 8.0, 2.0, 0.5)
    flagged = transitions[transitions["gap_hours"] >= threshold].copy()
    if flagged.empty:
        st.success("No activity gaps meet the selected threshold.")
    else:
        st.dataframe(
            flagged[
                ["case_id", "from_activity", "to_activity", "gap_hours", "timestamp"]
            ].rename(
                columns={
                    "case_id": "Case",
                    "from_activity": "From",
                    "to_activity": "To",
                    "gap_hours": "Gap (hours)",
                    "timestamp": "Event timestamp",
                }
            ),
            hide_index=True,
            width="stretch",
        )

elif page == "Pathway Explorer":
    page_header(
        "Pathway Explorer",
        "Explore recorded activity sequences and how often each activity appears.",
    )
    case_options = sorted(df["case_id"].dropna().unique().tolist())
    selected_case = st.selectbox("Select a case", case_options)
    journey = df[df["case_id"] == selected_case].sort_values("timestamp")

    section_heading("Recorded Journey", f"{len(journey)} events for case {selected_case}")
    nodes = journey["activity"].tolist()

    if nodes:
        flow = go.Figure()
        for i, activity in enumerate(nodes):
            flow.add_trace(
                go.Scatter(
                    x=[i],
                    y=[0],
                    mode="markers+text",
                    marker=dict(size=30, color=TEAL if i == 0 else NAVY),
                    text=[activity],
                    textposition="bottom center",
                    textfont=dict(size=11, color=NAVY),
                    hovertemplate=f"Step {i + 1}: {activity}<extra></extra>",
                    showlegend=False,
                )
            )
            if i < len(nodes) - 1:
                flow.add_annotation(
                    x=i + 0.5,
                    y=0,
                    ax=i,
                    ay=0,
                    xref="x",
                    yref="y",
                    axref="x",
                    ayref="y",
                    text="",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1.5,
                    arrowcolor="#9AAABD",
                )
        flow.update_layout(
            height=220,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=30, r=30, t=25, b=70),
            xaxis=dict(visible=False, range=[-0.5, len(nodes) - 0.5]),
            yaxis=dict(visible=False, range=[-0.5, 0.7]),
        )
        st.plotly_chart(flow, use_container_width=True)

    st.dataframe(
        journey[["timestamp", "activity"]].rename(
            columns={"timestamp": "Timestamp", "activity": "Activity"}
        ),
        hide_index=True,
        width="stretch",
    )

    section_heading("Activity Coverage", "Number of cases containing each activity.")
    coverage = px.bar(
        activity_summary.sort_values("case_count"),
        x="case_count",
        y="activity",
        orientation="h",
        text="case_count",
        labels={"case_count": "Cases", "activity": ""},
        color_discrete_sequence=[TEAL],
    )
    coverage.update_traces(textposition="outside")
    st.plotly_chart(style_chart(coverage, 330), use_container_width=True)

elif page == "Delay Analysis":
    page_header(
        "Delay & Transition Analysis",
        "Identify longer time gaps between consecutive events in the same case.",
    )
    threshold = st.slider(
        "Delay threshold (hours)",
        min_value=0.5,
        max_value=12.0,
        value=2.0,
        step=0.5,
    )
    valid_gaps = transitions.dropna(subset=["gap_hours"])
    flagged = valid_gaps[valid_gaps["gap_hours"] >= threshold].copy()

    x1, x2, x3 = st.columns(3)
    x1.metric("Transitions Analysed", f"{len(valid_gaps):,}")
    x2.metric("Flagged Gaps", f"{len(flagged):,}")
    x3.metric(
        "Longest Gap",
        f"{valid_gaps['gap_hours'].max():.2f} h" if not valid_gaps.empty else "N/A",
    )

    section_heading("Time Between Activities", "Gaps are calculated from timestamps within each case.")
    if valid_gaps.empty:
        st.info("No consecutive activity timestamps are available for comparison.")
    else:
        gap_fig = px.bar(
            valid_gaps,
            x="case_id",
            y="gap_hours",
            color="to_activity",
            hover_data=["from_activity", "to_activity", "timestamp"],
            labels={
                "case_id": "Case",
                "gap_hours": "Gap (hours)",
                "to_activity": "Next activity",
            },
        )
        gap_fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="#D97706",
            annotation_text=f"Threshold: {threshold:.1f} h",
        )
        st.plotly_chart(style_chart(gap_fig, 360), use_container_width=True)

    section_heading("Flagged Transitions", "These are time gaps for review, not proof of clinical problems.")
    if flagged.empty:
        st.success("No gaps meet the selected threshold.")
    else:
        st.dataframe(
            flagged[
                ["case_id", "from_activity", "to_activity", "gap_hours", "timestamp"]
            ].rename(
                columns={
                    "case_id": "Case",
                    "from_activity": "From activity",
                    "to_activity": "To activity",
                    "gap_hours": "Gap (hours)",
                    "timestamp": "Timestamp",
                }
            ).sort_values("Gap (hours)", ascending=False),
            hide_index=True,
            width="stretch",
        )

elif page == "Data Quality":
    page_header(
        "Data Quality & Validation",
        "Review completeness, timestamp validity and duplicate event records.",
    )

    raw = pd.read_csv(data_path)
    required = ["case_id", "activity", "timestamp"]
    missing_columns = [column for column in required if column not in raw.columns]
    missing_values = int(raw[required].isna().any(axis=1).sum()) if not missing_columns else 0
    invalid_timestamps = (
        int(pd.to_datetime(raw["timestamp"], errors="coerce").isna().sum())
        if "timestamp" in raw.columns else len(raw)
    )
    duplicate_rows = int(raw.duplicated().sum())
    valid_rows = len(df)

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Raw Rows", f"{len(raw):,}")
    q2.metric("Valid Event Rows", f"{valid_rows:,}")
    q3.metric("Invalid Timestamps", f"{invalid_timestamps:,}")
    q4.metric("Duplicate Rows", f"{duplicate_rows:,}")

    checks = [
        {
            "Check": "Required columns",
            "Result": "PASS" if not missing_columns else "FAIL",
            "Details": "All required columns present" if not missing_columns
            else "Missing: " + ", ".join(missing_columns),
        },
        {
            "Check": "Missing required values",
            "Result": "PASS" if missing_values == 0 else "REVIEW",
            "Details": f"{missing_values} row(s) have missing required fields",
        },
        {
            "Check": "Timestamp parsing",
            "Result": "PASS" if invalid_timestamps == 0 else "REVIEW",
            "Details": f"{invalid_timestamps} invalid or missing timestamp(s)",
        },
        {
            "Check": "Duplicate rows",
            "Result": "PASS" if duplicate_rows == 0 else "REVIEW",
            "Details": f"{duplicate_rows} duplicate row(s)",
        },
    ]
    section_heading("Validation Results", "Automated checks against the loaded CSV.")
    st.dataframe(pd.DataFrame(checks), hide_index=True, width="stretch")
    st.caption(
        "Rows with missing required values or invalid timestamps are excluded from "
        "the displayed process analysis. Review the original CSV before relying on results."
    )

    section_heading("Dataset Profile")
    profile = pd.DataFrame(
        {
            "Metric": ["Unique cases", "Unique activities", "First event", "Last event"],
            "Value": [
                str(df["case_id"].nunique()),
                str(df["activity"].nunique()),
                str(df["timestamp"].min()),
                str(df["timestamp"].max()),
            ],
        }
    )
    st.dataframe(profile, hide_index=True, width="stretch")

elif page == "Event Log":
    page_header(
        "Event Log Explorer",
        "Filter, inspect and export the underlying synthetic event records.",
    )
    f1, f2 = st.columns(2)
    with f1:
        case_filter = st.multiselect(
            "Filter by case",
            sorted(df["case_id"].dropna().unique().tolist()),
        )
    with f2:
        activity_filter = st.multiselect(
            "Filter by activity",
            sorted(df["activity"].dropna().unique().tolist()),
        )

    filtered = df.copy()
    if case_filter:
        filtered = filtered[filtered["case_id"].isin(case_filter)]
    if activity_filter:
        filtered = filtered[filtered["activity"].isin(activity_filter)]

    st.caption(f"Showing {len(filtered):,} of {len(df):,} valid event rows.")
    st.dataframe(filtered, hide_index=True, width="stretch")

    st.download_button(
        "Download filtered event log (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="careflow_filtered_event_log.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("---")
st.markdown(
    '<div class="footer">CAREFLOW • INFOTACT SOLUTIONS • '
    'Synthetic data demonstration only • Not for clinical decision-making</div>',
    unsafe_allow_html=True,
)
