import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

CSV_PATH = "supreme_court_case_sample.csv"
CASE_STATUS_URL = "https://www.sci.gov.in/case-status-diary-no/"

# -------------------------------------------------
# Utility helpers
# -------------------------------------------------

def stop_if_missing(condition, message):
    if not condition:
        input(f"\nCRITICAL ERROR: {message}\nPress ENTER to stop.")
        raise RuntimeError(message)

def wait_for_case_details_page(driver, timeout=600):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//tr[@data-tab-name='case_details']")
            )
        )
        return True
    except:
        return False

def wait_for_section_header(driver, tab_name, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//tr[@data-tab-name='{tab_name}']")
            )
        )
        return True
    except:
        return False

def expand_section_by_tab(driver, tab_name):
    button = driver.find_element(
        By.XPATH, f"//tr[@data-tab-name='{tab_name}']//button"
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    driver.execute_script("arguments[0].click();", button)

def expand_orders_section(driver):
    try:
        # 1. Find the button by text (most reliable)
        button_xpath = "//button[normalize-space()='Judgement/Orders']"
        button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, button_xpath))
        )

        # 2. Check if already expanded
        is_expanded = button.get_attribute("aria-expanded")
        if is_expanded == "true":
            return

        # 3. Scroll and Click
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
        time.sleep(1) # Small pause for scroll to finish
        try:
            button.click()
        except:
            driver.execute_script("arguments[0].click();", button)
            
        # 4. Wait a moment for animation
        time.sleep(2) 
    except Exception as e:
        print(f"Warning: Could not expand Judgement section: {e}")
    
def normalize_name(text):
    if not text:
        return ""
    # Normalize unicode whitespace
    text = "".join(" " if ord(c) in (160, 8203) else c for c in text)
    text = text.upper()
    
    # Remove everything inside brackets or parentheses (e.g., [AOR], (SCLSC))
    text = re.sub(r"\[.*?\]|\(.*?\)", "", text)
    
    # Remove titles
    text = re.sub(r"\b(MR|MS|MRS|ADV|ADVOCATE|AOR)\b\.?", "", text)
    
    # Remove punctuation and extra whitespace
    text = re.sub(r"[.,]", "", text)
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


# -------------------------------------------------
# Parsing helpers
# -------------------------------------------------

def extract_diary_number(text):
    m = re.search(r"\b\d+/\d+\b", text)
    return m.group(0) if m else ""

def get_first_matching(case_data, keys):
    for k in keys:
        if k in case_data:
            return case_data[k]
    return ""

def extract_case_number(text):
    return text.split("Registered on")[0].strip()

def extract_case_type(text):
    return text.split("No.")[0].strip() if "No." in text else ""

def extract_case_status(text):
    m = re.match(r"[A-Z]+", text.strip())
    return m.group(0) if m else ""

def extract_registration_date(text):
    m = re.search(r"Registered on (\d{2}-\d{2}-\d{4})", text)
    return m.group(1) if m else ""

def extract_filing_date(text):
    m = re.search(r"Filed on (\d{2}-\d{2}-\d{4})", text)
    return m.group(1) if m else ""

def extract_bench_from_case_details(case_data):
    """
    Extracts bench from:
    'Present/Last Listed On' -> '17-10-2024 [HON'BLE ...]'
    """
    text = case_data.get("Present/Last Listed On", "")
    if not text:
        return ""

    # Extract text inside square brackets
    m = re.search(r"\[(.*?)\]", text)
    if not m:
        return ""

    bench = m.group(1)

    # Normalize spacing issues like 'PARDIWALAand'
    bench = re.sub(r"\band\b", " and ", bench, flags=re.IGNORECASE)
    bench = re.sub(r"\s+", " ", bench)

    return bench.strip()

def extract_first_judge(bench):
    if not bench:
        return ""

    # Prefer comma
    if "," in bench:
        return bench.split(",", 1)[0].strip()

    # Split on literal 'and' even if glued
    parts = re.split(r"and", bench, maxsplit=1, flags=re.IGNORECASE)
    return parts[0].strip()

def split_advocate_names(text):
    if not text:
        return []
    # Split on commas or 'and' or '&'
    parts = re.split(r",|&|\band\b", text, flags=re.IGNORECASE)
    return [normalize_name(p) for p in parts if normalize_name(p)]

def expand_ia_section(driver):
    try:
        button = driver.find_element(
            By.XPATH,
            "//button[normalize-space()='Interlocutory Application Documents']"
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", button
        )
        driver.execute_script("arguments[0].click();", button)
    except:
        pass  # section may already be open
    
    

def extract_last_listed_from_case_details(case_data):
    """
    Extracts date from:
    'Present/Last Listed On' -> '17-10-2024 [HON'BLE ...]'
    """
    text = case_data.get("Present/Last Listed On", "")
    if not text:
        return ""

    m = re.match(r"(\d{2}-\d{2}-\d{4})", text.strip())
    return m.group(1) if m else ""

