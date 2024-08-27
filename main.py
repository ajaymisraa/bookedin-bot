import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, date

# Configuration
URL = "https://bookedin.com/book/chapel-hill-barber-shop"
REFRESH_INTERVAL = 120  
DESIRED_DAYS = ["Monday", "Tuesday", "Wednesday"]
DESIRED_TIMEFRAMES = {
    "Tuesday": ("10:00", "14:00"),
    "Wednesday": ("12:00", "16:00"),
    "Monday": ("10:00", "11:00")
}
YOUR_INFO = {
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "1234567890",
    "phone_type": "Mobile"
}

def is_time_in_range(time_str, desired_range):
    time_obj = datetime.strptime(time_str, "%I:%M%p").time()
    start = datetime.strptime(desired_range[0], "%H:%M").time()
    end = datetime.strptime(desired_range[1], "%H:%M").time()
    return start <= time_obj <= end

def check_and_book_appointment():
    driver = webdriver.Chrome()  
    driver.get(URL)

    try:
        next_avail_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn") and .//span[contains(text(), "Next Avail")]]'))
        )
        next_avail_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'services'))
        )

        date_element = driver.find_element(By.XPATH, '//h3[contains(@class, "hidden lg:flex font-semibold text-6")]')
        if date_element:
            date_text = date_element.text
            print(f"Available appointment date: {date_text}")

            current_year = date.today().year
            appointment_date = datetime.strptime(f"{date_text}, {current_year}", "%A, %b %d, %Y")
            day_of_week = appointment_date.strftime("%A")

            if day_of_week in DESIRED_DAYS:
                time_slots = driver.find_elements(By.XPATH, '//a[contains(@class, "btn btn-company-brand")]')
                
                for slot in time_slots:
                    time_str = slot.text
                    if is_time_in_range(time_str, DESIRED_TIMEFRAMES[day_of_week]):
                        slot.click()
                        print(f"Selected time slot: {time_str}")
                        
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'form'))
                        )

                        driver.find_element(By.NAME, 'name').send_keys(YOUR_INFO['name'])
                        driver.find_element(By.NAME, 'email').send_keys(YOUR_INFO['email'])
                        driver.find_element(By.NAME, 'phone').send_keys(YOUR_INFO['phone'])
                        Select(driver.find_element(By.NAME, 'phoneType')).select_by_visible_text(YOUR_INFO['phone_type'])

                        driver.find_element(By.XPATH, '//button[contains(text(), "Book It")]').click()
                        print("Appointment booked!")
                        return True
                
                print("No suitable time slots available")
            else:
                print(f"Available date {day_of_week} is not in desired days")
        else:
            print("No available appointments found")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    return False

def main():
    while True:
        print("Checking for appointments...")
        if check_and_book_appointment():
            break
        print(f"Waiting {REFRESH_INTERVAL} seconds before next check...")
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()