# CareFlow: Clinical Pathway Process Mining

**Project:** Infotact Solutions CareFlow  
**Purpose:** Educational process mining and clinical pathway analysis

> **DEMO ONLY:** This project uses synthetic data, not real patient records. Findings are illustrative and must not be used for clinical decision-making.

## 1. Project Overview

CareFlow is a process-mining project designed to analyze clinical pathway event logs. It examines activity sequences, calculates case durations, summarizes activity frequencies, reconstructs pathways, and identifies potential delays.

The project uses Python, Pandas, and Streamlit to analyze event data and present results through an interactive dashboard.

## 2. Project Objectives

- Load and validate clinical event-log data.
- Calculate the duration of each case.
- Summarize activity frequencies.
- Reconstruct clinical pathway sequences.
- Detect potential delays using configurable thresholds.
- Visualize process-analysis results in an interactive dashboard.

## 3. Dataset Status

The official project dataset has not yet been received. Synthetic sample data is used for development, testing, and demonstration.

The current sample dataset contains:

- **3 synthetic cases**
- **18 events**
- **6 activities**

The activities are:

1. Registration
2. Initial Assessment
3. Lab Test
4. Diagnosis
5. Treatment
6. Discharge

All sample records are synthetic and do not represent real patients.

## 4. Technology Stack

- Python 3.13
- Pandas
- Streamlit
- Pytest
- Git
- GitHub

## 5. Project Features

- Event-log loading and validation
- Data-quality checks
- Case-duration calculation
- Activity-frequency summaries
- Clinical pathway reconstruction
- Configurable potential-delay detection
- Interactive dashboard metrics and charts
- Synthetic event-log display and CSV download
- Automated process-analysis tests

## 6. Project Structure

```text
CareFlow-Clinical-Pathway-Process-Mining/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── analysis.py
│   ├── data_loader.py
│   ├── process_analysis.py
│   └── test_process_analysis.py
└── reports/
```

The project may contain additional files and folders as development continues.

## 7. Installation and Setup

### Prerequisites

- Windows
- Python 3.13
- Git

### Step 1: Clone the repository

```bash
git clone https://github.com/akhilakorna-cmyk/CareFlow-Clinical-Pathway-Process-Mining.git
cd CareFlow-Clinical-Pathway-Process-Mining
```

### Step 2: Create a virtual environment

```powershell
py -3.13 -m venv .venv
```

### Step 3: Install dependencies

On Windows PowerShell, use the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 4: Launch the dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## 8. Running Automated Tests

Run the process-analysis tests using:

```powershell
.\.venv\Scripts\python.exe -m pytest .\src\test_process_analysis.py -v
```

The latest recorded test run passed all four tests:

- `test_calculate_durations`
- `test_summarize_activities`
- `test_reconstruct_journeys`
- `test_detect_delays`

Run the command again after making changes to verify the current version.

## 9. Current Project Status

- [x] Initial project setup
- [x] Synthetic dataset preparation
- [x] Data validation and quality checks
- [x] Process-analysis implementation
- [x] Duration and delay analysis
- [x] Automated process-analysis tests
- [x] Local dashboard launched
- [ ] Final dashboard verification
- [ ] Final repository and documentation review
- [ ] Cloud deployment verification
- [ ] Final report and presentation
- [ ] Integration of the official dataset when available

Update this checklist when each remaining task has been verified.

## 10. Limitations and Disclaimer

- The current dataset is synthetic and contains only three cases.
- Results demonstrate software functionality and are not clinical findings.
- Delay thresholds are demonstration settings, not clinically validated standards.
- The project must not be used for diagnosis, treatment decisions, or other clinical decision-making.
- Analysis of real clinical pathways requires an appropriate, approved dataset and further validation.

## 11. Future Enhancements

- Integrate the official project dataset when it becomes available.
- Analyze pathway variations across cases.
- Improve process visualizations and delay analysis.
- Verify deployment using Streamlit Community Cloud.
- Prepare the final project report and presentation.

## 12. GitHub Repository

[CareFlow: Clinical Pathway Process Mining](https://github.com/akhilakorna-cmyk/CareFlow-Clinical-Pathway-Process-Mining)
