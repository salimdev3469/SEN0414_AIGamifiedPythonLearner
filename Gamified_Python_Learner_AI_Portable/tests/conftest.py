"""
Global pytest configuration and fixtures
"""
import pytest
import os
from django.conf import settings

# Import all fixtures so they're available to all tests
pytest_plugins = [
    'tests.fixtures.base_fixtures',
]


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup test database"""
    with django_db_blocker.unblock():
        # Use in-memory SQLite for tests
        pass


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Automatically enable database access for all tests"""
    pass


@pytest.fixture(scope='session', autouse=True)
def configure_test_settings():
    """Configure Django settings for tests"""
    # Use simpler static files storage for tests (no manifest required)
    settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    yield
    # Restore original setting after tests
    settings.STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


@pytest.fixture
def live_server(live_server):
    """Make live_server available for Selenium tests"""
    return live_server


# ============================================================================
# Selenium WebDriver Fixtures
# ============================================================================

@pytest.fixture(scope='function')
def chrome_browser():
    """Setup Chrome browser with WebDriver Manager"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        options = Options()
        # Headless mode for CI/CD environments
        if os.getenv('HEADLESS', 'true').lower() == 'true':
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Use WebDriver Manager to automatically download and manage ChromeDriver
        # This may take time on first run
        driver_path = ChromeDriverManager().install()
        
        # Fix: WebDriver Manager sometimes returns wrong file (THIRD_PARTY_NOTICES)
        # Find the actual chromedriver.exe file
        import pathlib
        driver_dir = pathlib.Path(driver_path).parent
        actual_driver = None
        
        # Look for chromedriver.exe in the directory
        for file in driver_dir.rglob('chromedriver.exe'):
            actual_driver = str(file)
            break
        
        # If not found, try parent directory
        if not actual_driver:
            parent_dir = driver_dir.parent
            for file in parent_dir.rglob('chromedriver.exe'):
                actual_driver = str(file)
                break
        
        # Use actual driver if found, otherwise use original path
        if actual_driver and pathlib.Path(actual_driver).exists():
            driver_path = actual_driver
        
        service = Service(driver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        yield driver
        driver.quit()
    except ImportError as e:
        pytest.skip(f"Required packages not installed: {e}")
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error message
        if "WinError 193" in error_msg or "geçerli bir Win32 uygulaması değil" in error_msg:
            pytest.skip("Chrome WebDriver executable is invalid or corrupted. Try deleting .wdm cache folder.")
        else:
            pytest.skip(f"Chrome WebDriver not available: {error_msg}")


@pytest.fixture(scope='function')
def browser(chrome_browser):
    """Default browser fixture (uses Chrome by default)"""
    return chrome_browser

