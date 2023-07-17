from selenium import webdriver
import undetected_chromedriver as uc 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from openpyxl import Workbook
from datetime import datetime

# fill in input box w/ booking
def fill_input(driver, tracker):
    wait_for_content(driver, "//input[@id='tracing_by_booking_f:hl12']")
    
    input_box = driver.find_element(By.XPATH, "//input[@id='tracing_by_booking_f:hl12']")
    input_box.clear()
    input_box.send_keys(tracker)
    
    try:
        input_box.send_keys(Keys.ENTER)
    except Exception as e:
        pass
    
def wait_for_content(driver, element):
    # Wait for the JavaScript to fill in elements
    wait = WebDriverWait(driver, 10)  # Maximum wait time of 10 seconds
    element_locator = (By.XPATH, element)
    wait.until(EC.presence_of_element_located(element_locator))
    
def click_details(driver):
    wait_for_content(driver, ".//button[@id='tracing_by_booking_f:hl27:hl53']")
    details_button = driver.find_element(By.XPATH, "//button[@id='tracing_by_booking_f:hl27:hl53']")
    details_button.click()

def confirm_cookies(driver):
    wait_for_content(driver, "//button[@id='accept-recommended-btn-handler']")
    accept_all_button = driver.find_element(By.XPATH, "//button[@id='accept-recommended-btn-handler']")
    accept_all_button.click()
    
def select_container(driver):
    # Wait for table to load
    wait_for_content(driver, "//table[@id='tracing_by_booking_f:hl27']")
    
    # Find the table element by ID
    table = driver.find_element(By.ID, "tracing_by_booking_f:hl27")

    # Find the tbody element within the table element
    tbody = table.find_element(By.XPATH, "./tbody")

    # Find the tr elements within the tbody element
    trs = tbody.find_elements(By.XPATH, "./tr")

    trs[0].click()
    
def search(driver, tracker):
    # Fill input
    fill_input(driver, tracker)
    
    # Select a container
    select_container(driver)
    
    #Go to details page
    click_details(driver)
    
def retrieve_date_info(driver):
    # Find a table with id ABC123. <table> <tbody> <tr> ... <tr> <td>... <td>
    # Collect all the <tr> in the <tbody>
    # Collect the last <tr> in the list, this is the most recent ETA
    # Use regex expression to find a string that matches a date format. i.e. [2023-07-11]
    # Format date
    # return a string formatted like [5/6]
    
    # Wait for table to load
    wait_for_content(driver, "//table[@id='tracing_by_booking_f:hl66']")
    
    # Find the table element by ID
    table = driver.find_element(By.ID, "tracing_by_booking_f:hl66")

    # Find the tbody element within the table element
    tbody = table.find_element(By.XPATH, "./tbody")

    # Find the tr elements within the tbody element
    trs = tbody.find_elements(By.XPATH, "./tr")
    
    relevant_row = trs.pop()
    td_list = relevant_row.find_elements(By.XPATH, "./td")
    
    date = td_list[2].text
    return format_date(date)
  
def click_by_booking(driver):
    # Returns to the booking screen for subsequent searches
    by_booking_button = driver.find_element(By.XPATH, "//a[contains(text(),'by Booking')]")
    by_booking_button.click()

def format_date(date):
    # Parse the input string into a datetime object
    date_object = datetime.strptime(date, "%Y-%m-%d")

    # Format the date as "month/day"
    formatted_date = date_object.strftime("%m/%d")
    return formatted_date

# Setup excel workbook
workbook = Workbook()
worksheet = workbook.active
worksheet.title = "Shipping Date Changes"
worksheet.column_dimensions['A'].width = 25

# Create a new instance of the Firefox driver
options = uc.ChromeOptions()
options.add_argument("--auto-open-devtools-for-tabs")

driver = uc.Chrome(use_subprocess=True, options=options) 
driver.get('https://www.hapag-lloyd.com/en/online-business/track/track-by-booking-solution.html')

# Get list of HAPAG tracking numbers
list_tracking_numbers = open("list-trackers.txt", "r").readlines()

# Confirm cookies
confirm_cookies(driver)

for entry in list_tracking_numbers:
    try:
        search(driver, entry)
        
        date = retrieve_date_info(driver)
        print(date)
        entry = entry.strip()
        row = [entry, date]
        
        # append row into worksheet
        worksheet.append(row)
        click_by_booking(driver)
        
    except Exception as e:
        print(f"Booking date was not found, skipping: {entry}")
        row = [entry.strip(), 'Booking date not found']
        worksheet.append(row)
        click_by_booking(driver)
        continue
    
workbook.save("output/hapag_shipping_dates_changes.xlsx")
driver.quit()