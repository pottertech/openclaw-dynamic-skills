---
name: software-tester
description: Testing strategies, automation frameworks, and quality assurance practices. Use when writing tests, setting up CI/CD pipelines, planning QA strategy, or debugging test failures.
---

# Software Tester

Comprehensive testing strategies, automation frameworks, and quality assurance practices for reliable software.

## When to Use

- Writing unit, integration, or e2e tests
- Setting up CI/CD testing pipelines
- Planning QA strategy
- Debugging test failures
- Performance testing
- Security testing
- Test automation decisions
- Quality metrics and reporting

## Testing Pyramid

```
        /\
       /  \      E2E Tests (10%)
      /----\     UI, full workflow
     /      \    
    /--------\   Integration Tests (20%)
   /          \  API, database, services
  /------------\ 
 /              \ Unit Tests (70%)
/________________\ Functions, classes, modules
```

### Unit Tests

**Purpose:** Test individual functions/classes in isolation

**Characteristics:**
- Fast (<10ms per test)
- Isolated (mocks/stubs for dependencies)
- Deterministic (same result every time)
- High coverage target (80%+)

**Example (Python/pytest):**
```python
def test_add_numbers():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

**Example (JavaScript/Jest):**
```javascript
test('adds numbers correctly', () => {
  expect(add(2, 3)).toBe(5);
  expect(add(-1, 1)).toBe(0);
});

