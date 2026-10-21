# CareFlow: Clinical Pathway Process Mining

**Project:** Infotact Solutions CareFlow

> **DEMO ONLY:** This project currently uses synthetic data, not real patient records. It is intended for educational and demonstration purposes, not clinical decision-making.

## Project Overview

CareFlow is a process-mining project that analyzes clinical pathway event data to understand the sequence of activities, estimate case durations, summarize activity frequencies, and identify potential delays.

The project uses Python, Pandas, and Streamlit to process event data and present the results in an interactive dashboard.

## Objectives

- Load and validate clinical event-log data.
- Calculate clinical case durations.
- Summarize activity frequencies.
- Reconstruct patient pathway sequences.
- Identify potential delays using configurable thresholds.
- Visualize results in an interactive dashboard.

## Dataset Status

The official project dataset is pending approval or delivery. Synthetic sample data is being used for development and testing until an approved dataset is provided.

The current sample contains three synthetic cases, 18 events, and six activities:

- Registration
- Initial Assessment
- Lab Test
- Diagnosis
- Treatment
- Discharge

These sample records do not represent real patients.

## Technology Stack

- Python
- Pandas
- Streamlit
- Pytest
- Git and GitHub

## Project Features

- Data loading and validation
- Case duration calculation
- Activity frequency summaries
- Clinical pathway reconstruction
- Configurable delay detection
- Interactive charts and summary metrics
- Synthetic event-log display and CSV download
- Automated process-analysis tests

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/akhilakorna-cmyk/CareFlow-Clinical-Pathway-Process-Mining.git
cd CareFlow-Clinical-Pathway-Process-Mining
```

### 2. Create a virtual environment

```bash
py -3.13 -m venv .venv
```

### 3. Activate the environment on Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the dashboard

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## Run Automated Tests

With the virtual environment activated, run:

```bash
python -m pytest src/test_process_analysis.py -v
```

The latest recorded test run passed all four process-analysis tests. Run the command above again to verify the current version.

## Current Project Status

- [x] Initial project setup
- [x] Synthetic dataset preparation
- [x] Data validation
- [x] Process-analysis implementation
- [x] Clinical pathway and delay analysis
- [x] Interactive dashboard implementation
- [x] Four automated process-analysis tests passing
- [ ] Final dashboard verification
- [ ] README and repository review
- [ ] Cloud deployment
- [ ] Final report and presentation
- [ ] Integration of the official dataset when available

## Limitations

- The current dataset is synthetic and very small.
- Results demonstrate software functionality only.
- Delay thresholds are configurable demonstration settings, not clinically validated standards.
- Findings must not be interpreted as evidence of real-world clinical performance.

## Future Enhancements

- Integrate the approved project dataset.
- Evaluate data quality and pathway variations.
- Improve process visualizations and delay analysis.
- Deploy the dashboard to Streamlit Community Cloud.
- Prepare the final project report and presentation.

## Repository

[CareFlow Clinical Pathway Process Mining on GitHub](https://github.com/akhilakorna-cmyk/CareFlow-Clinical-Pathway-Process-Mining)
