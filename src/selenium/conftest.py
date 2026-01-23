"""
Pytest fixtures za Selenium testove
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
from datetime import datetime
from config import SCREENSHOT_DIR


@pytest.fixture(scope="function")
def driver():
    """
    Fixture koja stvara i vraća WebDriver instancu.
    Nakon testa automatski zatvara preglednik.
    """
    chrome_options = Options()
    # Headless mode za CI/CD okruženje
    if os.environ.get("HEADLESS", "false").lower() == "true":
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def screenshot_on_failure(driver, request):
    yield
    
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{request.node.name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(filepath)
        print(f"Screenshot spremljen: {filepath}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