test('throws on divide by zero', () => {
  expect(() => divide(10, 0)).toThrow(ZeroDivisionError);
});
```

### Integration Tests

**Purpose:** Test interactions between components

**Characteristics:**
- Moderate speed (<1s per test)
- Real dependencies (database, API)
- Test boundaries and contracts
- Coverage: critical paths

**Example (API Integration):**
```python
def test_user_creation_flow():
    # Create user via API
    response = client.post('/users', json={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    
    # Verify in database
    user = db.query(User).filter_by(email='test@example.com').first()
    assert user is not None
    assert user.name == 'Test User'
```

### E2E Tests

**Purpose:** Test complete user workflows

**Characteristics:**
- Slower (5-30s per test)
- Full stack (UI → API → DB)
- Critical user journeys only
- Flakiness management needed

**Example (Playwright):**
```python
from playwright.sync_api import sync_playwright

def test_login_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to login
        page.goto('https://app.example.com/login')
        
        # Fill form
        page.fill('input[name="email"]', 'user@example.com')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        
        # Verify success
        page.wait_for_selector('.dashboard')
        assert page.url.endswith('/dashboard')
        
        browser.close()
```

## Test Frameworks

### Python

**pytest:**
```python
# Installation
pip install pytest pytest-cov pytest-mock

# Run tests
pytest                    # All tests
pytest -v                 # Verbose
pytest -x                 # Stop on first failure
pytest --cov=app          # Coverage report
pytest tests/unit/        # Specific directory
pytest -k "test_user"     # Filter by name

# Fixtures
@pytest.fixture
def sample_user():
    return User(name='Test', email='test@example.com')

def test_user_creation(sample_user):
    assert sample_user.name == 'Test'
```

**unittest (built-in):**
```python
import unittest

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User('Test', 'test@example.com')
    
    def test_user_name(self):
        self.assertEqual(self.user.name, 'Test')
    
    def test_user_email(self):
        self.assertEqual(self.user.email, 'test@example.com')

if __name__ == '__main__':
    unittest.main()
```

### JavaScript/TypeScript

**Jest:**
```javascript
// Installation
npm install --save-dev jest @types/jest

// Run tests
npm test                  # All tests
npm test -- --watch       # Watch mode
npm test -- --coverage    # Coverage
npm test -- --verbose     # Verbose

// Test file
describe('User', () => {
  let user;
  
  beforeEach(() => {
    user = new User('Test', 'test@example.com');
  });
  
  test('has correct name', () => {
    expect(user.name).toBe('Test');
  });
  
  test('has valid email', () => {
    expect(user.email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
  });
});
```

**Vitest (faster alternative):**
```javascript
// Installation
npm install --save-dev vitest

// Run tests
npx vitest                # All tests
npx vitest --ui           # UI mode
npx vitest --coverage     # Coverage
```

### E2E Testing

**Playwright:**
```python
# Installation
pip install playwright
playwright install        # Install browsers

# Test file
from playwright.sync_api import sync_playwright

def test_checkout_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Add to cart
        page.goto('https://shop.example.com')
        page.click('.product:first-child')
        page.click('button.add-to-cart')
        
        # Checkout
        page.click('.cart-button')
        page.click('button.checkout')
        
        # Fill shipping
        page.fill('input[name="address"]', '123 Main St')
        page.click('button.submit-order')
        
        # Verify
        page.wait_for_text('Order confirmed')
        
        browser.close()
```

**Cypress:**
```javascript
// Installation
npm install --save-dev cypress

// Test file
describe('Checkout Flow', () => {
  it('completes purchase', () => {
    cy.visit('https://shop.example.com')
    cy.get('.product:first-child').click()
    cy.get('button.add-to-cart').click()
    cy.get('.cart-button').click()
    cy.get('button.checkout').click()
    
    cy.get('input[name="address"]').type('123 Main St')
    cy.get('button.submit-order').click()
    
    cy.contains('Order confirmed')
  })
})
```

## Mocking & Stubbing

### When to Mock

- External APIs (payment, email, SMS)
- Database calls (use in-memory instead)
- File system operations
- Time-dependent code
- Random number generation
- Network calls

### Python Mocking

```python
from unittest.mock import Mock, patch, MagicMock
import pytest

# Simple mock
def test_send_email():
    mock_email_service = Mock()
    mock_email_service.send.return_value = True
    
    result = send_welcome_email(mock_email_service, 'user@example.com')
    
    mock_email_service.send.assert_called_once_with(
        to='user@example.com',
        subject='Welcome!'
    )
    assert result == True

# Patch decorator
@patch('app.services.payment_gateway.charge')
def test_payment_success(mock_charge):
    mock_charge.return_value = {'status': 'success'}
    
    result = process_payment(100.00)
    
    assert result['status'] == 'success'
    mock_charge.assert_called_once_with(100.00)

# Context manager
def test_time_dependent_code():
    with patch('app.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 1, 1)
        
        result = get_current_year()
        assert result == 2026
```

### JavaScript Mocking

```javascript
// Jest mocking
jest.mock('../services/paymentGateway');

test('processes payment', async () => {
  paymentGateway.charge.mockResolvedValue({ status: 'success' });
  
  const result = await processPayment(100.00);
  
  expect(paymentGateway.charge).toHaveBeenCalledWith(100.00);
  expect(result.status).toBe('success');
});

// Mock modules
jest.mock('axios');
import axios from 'axios';

test('fetches user data', async () => {
  axios.get.mockResolvedValue({ data: { id: 1, name: 'Test' } });
  
  const user = await fetchUser(1);
  
  expect(axios.get).toHaveBeenCalledWith('/users/1');
  expect(user.name).toBe('Test');
});
```

## CI/CD Testing

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### GitLab CI

```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Performance Testing

### Load Testing (Locust)

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def view_product(self):
        self.client.get('/products/1')
    
    @task(1)
    def add_to_cart(self):
        self.client.post('/cart/add', json={'product_id': 1})
    
    @task(1)
    def checkout(self):
        self.client.post('/checkout')
```

**Run:**
```bash
locust -f locustfile.py --host=https://app.example.com
# Open http://localhost:8089 for web UI
```

### Stress Testing

```python
import asyncio
import aiohttp
import time

async def stress_test(session, url, num_requests):
    start = time.time()
    
    tasks = [session.get(url) for _ in range(num_requests)]
    responses = await asyncio.gather(*tasks)
    
    end = time.time()
    rps = num_requests / (end - start)
    
    print(f"Requests/sec: {rps}")
    print(f"Success: {sum(1 for r in responses if r.status == 200)}")

async def main():
    async with aiohttp.ClientSession() as session:
        await stress_test(session, 'https://api.example.com/users', 1000)

asyncio.run(main())
```

## Security Testing

### OWASP Top 10 Testing

**1. Injection Testing:**
```python
def test_sql_injection():
    # Should NOT work
    response = client.post('/login', json={
        'username': "admin' OR '1'='1",
        'password': 'anything'
    })
    assert response.status_code == 401
```

**2. XSS Testing:**
```python
def test_xss_prevention():
    response = client.post('/comments', json={
        'text': '<script>alert("xss")</script>'
    })
    assert '<script>' not in response.text
```

**3. Authentication Testing:**
```python
def test_rate_limiting():
    for i in range(10):
        response = client.post('/login', json={
            'username': 'admin',
            'password': 'wrong'
        })
    
    # Should be rate limited
    assert response.status_code == 429
```

### Security Scanning Tools

**SAST (Static Analysis):**
```bash
# Python
pip install bandit
bandit -r app/

# JavaScript
npm install --save-dev eslint eslint-plugin-security
npx eslint --plugin security .
```

**DAST (Dynamic Analysis):**
```bash
# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://app.example.com
```

## Test Data Management

### Test Fixtures

```python
# conftest.py
import pytest
from app.models import User, Product
from app.database import SessionLocal

@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user(db_session):
    user = User(name='Test User', email='test@example.com')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_product(db_session):
    product = Product(name='Test Product', price=99.99)
    db_session.add(product)
    db_session.commit()
    return product
```

### Factory Pattern

```python
# factories.py
from factory import Factory, Sequence, Faker
from app.models import User

class UserFactory(Factory):
    class Meta:
        model = User
    
    name = Faker('name')
    email = Sequence(lambda n: f'user{n}@example.com')
    password = 'hashed_password_123'

# Usage
def test_user_creation():
    user = UserFactory()
    assert user.email.endswith('@example.com')
```

## Coverage Analysis

### Python Coverage

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# View HTML report
open htmlcov/index.html

# Coverage thresholds in pytest.ini
[tool:pytest]
addopts = --cov=app --cov-fail-under=80
```

### JavaScript Coverage

```bash
# Jest coverage
npm test -- --coverage

# View report
open coverage/lcov-report/index.html

# Coverage config in package.json
{
  "jest": {
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

## Bug Reporting

### Template

```markdown
## Bug Report

**Title:** [Brief description]

**Severity:** Critical / High / Medium / Low

**Environment:**
- OS: macOS 14.0
- Browser: Chrome 120.0.6099.109
- App Version: 2.3.1

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Screenshots:**
[Attach if applicable]

**Logs:**
```
[Error logs here]
```

**Additional Context:**
[Any other details]
```

## Quality Metrics

### Key Metrics

| Metric | Target | Formula |
|--------|--------|---------|
| **Code Coverage** | 80%+ | (Lines tested / Total lines) × 100 |
| **Test Pass Rate** | 95%+ | (Passed tests / Total tests) × 100 |
| **Bug Escape Rate** | <5% | (Bugs in prod / Total bugs) × 100 |
| **Mean Time to Detect** | <1 hour | Average time from bug introduction to detection |
| **Flaky Test Rate** | <1% | (Flaky tests / Total tests) × 100 |

### Dashboard Example

```
Test Suite Status:
├─ Unit Tests: 245 passed, 2 failed (99.2%)
├─ Integration Tests: 89 passed, 0 failed (100%)
└─ E2E Tests: 23 passed, 1 flaky (95.8%)

Coverage:
├─ Lines: 84.2%
├─ Branches: 79.5%
├─ Functions: 88.1%
└─ Statements: 83.9%

Performance:
├─ Average Test Time: 2.3s
├─ Slowest Test: test_checkout_flow (8.5s)
└─ Total Suite: 4m 32s
```

## Best Practices

1. **Test early, test often** - Run tests on every commit
2. **Keep tests fast** - Unit tests <10ms, integration <1s
3. **Test behavior, not implementation** - Tests shouldn't break on refactoring
4. **Use meaningful names** - `test_user_creation_with_valid_email()`
5. **One assertion per concept** - Multiple related assertions OK
6. **Arrange-Act-Assert pattern** - Clear test structure
7. **Avoid test interdependence** - Each test should be isolated
8. **Mock external dependencies** - Don't rely on external services
9. **Test edge cases** - Empty inputs, max values, null/undefined
10. **Keep tests maintainable** - Refactor tests like production code

## Resources

- **Books:** "Test-Driven Development", "Growing Object-Oriented Software"
- **Frameworks:** pytest, Jest, Playwright, Cypress
- **Tools:** Locust, OWASP ZAP, SonarQube
- **Coverage:** Coverage.py, Istanbul,Codecov

## Examples

**Input:** "Write tests for user registration"

**Output:**
```python
def test_register_with_valid_data():
    response = client.post('/register', json={
        'email': 'user@example.com',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 201
    assert 'user_id' in response.json()

def test_register_duplicate_email():
    client.post('/register', json={
        'email': 'existing@example.com',
        'password': 'Pass123!'
    })
    response = client.post('/register', json={
        'email': 'existing@example.com',
        'password': 'NewPass123!'
    })
    assert response.status_code == 409

def test_register_weak_password():
    response = client.post('/register', json={
        'email': 'user@example.com',
        'password': '123'
    })
    assert response.status_code == 400
```

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*  
*Status: Production Ready*
