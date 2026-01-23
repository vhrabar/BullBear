"""
Konfiguracija za Selenium testove
"""
import os

# Base URL za aplikaciju
BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:5173")

DEFAULT_TIMEOUT = 10

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

TEST_USER = {
    "email": "test@fer.unizg.hr",
    "password": "TestPassword123",
    "name": "Test Korisnik"
}

INVALID_USER = {
    "email": "invalid@example.com",
    "password": "wrongpassword"
}