# def extract_hearing_and_order_counts(driver):
#     expand_orders_section(driver)

#     hearing_dates = set()
#     order_dates = set()

#     # Look for a table that follows the 'Judgement/Orders' text
#     # This XPath looks for the row containing the button, then the next row containing a table
#     table_xpath = "//tr[contains(., 'Judgement/Orders')]/following-sibling::tr//table"
    
#     try:
#         # Reduced timeout to 5 seconds - if it's not there, it's likely empty
#         table = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.XPATH, table_xpath))
#         )
        
#         rows = table.find_elements(By.XPATH, ".//tr")
#         for row in rows:
#             full_text = row.text.strip()
#             if not full_text: continue
            
#             dates = re.findall(r"\b\d{2}-\d{2}-\d{4}\b", full_text)
#             if dates:
#                 date = dates[0]
#                 hearing_dates.add(date)
                
#                 # Check for "Judgement" or "Order" in this specific row
#                 if re.search(r"\bJudg(e)?ment\b|\bOrder\b", full_text, re.IGNORECASE):
#                     order_dates.add(date)
                    
#     except Exception:
#         # If no table is found, we don't crash; we just return 0, 0
#         print("DEBUG: No Judgement/Order table found. Assuming count is 0.")

#     print(f"DEBUG: Found {len(hearing_dates)} hearings and {len(order_dates)} orders.")
#     return len(hearing_dates), len(order_dates)

def extract_hearing_and_order_counts(driver):
    expand_orders_section(driver)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//table//tr"))
    )

    time.sleep(1)

    rows = driver.find_elements(By.XPATH, "//table//tr")

    hearing_dates = set()
    order_dates = set()

    for row in rows:
        try:
            # Aggregate visible text from children
            parts = []
            for el in row.find_elements(By.XPATH, ".//td|.//th|.//span|.//a"):
                t = el.text.strip()
                if t:
                    parts.append(t)

            full_text = " ".join(parts)

            # Extract date
            m = re.search(r"\b\d{2}-\d{2}-\d{4}\b", full_text)
            if not m:
                continue

            date = m.group(0)

            # Hearing logic — ONLY ROP
            if "ROP" in full_text.upper():
                hearing_dates.add(date)

            # Order logic — ONLY Judgement / Judgment
            if re.search(r"\bJudg(e)?ment\b", full_text, re.IGNORECASE):
                order_dates.add(date)

        except:
            continue

    print("DEBUG UNIQUE ROP HEARING DATES:", len(hearing_dates))
    print("DEBUG UNIQUE JUDGEMENT DATES:", len(order_dates))

    return len(hearing_dates), len(order_dates)


def extract_first_hearing_from_orders(driver):
    expand_orders_section(driver)

    # Wait for the table to be stable
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href,'.pdf')]")
        )
    )
    
    # Small delay to ensure DOM is stable after expansion
    time.sleep(1)

    # Find all rows
    rows = driver.find_elements(By.XPATH, "//table//tr")

    dates = []

    # Extract text immediately before storing, to avoid stale references
    for row in rows:
        try:
            row_text = row.text  # Get text immediately
            matches = re.findall(r"\b\d{2}-\d{2}-\d{4}\b", row_text)
            for d in matches:
                try:
                    dates.append(datetime.strptime(d, "%d-%m-%Y"))
                except:
                    pass
        except:
            # Skip stale elements
            continue

    print("DEBUG ORDER ROW COUNT:", len(rows))
    print("DEBUG ORDER DATES FOUND:", [d.strftime("%d-%m-%Y") for d in dates])

    if not dates:
        return ""

    return min(dates).strftime("%d-%m-%Y")

# -------------------------------------------------
# Case details extraction
# -------------------------------------------------

def extract_case_details(driver):
    rows = driver.find_elements(
        By.XPATH, "//tr[@data-tab-name='case_details']/following::tr"
    )
    data = {}
    for r in rows:
        if r.get_attribute("data-tab-name"):
            break
        tds = r.find_elements(By.TAG_NAME, "td")
        if len(tds) == 2:
            data[tds[0].text.strip()] = tds[1].text.strip()
    return data

def extract_ia_filed_by(driver):
    # Expand IA section
    expand_ia_section(driver)

    try:
        # This XPath finds the "INTERLOCUTARY APPLICATION(s)" header row, 
        # then moves to the next row's table and grabs the "Filed By" spans.
        xpath_query = (
            "//tr[td/strong[contains(text(), 'INTERLOCUTARY APPLICATION')]]"
            "/following-sibling::tr[1]//td[@data-th='Filed By']/span"
        )
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_query))
        )
        
        cells = driver.find_elements(By.XPATH, xpath_query)
        return [c.text.strip() for c in cells]
    except:
        return []

# -------------------------------------------------
# Core scraping logic
# -------------------------------------------------

