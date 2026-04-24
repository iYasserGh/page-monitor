import time
import hashlib
import requests
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= Settings =================
TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN', 'your_bot_token_here')
TELEGRAM_CHAT_ID = os.environ.get('CHAT_ID', 'your_chat_id_here')
URL_TO_MONITOR = os.environ.get('URL_TO_MONITOR', 'your_url_to_monitor_here')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 300))
RISK_MODE = os.environ.get('RISK_MODE', 'False').lower() == 'true'
# ============================================

def send_telegram_photo(photo_path: str, caption: str):
    """Function to send photos via Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
            files = {'photo': photo}
            response = requests.post(url, data=payload, files=files)
            response.raise_for_status()
    except Exception as e:
        print(f"Error sending photo: {e}")

def take_full_screenshot(driver, file_name: str):
    """Function to take a full page screenshot"""
    # Measure the actual dimensions of the page after JS loads
    width = driver.execute_script("return document.body.parentNode.scrollWidth")
    height = driver.execute_script("return document.body.parentNode.scrollHeight")
    driver.set_window_size(width, height)
    time.sleep(1) # Short wait to ensure dimensions are applied
    driver.save_screenshot(file_name)

def get_page_data(driver):
    """Function to fetch page hash and screenshot"""
    driver.get(URL_TO_MONITOR)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5) # Additional wait to ensure all JS content is loaded
        # accept cookies if the button is present
        try:
            accept_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]")))
            accept_button.click()
            time.sleep(2) # Wait for the page to adjust after accepting cookies
        except:
            pass
        content = driver.find_element(By.TAG_NAME, "body").text
        page_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        temp_filename = "current_state.png"
        take_full_screenshot(driver, temp_filename)
        
        return page_hash, temp_filename
    except Exception as e:
        print(f"Error during processing: {e}")
        return None, None

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # تشغيل بدون واجهة
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

    if os.name == 'nt' or not os.path.exists("/usr/bin/chromedriver"):  # Windows
        service = Service(ChromeDriverManager().install())
    elif os.name == 'posix':  # Linux/Mac
        service = Service(executable_path="/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    previous_hash = None
    old_screenshot = "previous_state.png"

    send_telegram_photo("monitoring_started.jpg", "<b>Monitoring Started</b>\nThe monitoring system has been initiated and is now active.")    

    try:
        print("Monitoring system with screenshots is running...")
        while True:
            current_hash, current_screenshot = get_page_data(driver)
            
            if current_hash:
                if previous_hash is None:
                    previous_hash = current_hash
                    # Save the first screenshot as a reference
                    if os.path.exists(current_screenshot):
                        os.rename(current_screenshot, old_screenshot)
                    print("Initial state of the website saved.")
                
                elif current_hash != previous_hash:
                    print("Content changed! Sending images...")
                    
                    # Send the old image
                    send_telegram_photo(old_screenshot, "<b>Previous Version (Before Change)</b>")
                    
                    # Send the new image
                    send_telegram_photo(current_screenshot, f"<b>New Version (Change Detected)</b>\nLink: {URL_TO_MONITOR}")
                    
                    # Update the reference
                    previous_hash = current_hash
                    if os.path.exists(old_screenshot): os.remove(old_screenshot)
                    os.rename(current_screenshot, old_screenshot)
                else:
                    print("No changes detected.")
                    if os.path.exists(current_screenshot): os.remove(current_screenshot)
            
            if RISK_MODE:
                # may block the ip by the wevsite
                sleep_value = CHECK_INTERVAL
            else:
                sleep_value = CHECK_INTERVAL + random.randint(-20, 20)
                sleep_value = max(10, sleep_value)
            
            time.sleep(sleep_value)
            
    except KeyboardInterrupt:
        print("\nScript stopped manually.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()