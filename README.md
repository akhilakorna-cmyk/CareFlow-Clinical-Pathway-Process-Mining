# CareFlow: Clinical Pathway Process Mining

**Project:** Infotact Solutions CareFlow

> **DEMO ONLY:** This project currently uses synthetic data, not real patient records. It is intended for educational and demonstration purposes, not clinical decision-making.

## 1. Project Overview

CareFlow is a process-mining project that analyzes clinical pathway event data to understand activity sequences, calculate case durations, summarize activity frequencies, and identify potential delays.

The project uses Python, Pandas, and Streamlit to process event data and present results in an interactive dashboard.

## 2. Objectives

- Load and validate clinical event-log data.
- Calculate clinical case durations.
- Summarize activity frequencies.
- Reconstruct clinical pathway sequences.
- Identify potential delays using configurable thresholds.
- Visualize results in an interactive dashboard.

## 3. Dataset Status

The official project dataset is pending approval or delivery. Synthetic sample data is being used for development and testing until an approved dataset is provided.

The current sample contains:
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

These sample records do not represent real patients.

## 4. Technology Stack

- Python
- Pandas
- Streamlit
- Pytest
- Git and GitHub

## 5. Project Features

- Event-log loading and validation
- Case duration calculation
- Activity frequency summaries
- Clinical pathway reconstruction
- Configurable potential-delay detection
- Interactive charts and summary metrics
- Synthetic event-log display and CSV download
- Automated process-analysis tests

## 6. Setup Instructions

### Step 1: Clone the repository

```bash
git clone https://github.com/akhilakorna-cmyk/CareFlow-Clinical-Pathway-Process-Mining.git
cd CareFlow-Clinical-Pathway-Process-Mining
```

### Step 2: Create a virtual environment

```powershell
py -3.13 -m venv .venv
```

### Step 3: Activate the environment on Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 5: Run the dashboard

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## 7. Run Automated Tests

With the virtual environment activated, run:

```powershell
python -m pytest src/test_process_analysis.py -v
```

The latest recorded test run passed all four process-analysis tests. Run the command again to verify the current version.

## 8. Current Project Status

- [x] Initial project setup
- [x] Synthetic dataset preparation
- [x] Data validation
- [x] Process-analysis implementation
- [x] Clinical pathway and potential-delay analysis
- [x] Automated process-analysis tests
- [ ] Final dashboard verification
- [ ] Final repository and documentation review
- [ ] Cloud deployment verification
- [ ] Final report and presentation
- [ ] Integration of the official dataset when available

*Update this checklist as each remaining task is verified.*

## 9. Limitations

- The current dataset is synthetic and very small.
- Results demonstrate software functionality only.
- Delay thresholds are configurable demonstration settings, not clinically validated standards.
- Findings must not be interpreted as evidence of real-world clinical performance.

## 10. Future Enhancements

- Integrate the approved project dataset when available.
- Evaluate data quality and pathway variations.
- Improve process visualizations and delay analysis.
- Verify deployment using Streamlit Community Cloud.
- Prepare the final project report and presentation.

## 11. Repository

[CareFlow: Clinical Pathway Process Mining on GitHub](https://github.com/akhilakorna-cmyk/CareFlow-Clinical-Pathway-Process-Mining)