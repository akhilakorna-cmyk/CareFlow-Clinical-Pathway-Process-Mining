# CareFlow: Clinical Pathway Process Mining

## Mid-Review Presentation — 26 October 2026

**Student:** Korna Akhila  
**Branch:** B.Tech ECE (VLSI)  
**College:** Narayana Engineering College, Nellore  
**Project:** Infotact Solutions CareFlow: Clinical Pathway Process Mining

---

### Slide 1: Introduction

CareFlow is a process-mining project that analyzes clinical activity sequences, calculates case durations, identifies potential delays, and presents results through an interactive Streamlit dashboard.

**Current status:** The project uses synthetic demonstration data because the official dataset has not yet been received.

### Slide 2: Problem Statement and Objectives

**Problem statement:** Understanding activity sequences and time gaps in clinical workflows can be challenging when event records are presented only as raw data.

**Objectives:**
- Analyze clinical activity sequences.
- Calculate the duration of each case.
- Identify potential delays between activities.
- Validate event-log data quality.
- Visualize results through a Streamlit dashboard.

### Slide 3: Technologies Used

- Python for data processing and analysis.
- Pandas for event-log manipulation.
- Streamlit for dashboard development.
- Plotly for charts and visualizations.
- Pytest for automated testing.
- Git and GitHub for version control.
- CSV for storing event-log records.

### Slide 4: System Architecture

**CSV Event Log → Data Loading → Data Validation → Process Analysis → Delay Detection → Streamlit Dashboard**

The workflow loads the data, checks its quality, reconstructs activity sequences, calculates durations, detects potential time gaps, and displays