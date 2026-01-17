# Supreme Court of India – Diary Case Scraper

## Overview

This project is an **end-to-end Selenium-based web scraper** for extracting structured case metadata from the **Supreme Court of India – Diary Number Case Status portal**.

The scraper is designed to handle:
- Dynamic, accordion-based sections
- CAPTCHA-gated access (manual solve, automated extraction)
- Deeply nested HTML tables
- Legal domain–specific data normalization

The output is a **clean, analysis-ready CSV** suitable for legal analytics, research workflows, and downstream NLP / LLM pipelines.

---

## Key Features

- Automated extraction of **Case Details**, **Listing Dates**, **Judgements / Orders**, and **Interlocutory Applications**
- Robust handling of:
  - Dynamically expanded sections
  - Nested tables inside accordions
  - Non-standard HTML structures
- Intelligent parsing and normalization:
  - Diary Number
  - Case Number & Case Type
  - Filing / Registration / Decision Dates
  - Bench & First Judge
  - Case Status & Nature of Disposal
- Advanced legal analytics:
  - Number of hearings
  - Number of orders
  - Interim Applications split by:
    - Petitioner
    - Respondent
    - Interlocutors

---

## Data Extracted

The scraper outputs the following fields (non-exhaustive):

- Diary Number  
- Case Number  
- Case Type  
- Filing Date  
- Registration Date  
- Decision Date  
- Case Status  
- Nature of Disposal  
- CNR Number  
- Bench  
- First Judge Name  
- Petitioner / Respondent  
- Petitioner & Respondent Advocates  
- Impleader / Intervenor Advocates  
- First Hearing Date  
- Last Listed Date  
- Number of Hearings  
- Number of Orders  
- Number of Interim Applications:
  - By Petitioner
  - By Respondent
  - By Interlocutors
  - Total

---

## Project Structure

# Supreme Court of India – Diary Case Scraper

## Overview

This project is an **end-to-end Selenium-based web scraper** for extracting structured case metadata from the **Supreme Court of India – Diary Number Case Status portal**.

The scraper is designed to handle:
- Dynamic, accordion-based sections
- CAPTCHA-gated access (manual solve, automated extraction)
- Deeply nested HTML tables
- Legal domain–specific data normalization

The output is a **clean, analysis-ready CSV** suitable for legal analytics, research workflows, and downstream NLP / LLM pipelines.

---

## Key Features

- Automated extraction of **Case Details**, **Listing Dates**, **Judgements / Orders**, and **Interlocutory Applications**
- Robust handling of:
  - Dynamically expanded sections
  - Nested tables inside accordions
  - Non-standard HTML structures
- Intelligent parsing and normalization:
  - Diary Number
  - Case Number & Case Type
  - Filing / Registration / Decision Dates
  - Bench & First Judge
  - Case Status & Nature of Disposal
- Advanced legal analytics:
  - Number of hearings
  - Number of orders
  - Interim Applications split by:
    - Petitioner
    - Respondent
    - Interlocutors

---

## Data Extracted

The scraper outputs the following fields (non-exhaustive):

- Diary Number  
- Case Number  
- Case Type  
- Filing Date  
- Registration Date  
- Decision Date  
- Case Status  
- Nature of Disposal  
- CNR Number  
- Bench  
- First Judge Name  
- Petitioner / Respondent  
- Petitioner & Respondent Advocates  
- Impleader / Intervenor Advocates  
- First Hearing Date  
- Last Listed Date  
- Number of Hearings  
- Number of Orders  
- Number of Interim Applications:
  - By Petitioner
  - By Respondent
  - By Interlocutors
  - Total

---

## Tech Stack

- **Python 3.10+**
- **Selenium**
- **Chrome WebDriver**
- **Pandas**
- **Regular Expressions**
- **JavaScript DOM inspection (for selector validation)**

---

## How It Works (High-Level)

1. User navigates to the SCI diary case page
2. CAPTCHA is solved manually (as required by the website)
3. Script:
   - Detects successful page load via DOM markers
   - Expands required accordion sections
   - Extracts structured data from nested tables
   - Normalizes and derives analytical fields
4. Data is appended to a CSV file for further analysis

---

## Usage

```bash
pip install -r requirements.txt
python scraper.py

After launching:

1) Enter diary number and year in the browser

2) Solve CAPTCHA

3) Press ENTER in the terminal

4) Data is extracted and appended to CSV



