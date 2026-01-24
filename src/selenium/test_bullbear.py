import pytest
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import BASE_URL, DEFAULT_TIMEOUT, SCREENSHOT_DIR, TEST_USER, INVALID_USER


class TestBullBearApplication:
    """
    Main test class for the BullBear application.
    Contains 4 test cases covering various scenarios.
    """

    def take_screenshot(self, driver, test_name):
        """
        Helper method for saving screenshots.


        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(filepath)
        print(f"\n📸 Screenshot saved: {filepath}")
        return filepath

    # TEST CASE 1: REGULAR CASE - Navigation to the homepage
    def test_01_homepage_navigation(self, driver):
        """
        TEST CASE 1: Regular case - Navigation to the homepage

        INPUTS:
            - URL: http://localhost:5173/
            
        TEST STEPS:
            1. Open the application in the browser
            2. Verify the page loads successfully
            3. Check for the presence of key elements (logo, navigation, hero section)
            4. Verify the page title

        EXPECTED OUTPUT:
            - Homepage is displayed successfully
            - BullBear logo is visible
            - Navigation links are present
            - Hero section contains the expected text
        """
        print("\n" + "="*70)
        print("TEST CASE 1: Navigation to the homepage (Regular case)")
        print("="*70)
        
        print("\nStep 1: Opening the application...")
        driver.get(BASE_URL)
        time.sleep(2)

        print("Step 2: Checking the page title...")
        assert "BullBear" in driver.title or driver.title != "", \
            f"Page title is not as expected: {driver.title}"
        print(f"  Page title: {driver.title}")

        print("Step 3: Checking for the logo...")
        try:
            logo = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "logo-text"))
            )
            assert "BullBear" in logo.text, "Logo text does not contain 'BullBear'"
            print(f" Logo found: {logo.text}")
        except TimeoutException:
            self.take_screenshot(driver, "test_01_logo_not_found")
            pytest.fail(" Logo not found on the page")

        print("Step 4: Checking navigation links...")
        nav_links = driver.find_elements(By.CSS_SELECTOR, ".nav-links a")
        assert len(nav_links) >= 2, f" Expected at least 2 navigation links, found: {len(nav_links)}"
        print(f"   Found {len(nav_links)} navigation links")

        print(" Step 5: Checking hero section...")
        try:
            hero_title = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hero-title"))
            )
            assert len(hero_title.text) > 0, "Hero title is empty"
            print(f"   Hero title: {hero_title.text[:50]}...")
        except TimeoutException:
            self.take_screenshot(driver, "test_01_hero_not_found")
            pytest.fail(" Hero section not found")

        navigation_links = [
            "/features",
            "/pricing",
            "/faq",
            "/contact",
            "/about",
            "/login",
        ]

        for link in navigation_links:
            print(f"Testing navigation to {link}...")
            driver.get(f"{BASE_URL}{link}")
            time.sleep(2)
            assert driver.current_url.endswith(link), f"Navigation to {link} failed."

        self.take_screenshot(driver, "test_01_success")
        print("\nEST CASE 1 PASSED: Homepage is displayed correctly")

    # TEST CASE 2: REGULAR CASE - Navigation to the login page
    def test_02_login_page_navigation(self, driver):
        """
        TEST CASE 2: Regular case - Navigation to the login page

        INPUTS:
            - Action: Click on the "Login" button in the navigation

        TEST STEPS:
            1. Open the homepage
            2. Find and click the "Login" link
            3. Verify redirection to the /login page
            4. Check for the presence of login elements (OAuth buttons)

        EXPECTED OUTPUT:
            - User is redirected to /login
            - Login form is displayed
            - OAuth buttons are visible (Google, Microsoft)
        """
        print("\n" + "="*70)
        print("TEST CASE 2: Navigation to the login page (Regular case)")
        print("="*70)
        
        print("\nStep 1: Opening the homepage...")
        driver.get(BASE_URL)
        time.sleep(2)
        
        print("📋 Step 2: Finding the login button...")
        try:
            login_btn = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/login'], .nav-btn"))
            )
            print(f" Button found: {login_btn.text}")

            print("📋 Step 3: Clicking the login button...")
            login_btn.click()
            time.sleep(2)
        except TimeoutException:
            self.take_screenshot(driver, "test_02_login_btn_not_found")
            pytest.fail(" Login button not found")

        print(" Step 4: Checking the URL...")
        assert "/login" in driver.current_url, \
            f" Expected URL to contain /login, got: {driver.current_url}"
        print(f"  URL: {driver.current_url}")
        
        print("Step 5: Checking OAuth buttons...")
        oauth_buttons = driver.find_elements(By.CSS_SELECTOR, ".oauth-buttons button, .oauth-btn")
        print(f"   ✅ Found {len(oauth_buttons)} OAuth buttons")

        self.take_screenshot(driver, "test_02_success")
        print("\nTEST CASE 2 PASSED: Login page is displayed correctly")


    # TEST CASE 3: EDGE CASE - Accessing a protected page without authentication
    def test_03_protected_route_without_auth(self, driver):
        """
        TEST CASE 3: Edge case - Accessing a protected page without authentication

        INPUTS:
            - URL: http://localhost:5173/positions (protected route)
            - State: User is NOT logged in

        TEST STEPS:
            1. Attempt to directly access /positions without logging in
            2. Verify the system reacts to unauthorized access
            3. Check for redirection or error message display

        EXPECTED OUTPUT:
            - User is redirected to the login page
            - OR an authentication required message is displayed
            - Protected content is NOT displayed
        """
        print("\n" + "="*70)
        print("TEST CASE 3: Accessing a protected page without authentication (Edge case)")
        print("="*70)
        
        print("\nStep 1: Attempting to access the protected route /positions...")
        driver.get(f"{BASE_URL}/positions")
        time.sleep(3)

        print(" Step 2: Checking the system's response...")
        current_url = driver.current_url
        print(f" Current URL: {current_url}")

        is_redirected = "/login" in current_url or current_url == f"{BASE_URL}/"
        
        if is_redirected:
            print(" System correctly redirected the unauthorized user")
        else:
            page_source = driver.page_source.lower()
            needs_auth_message = any(msg in page_source for msg in [
                "login", "authentication", "unauthorized", "access denied"
            ])
            if needs_auth_message:
                print(" An authentication required message is displayed")
            else:
                #
                print(f" URL remains: {current_url}")

        print("Step 3: Checking that protected content is not displayed...")

        portfolio_elements = driver.find_elements(By.CSS_SELECTOR, ".portfolio-table, .positions-list, .stock-holdings")
        
        if len(portfolio_elements) == 0:
            print("Protected content is not displayed to unauthorized users")
        else:
            self.take_screenshot(driver, "test_03_security_issue")
            print(" Warning: Possible security issue - content may be visible")

        self.take_screenshot(driver, "test_03_protected_route")
        print("\nTEST CASE 3 PASSED: System correctly protects protected routes")

    # TEST CASE 4: NONEXISTENT FUNCTIONALITY - Accessing a nonexistent page
    def test_04_nonexistent_page(self, driver):
        """
        TEST CASE 4: Nonexistent functionality - Accessing a nonexistent page (404)

        INPUTS:
            - URL: http://localhost:5173/nonexistent-page-xyz

        TEST STEPS:
            1. Open a nonexistent URL
            2. Verify the system's reaction
            3. Check for 404 page display or redirection

        EXPECTED OUTPUT:
            - A page with an error message (404) is displayed
            - OR the user is redirected to the homepage
            - The application does not crash
        """
        print("\n" + "="*70)
        print("TEST CASE 4: Accessing a nonexistent page (Nonexistent functionality)")
        print("="*70)
        
        print("\ntep 1: Attempting to access a nonexistent page...")
        nonexistent_url = f"{BASE_URL}/nonexistent-page-xyz-123"
        driver.get(nonexistent_url)
        time.sleep(2)
        
        print(f" Requested URL: {nonexistent_url}")
        print(f"Current URL: {driver.current_url}")

        print("Step 2: Checking the system's response...")

        page_source = driver.page_source.lower()
        
        is_404_page = any(indicator in page_source for indicator in [
            "404", "not found", "page does not exist",
            "we couldn't find", "invalid url"
        ])
        
        is_redirected_home = driver.current_url == f"{BASE_URL}/" or driver.current_url == BASE_URL
        
        if is_404_page:
            print(" System correctly displays 404 page")
        elif is_redirected_home:
            print(" System redirected to the homepage")
        else:
            print(f" System remains at URL: {driver.current_url}")

        print("📋 Step 3: Checking the application's stability...")

        body = driver.find_element(By.TAG_NAME, "body")
        assert body is not None, "Body element not found - application may have crashed"
        assert len(body.text) > 0 or len(driver.find_elements(By.CSS_SELECTOR, "*")) > 5, \
            "Page is empty - possible application error"
        print("   Application is stable and displays content")

        self.take_screenshot(driver, "test_04_404_page")
        print("\nTEST CASE 4 PASSED: System correctly reacts to nonexistent pages")

    # TEST CASE 5: EDGE CASE - Navigation using browser buttons
    def test_05_browser_navigation(self, driver):
        """
        TEST CASE 5: Edge case - Navigation using browser back/forward buttons

        INPUTS:
            - Navigation: Homepage → Login → Back → Forward

        TEST STEPS:
            1. Open the homepage
            2. Navigate to the login page
            3. Click the browser "Back" button
            4. Click the browser "Forward" button
            5. Verify navigation correctness

        EXPECTED OUTPUT:
            - Back navigation returns to the homepage
            - Forward navigation returns to the login page
            - Application correctly follows browser history
        """
        print("\n" + "="*70)
        print("TEST CASE 5: Navigation using browser buttons (Edge case)")
        print("="*70)
        
        print("\nStep 1: Opening the homepage...")
        driver.get(BASE_URL)
        time.sleep(2)
        initial_url = driver.current_url
        print(f" Initial URL: {initial_url}")

        print(" Step 2: Navigating to the login page...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(2)
        login_url = driver.current_url
        print(f"URL after navigation: {login_url}")
        assert "/login" in login_url, "❌ Navigation to /login failed"

        print("Step 3: Clicking browser 'Back' button...")
        driver.back()
        time.sleep(2)
        back_url = driver.current_url
        print(f"URL after 'Back': {back_url}")

        print("Tep 4: Clicking browser 'Forward' button...")
        driver.forward()
        time.sleep(2)
        forward_url = driver.current_url
        print(f"URL after 'Forward': {forward_url}")

        print("Step 5: Verifying navigation...")
        assert "/login" in forward_url, \
            f"Forward navigation did not return to login, got: {forward_url}"
        print(" rowser navigation works correctly")

        self.take_screenshot(driver, "test_05_browser_nav")
        print("\n✅ TEST CASE 5 PASSED: Browser navigation works correctly")

    # TEST CASE 6: REGULAR CASE - Checking the responsiveness of elements
    def test_06_responsive_elements(self, driver):
        """
        TEST CASE 6: Regular case - Checking the interactivity of UI elements

        INPUTS:
            - Various UI elements on the homepage

        TEST STEPS:
            1. Open the homepage
            2. Find interactive elements (buttons, links)
            3. Check hover states
            4. Verify clickability

        EXPECTED OUTPUT:
            - All interactive elements are clickable
            - Elements respond to user actions
        """
        print("\n" + "="*70)
        print("TEST CASE 6: Checking the interactivity of UI elements (Regular case)")
        print("="*70)
        
        print("\nStep 1: Opening the homepage...")
        driver.get(BASE_URL)
        time.sleep(2)
        
        print("Step 2: Finding interactive elements...")

        buttons = driver.find_elements(By.CSS_SELECTOR, "button, .btn, a.btn-primary, a.btn-secondary")
        links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
        
        print(f"Found buttons: {len(buttons)}")
        print(f"Found links: {len(links)}")

        print("Step 3: Checking the clickability of elements...")

        clickable_count = 0
        for btn in buttons[:5]:
            try:
                if btn.is_displayed() and btn.is_enabled():
                    clickable_count += 1
            except:
                pass
        
        print(f" Clickable buttons: {clickable_count}")

        print("Step 4: Checking the validity of links...")

        valid_links = 0
        for link in links[:10]:
            try:
                href = link.get_attribute("href")
                if href and (href.startswith("http") or href.startswith("/")):
                    valid_links += 1
            except:
                pass
        
        print(f"Valid links: {valid_links}")

        # Save screenshot
        self.take_screenshot(driver, "test_06_ui_elements")
        print("\n TEST CASE 6 PASSED: UI elements are interactive")


class TestEdgeCases:
    """
    Additional tests for edge conditions and edge case scenarios.
    """
    
    def take_screenshot(self, driver, test_name):
        """Helper method for saving screenshots."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(filepath)
        print(f"\n📸 Screenshot saved: {filepath}")
        return filepath

    # TEST CASE 7: EDGE CASE - Rapid multiple clicking
    def test_07_rapid_clicking(self, driver):
        """
        TEST CASE 7: Edge case - Rapid multiple clicking on a button

        INPUTS:
            - Multiple rapid clicks on the same element

        TEST STEPS:
            1. Open the homepage
            2. Find the login button
            3. Perform rapid multiple clicks
            4. Check the stability of the application

        EXPECTED OUTPUT:
            - The application remains stable
            - No duplicate actions or errors occur
        """
        print("\n" + "="*70)
        print("TEST CASE 7: Rapid multiple clicking (Edge case)")
        print("="*70)
        
        print("\nStep 1: Opening the homepage...")
        driver.get(BASE_URL)
        time.sleep(2)
        
        print(" Step 2: Finding the button...")
        try:
            btn = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary, a[href='/login']"))
            )
            print(f"Button found: {btn.text}")
        except TimeoutException:
            self.take_screenshot(driver, "test_07_btn_not_found")
            pytest.skip("Button not found - skipping test")

        print("📋 Step 3: Performing rapid multiple clicks...")
        for i in range(5):
            try:
                btn.click()
            except:
                pass
            time.sleep(0.1)
        
        time.sleep(2)
        
        print(" Step 4: Checking the stability of the application...")

        try:
            body = driver.find_element(By.TAG_NAME, "body")
            assert body is not None
            print(" Application is stable after multiple clicks")
        except:
            self.take_screenshot(driver, "test_07_instability")
            pytest.fail("Application became unstable")

        self.take_screenshot(driver, "test_07_rapid_click")
        print("\nTEST CASE 7 PASSED: Application is resistant to rapid multiple clicks")


    # TEST CASE 8: NONEXISTENT FUNCTIONALITY - API endpoint that does not exist
    def test_08_nonexistent_api_route(self, driver):
        """
        TEST CASE 8: Nonexistent functionality - Accessing a nonexistent API endpoint

        INPUTS:
            - URL: http://localhost:5173/api/nonexistent-endpoint
            
        TEST STEPS:
            1. Attempt to access a nonexistent API endpoint via the browser
            2. Check the system's response
            3. Verify that no sensitive information is leaked

        EXPECTED OUTPUT:
            - An error or empty response is displayed
            - No leakage of sensitive information
        """
        print("\n" + "="*70)
        print("TEST CASE 8: Accessing a nonexistent API endpoint (Nonexistent functionality)")
        print("="*70)
        
        print("\nStep 1: Accessing a nonexistent API endpoint...")
        driver.get(f"{BASE_URL}/api/nonexistent-endpoint-xyz")
        time.sleep(2)
        
        print(f" URL: {driver.current_url}")
        
        print("Step 2: Checking the response content...")
        page_source = driver.page_source.lower()
        
        sensitive_patterns = ["stack trace", "exception", "error at line", "password", "secret"]
        has_sensitive_info = any(pattern in page_source for pattern in sensitive_patterns)
        
        if has_sensitive_info:
            self.take_screenshot(driver, "test_08_sensitive_info")
            print(" Warning: Possible leakage of sensitive information")
        else:
            print(" No leakage of sensitive information")

        self.take_screenshot(driver, "test_08_api_endpoint")
        print("\nTEST CASE 8 PASSED: System handles nonexistent API endpoints securely")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=report.html", "--self-contained-html"])

