import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[normalize-space()='Judgement/Orders']")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", button
    )

    try:
        # Attempt real user click first
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(button))
        button.click()
    except:
        # Fallback: JS click if intercepted
        driver.execute_script("arguments[0].click();", button)

    # CRITICAL: wait for table rows, not links
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//table//tr")
        )
    )
    
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

def extract_bench(text):
    if "[" in text and "]" in text:
        return text.split("[", 1)[1].rsplit("]", 1)[0].strip()
    return ""

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
    
    from datetime import datetime

def extract_first_order_date(driver):
    # """
    # Extracts the earliest date from the Judgement/Orders section.
    # Assumes dates are present in dd-mm-yyyy format.
    # """
    # expand_orders_section(driver)

    # # Wait for any order row to load
    # WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located(
    #         (By.XPATH, "//a[contains(@href,'.pdf')]")
    #     )
    # )

    # # Common pattern: date appears in the same row as the PDF link
    # date_cells = driver.find_elements(
    #     By.XPATH,
    #     "//a[contains(@href,'.pdf')]/ancestor::tr//td"
    # )

    # dates = []
    # for cell in date_cells:
    #     text = cell.text.strip()
    #     try:
    #         # strict parse to avoid junk text
    #         dt = datetime.strptime(text, "%d-%m-%Y")
    #         dates.append(dt)
    #     except:
    #         continue

    # if not dates:
    #     return ""

    # return min(dates).strftime("%d-%m-%Y")

    expand_orders_section(driver)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@href,'.pdf')]")
        )
    )

    rows = driver.find_elements(
        By.XPATH, "//a[contains(@href,'.pdf')]/ancestor::tr"
    )

    print("DEBUG ORDER ROW COUNT:", len(rows))

    for i, row in enumerate(rows):
        print(f"\n--- ORDER ROW {i+1} TEXT ---")
        print(row.text)

    return ""

from datetime import datetime

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

    listing_dates = [c.text.strip() for c in driver.find_elements(By.XPATH, "//td[@data-th='CL Date']/span")]
    last_listed = max(listing_dates)
    num_hearings = len(set(listing_dates))

    listing_rows = driver.find_elements(By.XPATH, "//td[@data-th='CL Date']/ancestor::tr")
    bench = ""

    for row in listing_rows:
        try:
            date_cell = row.find_element(
                By.XPATH, ".//td[@data-th='CL Date']/span"
            )
            if date_cell.text.strip() == last_listed:
                judges_cell = row.find_element(
                    By.XPATH, ".//td[@data-th='Judges']/span"
                )
                bench = judges_cell.text.strip()
                break
        except:
            continue
    
    
    
    first_judge = extract_first_judge(bench)
    print("DEBUG FIRST JUDGE:", first_judge)

    # -------- Interim Applications Counts --------
    
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
    num_orders = len(driver.find_elements(By.XPATH, "//a[contains(@href,'.pdf')]"))

    first_hearing = extract_first_order_date(driver)

    # -------- Derived fields --------
    raw_diary = get_first_matching(case_data, ["Diary Number", "Diary No."])
    raw_case_no = get_first_matching(case_data, ["Case Number", "Case No."])
    raw_status = get_first_matching(case_data, ["Status/Stage", "Status"])
    raw_cnr = get_first_matching(case_data, ["CNR Number", "CNR No."])

    nature_of_disposal = get_first_matching(case_data, ["Disp.Type"])
    decision_date = last_listed if extract_case_status(raw_status) == "DISPOSED" else ""

    impleader_adv = get_first_matching(case_data, ["Impleaders Advocate(s)"]) or "0"
    intervenor_adv = get_first_matching(case_data, ["Intervenor Advocate(s)"]) or "0"

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

