# Selenium UI Automation Tests

This directory contains Selenium WebDriver tests for browser automation using Chrome.

## Features

- ✅ **Automatic WebDriver Management**: Uses `webdriver-manager` to automatically download and manage ChromeDriver
- ✅ **Chrome Browser Support**: Tests run on Google Chrome
- ✅ **Headless Mode**: Runs in headless mode by default (can be disabled for debugging)
- ✅ **Responsive Design Testing**: Tests mobile, tablet, and desktop viewports
- ✅ **Form Validation Testing**: Tests form submission and validation
- ✅ **Login Flow Testing**: End-to-end login/registration flow testing

## Setup

### Prerequisites

1. **Install browser**:
   - Google Chrome

2. **Install dependencies**:
   ```bash
   pip install selenium webdriver-manager pytest pytest-django
   ```

   Or use the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

### WebDriver Management

The tests use `webdriver-manager` to automatically download and manage ChromeDriver. No manual driver installation is needed!

On first run, ChromeDriver will be downloaded automatically.

## Running Tests

### Run All UI Tests

**Windows:**
```bash
RUN_UI_TESTS.bat
```

**Linux/Mac:**
```bash
pytest tests/ui_automation/ -m ui -v
```

### Run Specific Test Classes

```bash
# Login flow tests only
pytest tests/ui_automation/test_selenium_ui.py::TestLoginFlowSelenium -m ui -v

# Browser compatibility tests
pytest tests/ui_automation/test_selenium_ui.py::TestBrowserCompatibility -m ui -v

# Responsive design tests
pytest tests/ui_automation/test_selenium_ui.py::TestResponsiveDesign -m ui -v
```

### Run Tests in Visible Browser (Debug Mode)

Set `HEADLESS=false` environment variable to see browser windows:

**Windows:**
```cmd
set HEADLESS=false
pytest tests/ui_automation/ -m ui -v
```

**Linux/Mac:**
```bash
HEADLESS=false pytest tests/ui_automation/ -m ui -v
```

### Run Tests for Specific Browser

```bash
# Chrome only
pytest ui_automation/test_selenium_ui.py -m ui -k chrome -v
```

## Test Structure

### Available Fixtures

- `browser`: Default browser (Chrome)
- `chrome_browser`: Chrome browser instance
- `live_server`: Django test server instance

### Test Classes

1. **TestLoginFlowSelenium**: Login/registration flow tests
   - Form element presence
   - Successful login flow

2. **TestCodeEditorInteraction**: Code editor tests
   - CodeMirror editor presence
   - Editor interaction

3. **TestFormSubmissionValidation**: Form validation tests
   - Password mismatch validation
   - Form error messages

4. **TestResponsiveDesign**: Responsive design tests
   - Mobile viewport (375x667)
   - Tablet viewport (768x1024)
   - Desktop viewport (1920x1080)

5. **TestBrowserCompatibility**: Browser compatibility tests
   - Chrome compatibility

## Configuration

### Headless Mode

By default, tests run in headless mode (no browser window). To disable:

```bash
# Windows
set HEADLESS=false

# Linux/Mac
export HEADLESS=false
```

### Browser Options

Browser options can be customized in `tests/conftest.py`:

```python
options = Options()
options.add_argument('--headless')  # Remove for visible browser
options.add_argument('--window-size=1920,1080')
# Add more options as needed
```

## Troubleshooting

### WebDriver Not Found

If you see errors like "WebDriver not found":
1. Check internet connection (drivers are downloaded automatically)
2. Ensure browser is installed
3. Try running with `HEADLESS=false` to see error messages

### Tests Timeout

If tests timeout:
1. Increase `implicitly_wait` in `conftest.py`
2. Check that Django test server starts correctly
3. Verify `live_server` fixture is working

### Browser Not Starting

If browser doesn't start:
1. Check browser installation
2. Try running with `HEADLESS=false` to see errors
3. Check browser version compatibility
4. Update `webdriver-manager` to latest version

## CI/CD Integration

For CI/CD environments:

1. Install Chrome in headless mode:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y chromium-browser
   
   # Or use Docker with Chrome image
   ```

2. Set environment variables:
   ```bash
   export HEADLESS=true
   export DISPLAY=:99  # For headless X server
   ```

3. Run tests:
   ```bash
   pytest tests/ui_automation/ -m ui -v
   ```

## Best Practices

1. **Use fixtures**: Always use provided browser fixtures instead of creating drivers manually
2. **Wait for elements**: Use `WebDriverWait` for dynamic content
3. **Clean up**: Fixtures automatically clean up browsers after tests
4. **Headless for CI**: Use headless mode in CI/CD, visible mode for debugging
5. **Chrome required**: Chrome must be installed for tests to run

## Notes

- UI tests are marked with `@pytest.mark.ui` and `@pytest.mark.slow`
- To skip UI tests: `pytest -m "not ui"`
- To run only UI tests: `pytest -m ui`
- Tests use Django's `live_server` fixture for real HTTP server
- All tests require database access (`@pytest.mark.django_db`)