def scrape_current_case(driver):
    input("Press ENTER ONLY after the case details page is fully visible...")

    stop_if_missing(wait_for_case_details_page(driver), "Case details page not detected")

    case_data = extract_case_details(driver)

    # -------- Listing Dates --------
    stop_if_missing(
    wait_for_section_header(driver, "listing_dates"),
    "Listing Dates section header missing"
    )

    expand_section_by_tab(driver, "listing_dates")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//td[@data-th='CL Date']/span"))
    )

    last_listed = extract_last_listed_from_case_details(case_data)

    listing_rows = driver.find_elements(By.XPATH, "//td[@data-th='CL Date']/ancestor::tr")
    bench = extract_bench_from_case_details(case_data)
    num_hearings, num_orders = extract_hearing_and_order_counts(driver)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, "//table[contains(@class,'caseDetailsTable')]")
        )
    )
    
    first_judge = extract_first_judge(bench)
    print("DEBUG FIRST JUDGE:", first_judge)
    
    # -------- Interim Applications Counts --------
    
    ia_filed_by = extract_ia_filed_by(driver)
    
    # Split names in case there are multiple advocates listed in the main table
    pet_advs = split_advocate_names(case_data.get("Petitioner Advocate(s)", ""))
    resp_advs = split_advocate_names(case_data.get("Respondent Advocate(s)", ""))

    num_ia_petitioner = 0
    num_ia_defendant = 0
    num_ia_interlocuters = 0

    for f in ia_filed_by:
        norm_f = normalize_name(f)
        if not norm_f: continue

        # Check if the person filing the IA is one of the Petitioner advocates
        if any(norm_f == p for p in pet_advs):
            num_ia_petitioner += 1
        # Check if they are one of the Respondent advocates
        elif any(norm_f == r for r in resp_advs):
            num_ia_defendant += 1
        else:
            num_ia_interlocuters += 1

    print("DEBUG PET ADV:", pet_advs)
    print("DEBUG IA FILED BY:", ia_filed_by)
    print("DEBUG PET ADV (norm list):", pet_advs)
    print("DEBUG FILED BY (norm):", [normalize_name(f) for f in ia_filed_by])
    
    total_num_ia = (
    num_ia_petitioner +
    num_ia_defendant +
    num_ia_interlocuters
    )
    # -------- Orders --------
    expand_orders_section(driver)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'.pdf')]"))
    )

    # -------- Derived fields --------
    raw_diary = get_first_matching(case_data, ["Diary Number", "Diary No."])
    raw_case_no = get_first_matching(case_data, ["Case Number", "Case No."])
    raw_status = get_first_matching(case_data, ["Status/Stage", "Status"])
    raw_cnr = get_first_matching(case_data, ["CNR Number", "CNR No."])

    nature_of_disposal = get_first_matching(case_data, ["Disp.Type"])
    decision_date = last_listed if extract_case_status(raw_status) == "DISPOSED" else ""

    impleader_adv = get_first_matching(case_data, ["Impleaders Advocate(s)"]) or "0"
    intervenor_adv = get_first_matching(case_data, ["Intervenor Advocate(s)"]) or "0"
    
    num_hearings, num_orders = extract_hearing_and_order_counts(driver)

    return {
        "Diary Number": extract_diary_number(raw_diary),
        "Case Number": extract_case_number(raw_case_no),
        "Case Type": extract_case_type(raw_case_no),
        "Filing Date": extract_filing_date(raw_diary),
        "Registration Date": extract_registration_date(raw_case_no),
        "Case Status": extract_case_status(raw_status),
        "Nature of Disposal": nature_of_disposal,
        "CNR Number": raw_cnr,
        "Decision Date": decision_date,
        "Bench": bench,
        "First Judge Name": extract_first_judge(bench),
        "Petitioner": case_data.get("Petitioner(s)", ""),
        "Respondent": case_data.get("Respondent(s)", ""),
        # CHANGE THESE TWO LINES:
        "Petitioner Legal Representative": ", ".join(pet_advs),
        "Respondent Legal Representative": ", ".join(resp_advs),
        "Impleader Advocate(s)": impleader_adv,
        "Intervenor Advocate(s)": intervenor_adv,
        "First Hearing Date": extract_first_hearing_from_orders(driver),
        "Last Listed On": last_listed,
        "Number of Hearings": num_hearings,
        "Number of Orders": num_orders,
        "Number of Interim Applications by Petitioner": num_ia_petitioner,
        "Number of Interim Applications by Defendant": num_ia_defendant,
        "Number of Interim Applications by Interlocuters": num_ia_interlocuters,    
        "Total Number of Interim Applications": total_num_ia,
    }

# -------------------------------------------------
# Runner
# -------------------------------------------------

def run():
    driver = webdriver.Chrome()
    
    driver.get(CASE_STATUS_URL)
    row = scrape_current_case(driver)
    df = pd.read_csv(CSV_PATH)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

if __name__ == "__main__":
    run()

