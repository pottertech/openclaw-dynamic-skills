---
name: software-developer
description: Development best practices, coding patterns, debugging strategies, and professional workflows. Use when writing code, reviewing PRs, debugging issues, optimizing performance, or setting up development environments.
---

# Software Developer

Professional development practices, coding patterns, and workflows for building maintainable, high-quality software.

## When to Use

- Writing new code or features
- Reviewing pull requests
- Debugging issues
- Optimizing performance
- Refactoring legacy code
- Setting up development environments
- Learning new patterns or languages
- Code quality improvements

## Clean Code Principles

### SOLID Principles

**S - Single Responsibility Principle**
```python
# ❌ Bad: Multiple responsibilities
class UserService:
    def create_user(self, data):
        # Validate
        if not data['email']:
            raise ValueError('Email required')
        
        # Save to DB
        db.execute('INSERT INTO users...', data)
        
        # Send email
        smtp.send_email(data['email'], 'Welcome!')
        
        # Log activity
        logger.info(f'User created: {data["email"]}')

# ✅ Good: Single responsibility each
class UserValidator:
    def validate(self, data):
        if not data['email']:
            raise ValueError('Email required')

class UserRepository:
    def save(self, data):
        db.execute('INSERT INTO users...', data)

class EmailService:
    def send_welcome(self, email):
        smtp.send_email(email, 'Welcome!')

class UserService:
    def create_user(self, data):
        UserValidator().validate(data)
        UserRepository().save(data)
        EmailService().send_welcome(data['email'])
        logger.info(f'User created: {data["email"]}')
```

**O - Open/Closed Principle**
```python
# ❌ Bad: Closed for extension
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == 'credit_card':
            # Credit card logic
        elif payment_type == 'paypal':
            # PayPal logic
        elif payment_type == 'crypto':
            # Crypto logic

# ✅ Good: Open for extension
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass

class CreditCardPayment(PaymentMethod):
    def process(self, amount):
        # Credit card logic

class PayPalPayment(PaymentMethod):
    def process(self, amount):
        # PayPal logic

class PaymentProcessor:
    def process(self, method: PaymentMethod, amount):
        return method.process(amount)
```

**L - Liskov Substitution Principle**
```python
# ❌ Bad: Subclass breaks parent contract
class Bird:
    def fly(self):
        pass

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")

# ✅ Good: Proper abstraction
class Bird:
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        # Fly

class SwimmingBird(Bird):
    def move(self):
        # Swim
```

**I - Interface Segregation Principle**
```python
# ❌ Bad: Fat interface
class Worker:
    def work(self): pass
    def eat(self): pass
    def sleep(self): pass

class Robot(Worker):
    def work(self): pass
    def eat(self):
        raise NotImplementedError()  # Robots don't eat!
    def sleep(self):
        raise NotImplementedError()

# ✅ Good: Segregated interfaces
class Workable:
    def work(self): pass

class Eatable:
    def eat(self): pass

class HumanWorker(Workable, Eatable):
    def work(self): pass
    def eat(self): pass

class RobotWorker(Workable):
    def work(self): pass
```

**D - Dependency Inversion Principle**
```python
# ❌ Bad: High-level depends on low-level
class MySQLDatabase:
    def connect(self): pass
    def query(self, sql): pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Hard dependency

# ✅ Good: Depend on abstractions
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self): pass
    
    @abstractmethod
    def query(self, sql): pass

class MySQLDatabase(Database):
    def connect(self): pass
    def query(self, sql): pass

class UserService:
    def __init__(self, db: Database):
        self.db = db  # Depends on abstraction
```

### DRY (Don't Repeat Yourself)

```python
# ❌ Bad: Repeated logic
def calculate_employee_tax(salary):
    if salary < 50000:
        return salary * 0.1
    elif salary < 100000:
        return salary * 0.2
    else:
        return salary * 0.3

def calculate_contractor_tax(income):
    if income < 50000:
        return income * 0.1
    elif income < 100000:
        return income * 0.2
    else:
        return income * 0.3

# ✅ Good: Extracted logic
def calculate_tax(income):
    if income < 50000:
        return income * 0.1
    elif income < 100000:
        return income * 0.2
    else:
        return income * 0.3

def calculate_employee_tax(salary):
    return calculate_tax(salary)

def calculate_contractor_tax(income):
    return calculate_tax(income)
```

