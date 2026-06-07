import time
import os
import subprocess
from shutil import which
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.firefox import GeckoDriverManager

WAIT_TIMEOUT = 120
PROFILE_NAME = "whatsapp_bot"
PROFILE_DIR = Path.home() / ".mozilla" / "firefox" / PROFILE_NAME


_driver = None
_wait = None


def ensure_firefox_profile(profile_name: str, profile_path: Path) -> Path:
    """Create a persistent Firefox profile if it doesn't exist."""
    if profile_path.exists() and any(profile_path.iterdir()):
        print(f"✅ Existing profile found at: {profile_path}")
        return profile_path
    print(f"🔧 Creating new Firefox profile '{profile_name}'...")
    profile_path.mkdir(parents=True, exist_ok=True)
    full_profile_arg = f'"{profile_name} {profile_path}"'
    cmd = f'firefox -CreateProfile {full_profile_arg}'
    subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    print(f"✅ Profile created")
    return profile_path


def send_message_to_client(phone_number: str, message: str):
    """Send a WhatsApp message using the already‑logged‑in driver."""
    global _driver, _wait
    if _driver is None or _wait is None:
        raise RuntimeError("Bot not started. Call start_bot() first.")

    _driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")
    print(f"⏳ Waiting for chat with {phone_number} to load...")
    _wait.until(ec.presence_of_element_located((By.XPATH, "//div[@id='main']")))
    time.sleep(5)

    # Find input box
    input_box = None
    strategies = [
        "div[contenteditable='true'][data-tab='10']",
        "div[contenteditable='true']",
    ]
    for selector in strategies:
        try:
            _wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, selector)))
            input_box = WebDriverWait(_driver, 10).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            print(f"✅ Input box found using: {selector}")
            break
        except Exception as e:
            print(f"⚠️ Strategy '{selector}' failed: {e}")
            continue
    if not input_box:
        try:
            input_box = _wait.until(
                ec.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
            )
            print("✅ Input box found using XPATH fallback")
        except Exception:
            raise Exception("Could not find message input box")

    print("✏️ Typing message...")
    _driver.execute_script("arguments[0].focus();", input_box)
    input_box.clear()
    input_box.send_keys(Keys.CONTROL + "a")
    input_box.send_keys(Keys.DELETE)
    time.sleep(1)

    for char in message:
        input_box.send_keys(char)
        time.sleep(0.02)
    time.sleep(1)

    send_btn = _wait.until(
        ec.element_to_be_clickable((By.XPATH, "//footer//button[@aria-label='Send']"))
    )
    send_btn.click()
    print(f"✅ Message sent to {phone_number}!")
    time.sleep(2)


def start_bot():
    """Launch Firefox, log into WhatsApp, and keep the driver alive."""
    global _driver, _wait
    profile_path = ensure_firefox_profile(PROFILE_NAME, PROFILE_DIR)

    options = Options()
    options.add_argument("--start-maximized")
    options.profile = str(profile_path)  # ← correct way

    # service = Service(which("geckodriver") or GeckoDriverManager().install())
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    service = Service(os.path.join(BASE_DIR, "geckodriver.exe"))
    _driver = webdriver.Firefox(service=service, options=options)
    _wait = WebDriverWait(_driver, WAIT_TIMEOUT)

    _driver.get("https://web.whatsapp.com")
    print("📱 Waiting for WhatsApp Web to load...")
    try:
        _wait.until(ec.presence_of_element_located((By.ID, "side")))
        print("✅ Already logged in")
    except:
        print("🔐 Scan QR code now...")
        _wait.until(ec.presence_of_element_located((By.ID, "side")))
        print("✅ Login successful")


def close_bot():
    global _driver
    if _driver:
        _driver.quit()
        print("👋 Browser closed.")

if __name__ == "__main__":
    start_bot()
