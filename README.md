Supreme Court of India – Diary Case Scraper
Overview

This project is an end-to-end Selenium-based web scraper for extracting structured case metadata from the ecourts website of Supreme Court of India – Diary Number Case Status portal.

The scraper is designed to handle:

Dynamic, accordion-based sections

CAPTCHA-gated access (manual solve, automated extraction)

Deeply nested HTML tables

Legal domain–specific data normalization

The output is a clean, analysis-ready CSV suitable for legal analytics, research workflows, and downstream NLP / LLM pipelines.

Key Features

Automated extraction of Case Details, Listing Dates, Judgements / Orders, and Interlocutory Applications

Robust handling of:

Dynamically expanded sections

Nested tables inside accordions

Non-standard HTML structures

Intelligent parsing and normalization:

Diary Number

Case Number & Type

Filing / Registration / Decision Dates

Bench & First Judge

Case Status & Nature of Disposal

Advanced legal analytics:

Number of hearings

Number of orders

Interim Applications split by:

Petitioner

Respondent

Interlocutors

Production-ready CSV output for analytics or ML pipelines

Data Extracted

The scraper outputs the following fields (non-exhaustive):

Diary Number

Case Number

Case Type

Filing Date

Registration Date

Decision Date

Case Status

Nature of Disposal

CNR Number

Bench

First Judge Name

Petitioner / Respondent

Petitioner & Respondent Advocates

Impleader / Intervenor Advocates

First Hearing Date

Last Listed Date

Number of Hearings

Number of Orders

Number of Interim Applications:

By Petitioner

By Respondent

By Interlocutors

Total

Tech Stack

Python 3.10+

Selenium

Chrome WebDriver

Pandas

Regular Expressions

JavaScript DOM inspection (for selector validation)

How It Works (High-Level)

User navigates to the SCI diary case page

CAPTCHA is solved manually (as required by the website)

Script:

Detects successful page load via DOM markers

Expands required accordion sections

Extracts structured data from nested tables

Normalizes and derives analytical fields

Data is appended to a CSV file for further analysis

Usage
pip install -r requirements.txt
python scraper.py


After launching:

Enter diary number and year in the browser

Solve CAPTCHA

Press ENTER in the terminal

Data is extracted and appended to CSV

Design Decisions

Manual CAPTCHA handling to respect site constraints

DOM-truth based extraction instead of brittle visual assumptions

Explicit waits and guarded selectors for stability

Legal-domain aware parsing (e.g., bench extraction, IA attribution)

Limitations

CAPTCHA cannot be automated

Website structure changes may require selector updates

Intended for research / analytical use, not high-frequency scraping

Future Enhancements

Batch diary number ingestion

Headless execution with manual CAPTCHA handoff

Database-backed storage

Integration with legal NLP pipelines (summarization, RAG, embeddings)

Logging and retry mechanisms