### KISS (Keep It Simple, Stupid)

```python
# ❌ Bad: Over-engineered
def process_data(items):
    result = list(
        map(
            lambda x: x['value'] * 2,
            filter(
                lambda x: x['active'] and x['value'] > 0,
                sorted(
                    items,
                    key=lambda x: x['timestamp'],
                    reverse=True
                )
            )
        )
    )
    return result

# ✅ Good: Simple and clear
def process_data(items):
    # Sort by timestamp (newest first)
    sorted_items = sorted(items, key=lambda x: x['timestamp'], reverse=True)
    
    # Filter active items with positive values
    filtered = [item for item in sorted_items if item['active'] and item['value'] > 0]
    
    # Double the values
    return [item['value'] * 2 for item in filtered]
```

## Code Review Checklist

### Functionality
- [ ] Code does what it's supposed to do
- [ ] Edge cases handled (null, empty, max values)
- [ ] Error handling appropriate
- [ ] No logic errors or bugs
- [ ] Tests included and passing

### Code Quality
- [ ] Follows style guide
- [ ] Clear variable/function names
- [ ] No code duplication (DRY)
- [ ] Functions are small and focused
- [ ] Comments explain "why", not "what"

### Architecture
- [ ] Follows existing patterns
- [ ] Proper separation of concerns
- [ ] No circular dependencies
- [ ] Database queries optimized
- [ ] API design consistent

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] XSS prevention in place
- [ ] Authentication/authorization checked

### Performance
- [ ] No unnecessary loops
- [ ] Database indexes used
- [ ] Caching where appropriate
- [ ] No memory leaks
- [ ] Async where beneficial

### Maintainability
- [ ] Code is testable
- [ ] Logging added
- [ ] Documentation updated
- [ ] No dead code
- [ ] Configuration externalized

## Git Workflows

### Feature Branch Workflow

```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/user-authentication

# Work on feature
git add .
git commit -m "feat: add user login endpoint"

git add .
git commit -m "feat: add password hashing"

# Keep up to date with main
git fetch origin
git rebase origin/main

# Push and create PR
git push -u origin feature/user-authentication
# Then create PR on GitHub/GitLab
```

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build/config changes

**Examples:**
```bash
feat(auth): add user login endpoint

Implemented POST /api/auth/login with JWT token generation.
Includes rate limiting and account lockout after 5 failed attempts.

Closes #123

---

fix(database): resolve connection pool leak

Fixed issue where database connections weren't being returned
to the pool after query timeout.

Fixes #456
```

### Rebasing vs Merging

**Rebase (cleaner history):**
```bash
git checkout feature-branch
git rebase main
# Resolve conflicts if any
git rebase --continue
```

**Merge (preserves history):**
```bash
git checkout main
git merge feature-branch
```

### Cherry-Picking

```bash
# Apply specific commit from another branch
git cherry-pick abc123

# Apply multiple commits
git cherry-pick abc123^..abc123

# Apply without committing (for modifications)
git cherry-pick -n abc123
```

## Debugging Strategies

### Systematic Approach

**1. Reproduce the Issue**
- Get exact steps to reproduce
- Note environment (OS, version, config)
- Identify triggers and patterns

**2. Isolate the Problem**
- Narrow down to specific component
- Use binary search (comment out half the code)
- Check recent changes

**3. Gather Information**
- Check logs
- Add debug logging
- Use debugger
- Inspect state

**4. Form Hypothesis**
- What could cause this?
- What changed recently?
- What's different from expected?

**5. Test Hypothesis**
- Make targeted change
- Verify fix
- Check for side effects

### Python Debugging

```python
# Print debugging
def process_data(data):
    print(f"Input: {data}")  # Quick debug
    result = transform(data)
    print(f"Output: {result}")
    return result

# Logging (better than print)
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processing {len(data)} items")
    result = transform(data)
    logger.info(f"Processed successfully")
    return result

# Debugger
import pdb

def problematic_function(x, y):
    pdb.set_trace()  # Breakpoint
    result = x / y
    return result

# Run: python script.py
# Commands: n (next), s (step), c (continue), q (quit)

# Modern: breakpoint() (Python 3.7+)
def another_function(data):
    breakpoint()  # Built-in debugger
    return process(data)
```

### JavaScript Debugging

```javascript
// Console debugging
console.log('Value:', value);
console.error('Error:', error);
console.trace('Stack trace');

// Debugger statement
function problematicFunction(x, y) {
  debugger;  // Breakpoint
  return x / y;
}

// Chrome DevTools
// - Set breakpoints in Sources tab
// - Watch expressions
// - Call stack inspection
// - Network tab for API calls
```

### Common Debugging Tools

**Python:**
```bash
# pdb (built-in)
python -m pdb script.py

# ipdb (better interface)
pip install ipdb
python -m ipdb script.py

# pdb++ (enhanced)
pip install pdbpp
python -m pdb script.py

# Remote debugging
pip install remote-pdb
# Set breakpoint, connect via telnet
```

**JavaScript:**
```bash
# Node.js inspector
node --inspect script.js
# Open chrome://inspect in Chrome

# Debug package
npm install debug
DEBUG=myapp:* node app.js
```

## Performance Optimization

### Identify Bottlenecks

**Profiling:**
```python
# cProfile (built-in)
import cProfile
import pstats

def slow_function():
    # ... code ...

profiler = cProfile.Profile()
profiler.enable()
slow_function()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)

# Line profiler (per-line timing)
pip install line_profiler
kernprof -l -v script.py

# Memory profiler
pip install memory_profiler
python -m memory_profiler script.py
```

### Common Optimizations

**1. Algorithmic Improvements**
```python
# ❌ O(n²) - Nested loops
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# ✅ O(n) - Use set
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
```

**2. Caching**
```python
from functools import lru_cache

# ❌ Recalculates every time
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# ✅ Memoized
@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**3. Database Optimization**
```python
# ❌ N+1 query problem
users = db.query(User).all()
for user in users:
    posts = db.query(Post).filter_by(user_id=user.id).all()
    # Executes 1 + N queries!

# ✅ Eager loading
users = db.query(User).options(joinedload(User.posts)).all()
# Executes 1 query with JOIN
```

**4. Async Operations**
```python
# ❌ Sequential (slow)
import requests

def fetch_all(urls):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.text)
    return results

# ✅ Concurrent (fast)
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.text() for r in responses]
```

## Refactoring Techniques

### Extract Method

```python
# Before
def process_order(order):
    # Validate order
    if not order.items:
        raise ValueError('Empty order')
    if order.total <= 0:
        raise ValueError('Invalid total')
    
    # Calculate tax
    tax_rate = 0.08
    tax = order.total * tax_rate
    
    # Calculate shipping
    if order.total > 100:
        shipping = 0
    else:
        shipping = 10
    
    # Final total
    final = order.total + tax + shipping
    
    return final

# After
def process_order(order):
    validate_order(order)
    tax = calculate_tax(order.total)
    shipping = calculate_shipping(order.total)
    return order.total + tax + shipping

def validate_order(order):
    if not order.items:
        raise ValueError('Empty order')
    if order.total <= 0:
        raise ValueError('Invalid total')

def calculate_tax(amount):
    return amount * 0.08

def calculate_shipping(amount):
    return 0 if amount > 100 else 10
```

### Replace Conditional with Polymorphism

```python
# Before
class Bird:
    def get_speed(self, wind_speed):
        if self.type == 'eagle':
            return 50 + wind_speed * 0.5
        elif self.type == 'penguin':
            return 0  # Can't fly
        elif self.type == 'sparrow':
            return 20 + wind_speed * 0.3

# After
class Bird(ABC):
    @abstractmethod
    def get_speed(self, wind_speed):
        pass

class Eagle(Bird):
    def get_speed(self, wind_speed):
        return 50 + wind_speed * 0.5

class Penguin(Bird):
    def get_speed(self, wind_speed):
        return 0

class Sparrow(Bird):
    def get_speed(self, wind_speed):
        return 20 + wind_speed * 0.3
```

## Design Patterns

### Factory Pattern

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount):
        pass

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount):
        print(f"Processing ${amount} via credit card")

class PayPalProcessor(PaymentProcessor):
    def process(self, amount):
        print(f"Processing ${amount} via PayPal")

class PaymentFactory:
    @staticmethod
    def create_processor(payment_type):
        if payment_type == 'credit_card':
            return CreditCardProcessor()
        elif payment_type == 'paypal':
            return PayPalProcessor()
        else:
            raise ValueError(f'Unknown payment type: {payment_type}')

# Usage
processor = PaymentFactory.create_processor('credit_card')
processor.process(100.00)
```

### Singleton Pattern

```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = cls._create_connection()
        return cls._instance
    
    @classmethod
    def _create_connection(cls):
        # Create database connection
        return "DB_CONNECTION"

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # Same instance
```

### Observer Pattern

```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, data):
        for observer in self._observers:
            observer.update(data)

class Observer:
    def update(self, data):
        print(f"Received: {data}")

# Usage
subject = Subject()
observer1 = Observer()
observer2 = Observer()

subject.attach(observer1)
subject.attach(observer2)
subject.notify("Hello observers!")
```

## API Development

### REST Best Practices

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# GET - List resources
@app.route('/api/users', methods=['GET'])
def list_users():
    users = db.query(User).all()
    return jsonify([user.to_dict() for user in users])

# GET - Single resource
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(user.to_dict())

# POST - Create resource
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Validate
    if not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    user = User(**data)
    db.add(user)
    db.commit()
    
    return jsonify(user.to_dict()), 201

# PUT - Update resource
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = db.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    
    data = request.get_json()
    for key, value in data.items():
        setattr(user, key, value)
    
    db.commit()
    return jsonify(user.to_dict())

# DELETE - Remove resource
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    
    db.delete(user)
    db.commit()
    return '', 204
```

### Error Handling

```python
from functools import wraps

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except NotFoundError as e:
            return jsonify({'error': 'Not found'}), 404
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper

@app.route('/api/users/<int:user_id>')
@handle_errors
def get_user(user_id):
    user = db.query(User).get(user_id)
    if not user:
        raise NotFoundError()
    return jsonify(user.to_dict())
```

## Logging & Monitoring

### Logging Best Practices

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log levels
logger.debug('Detailed information for debugging')
logger.info('General information about operation')
logger.warning('Something unexpected happened')
logger.error('Serious problem, some function failed')
logger.critical('Very serious error, program may not continue')

# Structured logging
import json

def log_event(event_type, **kwargs):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event': event_type,
        **kwargs
    }
    logger.info(json.dumps(log_entry))

# Usage
log_event('user_login', user_id=123, ip='192.168.1.1')
```

### Monitoring Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Instrument code
@app.route('/api/users')
@REQUEST_LATENCY.time()
def get_users():
    try:
        users = db.query(User).all()
        REQUEST_COUNT.labels(method='GET', endpoint='/api/users', status=200).inc()
        return jsonify([u.to_dict() for u in users])
    except Exception as e:
        REQUEST_COUNT.labels(method='GET', endpoint='/api/users', status=500).inc()
        raise

# Start metrics server
start_http_server(8000)
```

## Best Practices

1. **Write readable code** - Code is read more than written
2. **Use version control** - Commit often, write good messages
3. **Test your code** - Unit tests, integration tests
4. **Document as you go** - Comments, README, API docs
5. **Keep functions small** - One responsibility, <50 lines
6. **Name things well** - Clear, descriptive names
7. **Handle errors gracefully** - Don't swallow exceptions
8. **Log appropriately** - Enough to debug, not too much
9. **Security first** - Validate input, sanitize output
10. **Performance matters** - Profile before optimizing

## Resources

- **Books:** "Clean Code", "The Pragmatic Programmer", "Refactoring"
- **Patterns:** "Design Patterns" (Gang of Four)
- **Tools:** Git, Docker, Kubernetes, VS Code
- **Practice:** LeetCode, Exercism, Codewars

## Examples

**Input:** "Review this code for issues"

```python
def get_data(id):
    conn = create_connection()
    result = conn.query(f"SELECT * FROM table WHERE id={id}")
    return result
```

**Output:**
```
Issues found:
1. ❌ SQL injection vulnerability - Use parameterized queries
2. ❌ Connection not closed - Use context manager
3. ❌ No error handling - Add try/except
4. ❌ No input validation - Validate id parameter
5. ❌ Hardcoded table name - Use configuration

Fixed version:
```python
def get_data(id):
    if not isinstance(id, int) or id <= 0:
        raise ValueError('Invalid ID')
    
    try:
        with create_connection() as conn:
            result = conn.query(
                'SELECT * FROM table WHERE id=%s',
                (id,)
            )
            return result
    except DatabaseError as e:
        logger.error(f'Database error: {e}')
        raise
```
```

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*  
*Status: Production Ready*
