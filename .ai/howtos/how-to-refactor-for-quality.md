# How to: Refactor for Quality (Complexity + SRP)

**Purpose**: Architectural refactoring guide for resolving complexity and SRP violations together

**Scope**: Holistic approach to fixing cyclomatic complexity (Radon, Xenon) and Single Responsibility Principle violations using architecture-first analysis

**Overview**: This guide addresses the tension between complexity and SRP violations through holistic refactoring
    rather than sequential fixing. Covers analyzing why code is complex (too many responsibilities vs just verbose),
    choosing appropriate refactoring strategies (extract methods vs classes vs modules), and iteratively refactoring
    with both constraints in mind. Includes decision trees, before/after examples, anti-patterns to avoid, and
    validation workflows. Prerequisite: Complete basic linting fixes first (see how-to-fix-linting-errors.md).

**Dependencies**: make lint-complexity, make lint-solid, poetry, radon, xenon, thai-lint srp

**Exports**: Well-architected code with A-grade complexity and no SRP violations

**Related**: how-to-fix-linting-errors.md, AGENTS.md (Quality Gates section)

**Implementation**: Architecture-first analysis followed by iterative refactoring with dual constraint validation

---

## Overview

Complexity and SRP violations are **architectural issues**, not mechanical fixes. They require understanding why code is structured the way it is and making thoughtful refactoring decisions.

**The Problem**: Sequential fixing creates a back-and-forth cycle:
- Fix complexity by extracting methods → Creates SRP violations (too many methods in one class)
- Fix SRP by splitting classes → Creates complexity elsewhere (more integration code)
- Repeat endlessly without improvement

**The Solution**: Holistic refactoring
- Analyze complexity and SRP violations together
- Understand the root cause (multi-responsibility vs verbosity)
- Choose refactoring strategy based on the cause
- Refactor with both constraints in mind
- Validate both constraints after each change

---

## Prerequisites

Before starting architectural refactoring:

✅ **Complete basic linting first**: See `.ai/howtos/how-to-fix-linting-errors.md`

Ensure:
- `make lint` passes (Ruff, Flake8)
- `make lint-security` passes (Bandit, pip-audit)
- MyPy type checking passes
- Pylint score is 10.00/10
- All tests pass

**Why**: Architectural refactoring is complex. Don't complicate it with style issues, security problems, or type errors.

---

## The Back-and-Forth Problem

### Why Sequential Fixing Fails

**Example: Sequential approach**

```python
# Step 1: Complex function (B-grade complexity)
def process_order(order_data: dict) -> dict:
    """Process customer order."""
    # 10 lines: Validate order data
    if not order_data.get("customer_id"):
        raise ValueError("Missing customer_id")
    if not order_data.get("items"):
        raise ValueError("Missing items")
    # ... more validation

    # 10 lines: Calculate totals
    subtotal = 0
    for item in order_data["items"]:
        subtotal += item["price"] * item["quantity"]
    tax = subtotal * 0.08
    total = subtotal + tax

    # 10 lines: Update inventory
    for item in order_data["items"]:
        inventory[item["id"]] -= item["quantity"]
        if inventory[item["id"]] < 0:
            raise ValueError(f"Insufficient inventory for {item['id']}")

    # Result: 30+ lines, B-grade complexity
    return {"total": total, "status": "processed"}
```

**Attempt 1: Fix complexity by extracting methods**

```python
class OrderProcessor:
    """Process customer orders."""

    def process_order(self, order_data: dict) -> dict:
        """Process customer order."""
        self._validate_order(order_data)
        total = self._calculate_total(order_data)
        self._update_inventory(order_data)
        return {"total": total, "status": "processed"}

    def _validate_order(self, order_data: dict) -> None:
        """Validate order data."""
        # Validation logic

    def _calculate_total(self, order_data: dict) -> float:
        """Calculate order total."""
        # Calculation logic

    def _update_inventory(self, order_data: dict) -> None:
        """Update inventory levels."""
        # Inventory logic

# ✅ Complexity: A-grade (small methods)
# ❌ SRP: This class does THREE things (validate, calculate, update inventory)
```

**Attempt 2: Fix SRP by splitting classes**

```python
class OrderValidator:
    """Validate order data."""
    def validate(self, order_data: dict) -> None:
        # Validation logic

class OrderCalculator:
    """Calculate order totals."""
    def calculate_total(self, order_data: dict) -> float:
        # Calculation logic

class InventoryUpdater:
    """Update inventory levels."""
    def update(self, order_data: dict) -> None:
        # Inventory logic

class OrderProcessor:
    """Coordinate order processing."""
    def __init__(self):
        self.validator = OrderValidator()
        self.calculator = OrderCalculator()
        self.inventory = InventoryUpdater()

    def process(self, order_data: dict) -> dict:
        """Process order."""
        self.validator.validate(order_data)
        total = self.calculator.calculate_total(order_data)
        self.inventory.update(order_data)
        return {"total": total, "status": "processed"}

# ✅ SRP: Each class has one responsibility
# ❌ Complexity: OrderProcessor.__init__ now complex (dependency injection)
# ❌ More lines of code overall
# ❌ More files to maintain
```

**The Cycle**: You're bouncing between fixing complexity (extract methods) and fixing SRP (split classes) without making real progress.

### The Holistic Approach

**Ask first: WHY is the code complex?**

1. **Is it doing multiple things?** → SRP violation causing complexity
   - Example: OrderProcessor validates AND calculates AND updates inventory
   - Fix: Split into focused classes (fixes both)

2. **Is it just verbose?** → Not an SRP violation, just needs extraction
   - Example: Single responsibility but long/repetitive code
   - Fix: Extract helper methods in the same class

3. **Is it inherently complex logic?** → Actual domain complexity
   - Example: Complex business rules, state machines
   - Fix: Simplify algorithm or accept B-grade in exceptional cases

---

## The Architecture-First Analysis

Before making any changes, analyze the code holistically.

### Step 1: Identify Violations

```bash
# Run complexity analysis
make lint-complexity

# Look for:
# - Radon: Average complexity score
# - Xenon: Functions/classes with B-grade or worse
# - Nesting linter: Deep nesting violations

# Run SRP analysis
make lint-solid

# Look for:
# - Classes with multiple responsibilities
# - Classes with too many public methods
# - Classes with unrelated method groups
```

### Step 2: Analyze Root Cause

For each violation, ask:

**Complexity Questions**:
- Why is this function/class complex?
- Is it doing multiple things? (SRP violation)
- Is it just verbose but focused?
- Does it have deep nesting?
- Does it have many branches (if/elif/else)?

**SRP Questions**:
- What is this class's single responsibility?
- Can I describe it in one sentence without "and"?
- Are there distinct groups of methods?
- Would splitting this improve or complicate the codebase?

### Step 3: Choose Refactoring Strategy

Use this decision tree:

```
Is the code complex?
├─ YES: Why is it complex?
│  ├─ Doing multiple things (SRP violation)
│  │  └─ Strategy: Extract separate classes (fixes both complexity + SRP)
│  │
│  ├─ Just verbose/repetitive
│  │  └─ Strategy: Extract helper methods (same class, fixes complexity only)
│  │
│  ├─ Deep nesting
│  │  └─ Strategy: Early returns + guard clauses (fixes complexity)
│  │
│  └─ Inherent domain complexity
│     └─ Strategy: Simplify algorithm or document justification
│
└─ NO: Is there an SRP violation?
   ├─ YES: Is the class also growing large?
   │  ├─ YES → Strategy: Split into focused classes
   │  └─ NO → Strategy: Move methods to appropriate classes
   │
   └─ NO: Code is clean, no refactoring needed
```

---

## Refactoring Strategies

### Strategy 1: Extract Helper Methods (Same Class)

**When**: Code is verbose/repetitive but has a single responsibility

**Before**:
```python
class ReportGenerator:
    """Generate customer reports."""

    def generate_report(self, customer_id: str) -> dict:
        """Generate complete customer report."""
        # 15 lines: Fetch customer data
        customer = db.query("SELECT * FROM customers WHERE id = ?", (customer_id,))
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        customer_data = {
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "address": customer[4],
        }

        # 15 lines: Fetch order history
        orders = db.query("SELECT * FROM orders WHERE customer_id = ?", (customer_id,))
        order_data = []
        for order in orders:
            order_data.append({
                "id": order[0],
                "date": order[1],
                "total": order[2],
                "status": order[3],
            })

        # 10 lines: Calculate metrics
        total_spent = sum(o["total"] for o in order_data)
        order_count = len(order_data)
        avg_order = total_spent / order_count if order_count > 0 else 0

        return {
            "customer": customer_data,
            "orders": order_data,
            "metrics": {
                "total_spent": total_spent,
                "order_count": order_count,
                "avg_order": avg_order,
            }
        }

# Issues:
# - 40+ lines (B-grade complexity)
# - But single responsibility: "Generate customer reports"
# - Not an SRP violation, just verbose
```

**After**:
```python
class ReportGenerator:
    """Generate customer reports."""

    def generate_report(self, customer_id: str) -> dict:
        """Generate complete customer report.

        Args:
            customer_id: ID of customer to report on

        Returns:
            Complete customer report with orders and metrics
        """
        customer_data = self._fetch_customer_data(customer_id)
        order_data = self._fetch_order_history(customer_id)
        metrics = self._calculate_metrics(order_data)

        return {
            "customer": customer_data,
            "orders": order_data,
            "metrics": metrics,
        }

    def _fetch_customer_data(self, customer_id: str) -> dict:
        """Fetch customer data from database.

        Args:
            customer_id: ID of customer

        Returns:
            Customer data dictionary

        Raises:
            ValueError: If customer not found
        """
        customer = db.query(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,)
        )
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        return {
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "address": customer[4],
        }

    def _fetch_order_history(self, customer_id: str) -> list[dict]:
        """Fetch order history for customer.

        Args:
            customer_id: ID of customer

        Returns:
            List of order dictionaries
        """
        orders = db.query(
            "SELECT * FROM orders WHERE customer_id = ?",
            (customer_id,)
        )

        return [
            {
                "id": order[0],
                "date": order[1],
                "total": order[2],
                "status": order[3],
            }
            for order in orders
        ]

    def _calculate_metrics(self, orders: list[dict]) -> dict:
        """Calculate customer metrics from orders.

        Args:
            orders: List of order dictionaries

        Returns:
            Metrics dictionary
        """
        total_spent = sum(o["total"] for o in orders)
        order_count = len(orders)
        avg_order = total_spent / order_count if order_count > 0 else 0

        return {
            "total_spent": total_spent,
            "order_count": order_count,
            "avg_order": avg_order,
        }

# Results:
# ✅ Complexity: A-grade (all methods < 10 lines)
# ✅ SRP: Still single responsibility (generate reports)
# ✅ Readability: Clear method names show what's happening
# ✅ Testability: Can test each part independently
```

### Strategy 2: Extract Separate Classes (Multi-Responsibility)

**When**: Code does multiple distinct things (SRP violation causing complexity)

**Before**:
```python
class UserManager:
    """Manage user accounts."""

    def create_user(self, email: str, password: str) -> dict:
        """Create new user account."""
        # Validate email format
        if "@" not in email:
            raise ValueError("Invalid email")

        # Hash password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Save to database
        user_id = db.insert("users", {
            "email": email,
            "password_hash": password_hash,
        })

        # Send welcome email
        email_body = f"Welcome {email}!"
        smtp.send(email, "Welcome", email_body)

        # Log creation
        logger.info(f"User created: {user_id}")

        return {"id": user_id, "email": email}

# Issues:
# - Does FIVE things: validate, hash, save, email, log
# - SRP violation causing complexity
# - Hard to test (mocking smtp, db, logger)
```

**After**:
```python
class EmailValidator:
    """Validate email addresses."""

    def validate(self, email: str) -> None:
        """Validate email format.

        Args:
            email: Email address to validate

        Raises:
            ValueError: If email format is invalid
        """
        if "@" not in email:
            raise ValueError("Invalid email")


class PasswordHasher:
    """Hash and verify passwords securely."""

    def hash_password(self, password: str) -> str:
        """Hash password using SHA256.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()


class UserRepository:
    """Database operations for users."""

    def save_user(self, email: str, password_hash: str) -> str:
        """Save user to database.

        Args:
            email: User email
            password_hash: Hashed password

        Returns:
            User ID
        """
        return db.insert("users", {
            "email": email,
            "password_hash": password_hash,
        })


class WelcomeEmailSender:
    """Send welcome emails to new users."""

    def send_welcome(self, email: str) -> None:
        """Send welcome email.

        Args:
            email: User email address
        """
        email_body = f"Welcome {email}!"
        smtp.send(email, "Welcome", email_body)


class UserManager:
    """Coordinate user account creation."""

    def __init__(
        self,
        validator: EmailValidator,
        hasher: PasswordHasher,
        repository: UserRepository,
        email_sender: WelcomeEmailSender,
    ):
        """Initialize user manager.

        Args:
            validator: Email validation service
            hasher: Password hashing service
            repository: User data repository
            email_sender: Welcome email service
        """
        self.validator = validator
        self.hasher = hasher
        self.repository = repository
        self.email_sender = email_sender

    def create_user(self, email: str, password: str) -> dict:
        """Create new user account.

        Args:
            email: User email
            password: User password

        Returns:
            User data dictionary

        Raises:
            ValueError: If email is invalid
        """
        self.validator.validate(email)
        password_hash = self.hasher.hash_password(password)
        user_id = self.repository.save_user(email, password_hash)
        self.email_sender.send_welcome(email)

        logger.info(f"User created: {user_id}")

        return {"id": user_id, "email": email}

# Results:
# ✅ Complexity: A-grade (all methods simple)
# ✅ SRP: Each class has ONE responsibility
# ✅ Testability: Easy to mock dependencies
# ✅ Reusability: Can use EmailValidator, PasswordHasher elsewhere
```

### Strategy 3: Reduce Nesting with Guard Clauses

**When**: Deep nesting causing complexity

**Before**:
```python
def process_payment(payment: dict) -> dict:
    """Process customer payment."""
    if payment:
        if payment.get("amount"):
            if payment["amount"] > 0:
                if payment.get("customer_id"):
                    customer = get_customer(payment["customer_id"])
                    if customer:
                        if customer.get("is_active"):
                            # Actually process payment
                            result = charge_card(payment)
                            return {"status": "success", "result": result}
                        else:
                            return {"status": "error", "message": "Inactive customer"}
                    else:
                        return {"status": "error", "message": "Customer not found"}
                else:
                    return {"status": "error", "message": "Missing customer_id"}
            else:
                return {"status": "error", "message": "Invalid amount"}
        else:
            return {"status": "error", "message": "Missing amount"}
    else:
        return {"status": "error", "message": "Missing payment data"}

# Issues:
# - 7 levels of nesting
# - Cyclomatic complexity: B-grade
# - Hard to read and understand
```

**After**:
```python
def process_payment(payment: dict) -> dict:
    """Process customer payment.

    Args:
        payment: Payment data dictionary

    Returns:
        Payment result dictionary
    """
    # Guard clauses - fail fast
    if not payment:
        return {"status": "error", "message": "Missing payment data"}

    if not payment.get("amount"):
        return {"status": "error", "message": "Missing amount"}

    if payment["amount"] <= 0:
        return {"status": "error", "message": "Invalid amount"}

    if not payment.get("customer_id"):
        return {"status": "error", "message": "Missing customer_id"}

    customer = get_customer(payment["customer_id"])
    if not customer:
        return {"status": "error", "message": "Customer not found"}

    if not customer.get("is_active"):
        return {"status": "error", "message": "Inactive customer"}

    # Happy path - no nesting
    result = charge_card(payment)
    return {"status": "success", "result": result}

# Results:
# ✅ Complexity: A-grade (no nesting)
# ✅ Readability: Clear validation flow
# ✅ Maintainability: Easy to add more validations
```

### Strategy 4: Extract to Module Level

**When**: Classes are growing large and have distinct functional areas

**Before**:
```python
# src/services/user_service.py
class UserService:
    """Handle all user-related operations."""

    def create_user(self, data): pass
    def update_user(self, id, data): pass
    def delete_user(self, id): pass
    def authenticate_user(self, email, password): pass
    def reset_password(self, email): pass
    def send_verification_email(self, user_id): pass
    def verify_email(self, token): pass
    def get_user_profile(self, user_id): pass
    def update_user_profile(self, user_id, data): pass
    def get_user_settings(self, user_id): pass
    def update_user_settings(self, user_id, data): pass

# Issues:
# - 11 public methods (SRP violation)
# - Three distinct areas: CRUD, auth, profile
# - 200+ lines in one class
```

**After**:
```python
# src/services/user_crud.py
class UserCRUD:
    """Basic user CRUD operations."""

    def create(self, data: dict) -> dict:
        """Create user."""
        pass

    def update(self, user_id: str, data: dict) -> dict:
        """Update user."""
        pass

    def delete(self, user_id: str) -> None:
        """Delete user."""
        pass


# src/services/user_auth.py
class UserAuthentication:
    """User authentication operations."""

    def authenticate(self, email: str, password: str) -> dict:
        """Authenticate user."""
        pass

    def reset_password(self, email: str) -> None:
        """Reset password."""
        pass

    def send_verification_email(self, user_id: str) -> None:
        """Send verification email."""
        pass

    def verify_email(self, token: str) -> bool:
        """Verify email token."""
        pass


# src/services/user_profile.py
class UserProfile:
    """User profile and settings operations."""

    def get_profile(self, user_id: str) -> dict:
        """Get user profile."""
        pass

    def update_profile(self, user_id: str, data: dict) -> dict:
        """Update user profile."""
        pass

    def get_settings(self, user_id: str) -> dict:
        """Get user settings."""
        pass

    def update_settings(self, user_id: str, data: dict) -> dict:
        """Update user settings."""
        pass


# Results:
# ✅ SRP: Each class has one responsibility
# ✅ Organization: Related functionality grouped
# ✅ Maintainability: Easier to find and modify code
# ✅ File size: Smaller, focused files
```

---

## The Iterative Refactoring Process

### Step 1: Analyze Together

```bash
# Run both checks
make lint-complexity
make lint-solid

# Review output and note:
# - Which files have violations in BOTH?
# - Which have only complexity issues?
# - Which have only SRP issues?
```

### Step 2: Prioritize Violations

Focus on files with both complexity AND SRP issues first - these give the biggest improvement.

```
Priority 1: Both complexity + SRP violations
  → These are doing too many things
  → Extract separate classes (Strategy 2)

Priority 2: Only complexity violations
  → Analyze: Multi-responsibility or just verbose?
  → If verbose: Extract helper methods (Strategy 1)
  → If nested: Use guard clauses (Strategy 3)

Priority 3: Only SRP violations
  → Move methods to appropriate classes
  → Or split if class is large (Strategy 4)
```

### Step 3: Refactor One File at a Time

```bash
# Pick one file
# Analyze root cause (see decision tree above)
# Choose strategy
# Refactor

# Validate BOTH constraints
make lint-complexity
make lint-solid
make test

# If all pass, move to next file
# If not, adjust refactoring
```

### Step 4: Repeat Until Clean

```bash
# Keep refactoring until:
make lint-complexity  # All A-grade
make lint-solid       # No violations
make test            # All pass

# Then run full validation
make lint-full
make test
```

---

## Complexity Analysis Deep Dive

### Understanding Xenon Grading

Xenon grades complexity using letter grades:

- **A**: Cyclomatic complexity 1-5 (simple, maintainable)
- **B**: Cyclomatic complexity 6-10 (moderate, acceptable in some codebases)
- **C**: Cyclomatic complexity 11-20 (complex, needs refactoring)
- **D**: Cyclomatic complexity 21-30 (very complex, hard to maintain)
- **F**: Cyclomatic complexity 31+ (extremely complex, unmaintainable)

**This project requires A-grade for ALL code** (see Makefile line 146):
```bash
xenon --max-absolute A --max-modules A --max-average A
```

### What Increases Complexity?

Each of these adds +1 to cyclomatic complexity:
- `if` statement
- `elif` branch
- `else` branch
- `for` loop
- `while` loop
- `and` in condition
- `or` in condition
- `except` clause
- `with` statement (sometimes)

**Example**:
```python
def calculate_discount(customer, order):  # Complexity = 1 (base)
    if customer.is_vip:                   # +1 = 2
        if order.total > 100:             # +1 = 3
            return 0.20
        else:                             # +1 = 4
            return 0.10
    elif customer.is_member:              # +1 = 5
        return 0.05
    else:                                 # +1 = 6
        return 0.0

# Cyclomatic complexity: 6 (B-grade)
```

### Reducing Complexity

**Technique 1: Extract functions**
```python
def calculate_discount(customer, order):  # Complexity = 3
    if customer.is_vip:                   # +1 = 2
        return _vip_discount(order)
    elif customer.is_member:              # +1 = 3
        return 0.05
    else:
        return 0.0

def _vip_discount(order):                 # Complexity = 2
    if order.total > 100:                 # +1 = 2
        return 0.20
    return 0.10

# Main function: 3 (A-grade)
# Helper function: 2 (A-grade)
```

**Technique 2: Use dictionaries instead of if/elif chains**
```python
# Before: Complexity = 5
def get_status_message(status_code):
    if status_code == 200:
        return "OK"
    elif status_code == 404:
        return "Not Found"
    elif status_code == 500:
        return "Server Error"
    else:
        return "Unknown"

# After: Complexity = 1
def get_status_message(status_code):
    """Get HTTP status message."""
    messages = {
        200: "OK",
        404: "Not Found",
        500: "Server Error",
    }
    return messages.get(status_code, "Unknown")
```

**Technique 3: Early returns (guard clauses)**
```python
# Before: Complexity = 4
def process(data):
    if data:
        if data.is_valid():
            if data.is_ready():
                return data.process()
    return None

# After: Complexity = 3
def process(data):
    """Process data if valid and ready."""
    if not data:
        return None
    if not data.is_valid():
        return None
    if not data.is_ready():
        return None
    return data.process()
```

---

## SRP Analysis Deep Dive

### What is Single Responsibility?

A class should have **one reason to change**.

**Good SRP**:
```python
class EmailSender:
    """Send emails via SMTP."""
    # Reason to change: Email sending protocol changes
    pass

class UserRepository:
    """Store and retrieve users from database."""
    # Reason to change: Database schema changes
    pass
```

**Bad SRP**:
```python
class UserManager:
    """Manage users."""
    def create_user(self): pass       # Database responsibility
    def send_welcome_email(self): pass # Email responsibility
    def validate_email(self): pass     # Validation responsibility

# Three reasons to change:
# 1. Database schema changes
# 2. Email provider changes
# 3. Validation rules change
```

### Identifying SRP Violations

Signs of SRP violations:
1. Class name contains "and" (UserAndOrderManager)
2. Class has methods in distinct groups
3. Class has many public methods (> 7-10)
4. You struggle to describe class in one sentence
5. thai-lint srp flags the class

### Running SRP Linter

```bash
# Run SRP linter
make lint-solid

# Or directly:
poetry run thai-lint srp src/ --config .thailint.yaml
```

### Fixing SRP Violations

**Step 1: Identify responsibilities**

List all public methods and group by responsibility:

```python
class OrderManager:
    # Group 1: Order CRUD
    def create_order(self): pass
    def update_order(self): pass
    def delete_order(self): pass

    # Group 2: Payment
    def process_payment(self): pass
    def refund_payment(self): pass

    # Group 3: Notifications
    def send_confirmation_email(self): pass
    def send_shipping_notification(self): pass

# Three responsibilities: Orders, Payments, Notifications
```

**Step 2: Extract to separate classes**

```python
class OrderRepository:
    """Store and retrieve orders."""
    def create(self, order): pass
    def update(self, order): pass
    def delete(self, order_id): pass


class PaymentProcessor:
    """Process order payments."""
    def process(self, payment): pass
    def refund(self, payment_id): pass


class OrderNotifications:
    """Send order-related notifications."""
    def send_confirmation(self, order): pass
    def send_shipping_update(self, order): pass


class OrderService:
    """Coordinate order operations."""
    def __init__(self, repo, payments, notifications):
        self.repo = repo
        self.payments = payments
        self.notifications = notifications
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Over-Splitting

**Problem**: Creating too many tiny classes

```python
# Too much splitting
class EmailAddressValidator:
    """Validate email addresses."""
    def validate(self, email): pass


class EmailAddressFormatter:
    """Format email addresses."""
    def format(self, email): pass


class EmailAddressNormalizer:
    """Normalize email addresses."""
    def normalize(self, email): pass

# Better: Group related functionality
class EmailAddress:
    """Email address operations."""
    def validate(self, email): pass
    def format(self, email): pass
    def normalize(self, email): pass
```

**Rule of thumb**: If classes are always used together, they should probably be one class.

### Anti-Pattern 2: Premature Optimization

**Problem**: Refactoring code that isn't complex or violating SRP

```python
# This is fine - don't over-engineer
class Calculator:
    """Perform calculations."""
    def add(self, a, b): return a + b
    def subtract(self, a, b): return a - b
    def multiply(self, a, b): return a * b
    def divide(self, a, b): return a / b

# Complexity: A-grade (all methods are trivial)
# SRP: Single responsibility (arithmetic)
# Don't split this!
```

**Rule of thumb**: If it's A-grade complexity and SRP is clear, leave it alone.

### Anti-Pattern 3: Creating Complexity Elsewhere

**Problem**: Moving complexity instead of reducing it

```python
# Before: Complex OrderProcessor
class OrderProcessor:
    def process(self, order):  # B-grade complexity
        # Complex processing logic
        pass

# Bad refactoring: Complexity moved to coordinator
class OrderValidator: pass
class OrderCalculator: pass
class OrderFulfiller: pass

class OrderCoordinator:
    def process(self, order):  # Still B-grade complexity!
        # Complex coordination logic
        validator = OrderValidator()
        calculator = OrderCalculator()
        fulfiller = OrderFulfiller()
        # ... complex coordination
        pass

# Better: Actually simplify the logic
class OrderProcessor:
    def process(self, order):  # A-grade complexity
        self._validate(order)
        self._calculate_totals(order)
        self._fulfill(order)

    def _validate(self, order): pass  # A-grade
    def _calculate_totals(self, order): pass  # A-grade
    def _fulfill(self, order): pass  # A-grade
```

**Rule of thumb**: Refactoring should reduce total complexity, not just move it.

### Anti-Pattern 4: God Objects via Dependency Injection

**Problem**: Injecting too many dependencies

```python
# Anti-pattern: Too many dependencies
class OrderService:
    def __init__(
        self,
        validator,
        calculator,
        inventory,
        payments,
        shipping,
        notifications,
        analytics,
        logging,
        cache,
    ):  # 9 dependencies!
        # This is a God Object disguised by dependency injection
        pass

# Better: Group related dependencies
class OrderService:
    def __init__(
        self,
        order_ops: OrderOperations,
        payment_service: PaymentService,
        notification_service: NotificationService,
    ):  # 3 logical groups
        pass
```

**Rule of thumb**: If a class needs > 5 dependencies, it's probably doing too much.

---

## Validation Workflow

### Running Quality Checks

```bash
# Check complexity
make lint-complexity

# Look for:
# - Radon output: Average complexity per file
# - Xenon output: Should show NO errors
# - Nesting linter: Should show no violations

# Check SRP
make lint-solid

# Look for:
# - Classes flagged for multiple responsibilities
# - Should show no violations

# Check tests still pass
make test

# Must exit with code 0
```

### Interpreting Results

**Xenon Output**:
```
# Good - no output means all A-grade
make lint-complexity
✓ Xenon passed

# Bad - shows violations
ERROR:xenon:src/example.py
  OrderProcessor.process:15 - B (6)

# Fix the flagged method until it's A-grade
```

**SRP Linter Output**:
```
# Good
make lint-solid
✓ SRP checks passed

# Bad
src/user_service.py:10
  UserService has multiple responsibilities:
  - User CRUD operations
  - Authentication
  - Email notifications

# Split UserService into focused classes
```

### Success Criteria

Before committing:

- [ ] `make lint-complexity` exits with code 0
- [ ] Xenon shows **NO errors** (all A-grade)
- [ ] Radon average complexity is **< 5.0 per file**
- [ ] `make lint-solid` exits with code 0
- [ ] No SRP violations flagged
- [ ] `make test` exits with code 0
- [ ] All tests still pass

---

## Complete Example: Before and After

### Before: Multiple Issues

```python
# src/services/order_service.py
class OrderService:
    """Handle order operations."""

    def create_order(self, order_data: dict) -> dict:
        """Create and process order."""
        # Validate (10 lines)
        if not order_data.get("customer_id"):
            raise ValueError("Missing customer_id")
        if not order_data.get("items"):
            raise ValueError("Missing items")
        if not isinstance(order_data["items"], list):
            raise ValueError("Items must be list")
        for item in order_data["items"]:
            if not item.get("product_id"):
                raise ValueError("Missing product_id")
            if not item.get("quantity"):
                raise ValueError("Missing quantity")

        # Calculate totals (10 lines)
        subtotal = 0
        for item in order_data["items"]:
            product = db.get_product(item["product_id"])
            item_total = product["price"] * item["quantity"]
            subtotal += item_total

        tax = subtotal * 0.08
        shipping = 10.0 if subtotal < 50 else 0
        total = subtotal + tax + shipping

        # Update inventory (10 lines)
        for item in order_data["items"]:
            current = inventory.get_quantity(item["product_id"])
            new_quantity = current - item["quantity"]
            if new_quantity < 0:
                raise ValueError(f"Insufficient inventory for {item['product_id']}")
            inventory.set_quantity(item["product_id"], new_quantity)

        # Save order (5 lines)
        order_id = db.insert_order({
            "customer_id": order_data["customer_id"],
            "items": order_data["items"],
            "total": total,
            "status": "pending",
        })

        # Send email (5 lines)
        customer = db.get_customer(order_data["customer_id"])
        email_body = f"Order {order_id} confirmed. Total: ${total}"
        smtp.send(customer["email"], "Order Confirmation", email_body)

        return {"order_id": order_id, "total": total}

# Issues:
# - 50+ lines (B-grade complexity)
# - SRP violations: validates, calculates, updates inventory, saves, sends email
# - Hard to test (many dependencies)
# - Hard to reuse parts
```

### After: Refactored

```python
# src/validation/order_validator.py
class OrderValidator:
    """Validate order data."""

    def validate(self, order_data: dict) -> None:
        """Validate order data structure and contents.

        Args:
            order_data: Order data to validate

        Raises:
            ValueError: If validation fails
        """
        self._validate_customer(order_data)
        self._validate_items(order_data)

    def _validate_customer(self, order_data: dict) -> None:
        """Validate customer data."""
        if not order_data.get("customer_id"):
            raise ValueError("Missing customer_id")

    def _validate_items(self, order_data: dict) -> None:
        """Validate order items."""
        if not order_data.get("items"):
            raise ValueError("Missing items")
        if not isinstance(order_data["items"], list):
            raise ValueError("Items must be list")

        for item in order_data["items"]:
            if not item.get("product_id"):
                raise ValueError("Missing product_id")
            if not item.get("quantity"):
                raise ValueError("Missing quantity")


# src/calculation/order_calculator.py
class OrderCalculator:
    """Calculate order totals and pricing."""

    TAX_RATE = 0.08
    FREE_SHIPPING_THRESHOLD = 50.0
    SHIPPING_COST = 10.0

    def calculate_total(self, items: list[dict]) -> dict:
        """Calculate order total breakdown.

        Args:
            items: List of order items

        Returns:
            Dictionary with subtotal, tax, shipping, total
        """
        subtotal = self._calculate_subtotal(items)
        tax = subtotal * self.TAX_RATE
        shipping = self._calculate_shipping(subtotal)
        total = subtotal + tax + shipping

        return {
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total,
        }

    def _calculate_subtotal(self, items: list[dict]) -> float:
        """Calculate subtotal from items."""
        subtotal = 0
        for item in items:
            product = db.get_product(item["product_id"])
            item_total = product["price"] * item["quantity"]
            subtotal += item_total
        return subtotal

    def _calculate_shipping(self, subtotal: float) -> float:
        """Calculate shipping cost based on subtotal."""
        if subtotal >= self.FREE_SHIPPING_THRESHOLD:
            return 0.0
        return self.SHIPPING_COST


# src/inventory/inventory_updater.py
class InventoryUpdater:
    """Update product inventory levels."""

    def reserve_items(self, items: list[dict]) -> None:
        """Reserve inventory for order items.

        Args:
            items: List of order items to reserve

        Raises:
            ValueError: If insufficient inventory
        """
        for item in items:
            self._reserve_item(item)

    def _reserve_item(self, item: dict) -> None:
        """Reserve single item from inventory."""
        product_id = item["product_id"]
        quantity = item["quantity"]

        current = inventory.get_quantity(product_id)
        new_quantity = current - quantity

        if new_quantity < 0:
            raise ValueError(f"Insufficient inventory for {product_id}")

        inventory.set_quantity(product_id, new_quantity)


# src/repositories/order_repository.py
class OrderRepository:
    """Store and retrieve orders from database."""

    def save(self, order_data: dict) -> str:
        """Save order to database.

        Args:
            order_data: Order data to save

        Returns:
            Created order ID
        """
        return db.insert_order(order_data)


# src/notifications/order_notifications.py
class OrderNotifications:
    """Send order-related notifications."""

    def send_confirmation(self, customer_id: str, order_id: str, total: float) -> None:
        """Send order confirmation email.

        Args:
            customer_id: Customer to notify
            order_id: Order ID
            total: Order total
        """
        customer = db.get_customer(customer_id)
        email_body = f"Order {order_id} confirmed. Total: ${total}"
        smtp.send(customer["email"], "Order Confirmation", email_body)


# src/services/order_service.py
class OrderService:
    """Coordinate order creation workflow."""

    def __init__(
        self,
        validator: OrderValidator,
        calculator: OrderCalculator,
        inventory: InventoryUpdater,
        repository: OrderRepository,
        notifications: OrderNotifications,
    ):
        """Initialize order service.

        Args:
            validator: Order validation service
            calculator: Order calculation service
            inventory: Inventory management service
            repository: Order data repository
            notifications: Order notification service
        """
        self.validator = validator
        self.calculator = calculator
        self.inventory = inventory
        self.repository = repository
        self.notifications = notifications

    def create_order(self, order_data: dict) -> dict:
        """Create and process new order.

        Args:
            order_data: Order data from customer

        Returns:
            Created order details

        Raises:
            ValueError: If validation or inventory reservation fails
        """
        self.validator.validate(order_data)
        totals = self.calculator.calculate_total(order_data["items"])
        self.inventory.reserve_items(order_data["items"])

        order_id = self.repository.save({
            "customer_id": order_data["customer_id"],
            "items": order_data["items"],
            "total": totals["total"],
            "status": "pending",
        })

        self.notifications.send_confirmation(
            order_data["customer_id"],
            order_id,
            totals["total"]
        )

        return {"order_id": order_id, "total": totals["total"]}

# Results:
# ✅ Complexity: All methods A-grade
# ✅ SRP: Each class has one responsibility
# ✅ Testability: Easy to test each component
# ✅ Reusability: Can use OrderCalculator, OrderValidator elsewhere
# ✅ Maintainability: Clear separation of concerns
```

---

## When to Accept B-Grade

Sometimes B-grade complexity is acceptable. Document the justification.

**Acceptable cases**:
1. Complex business logic that can't be simplified
2. State machines with many states
3. Parser/interpreter logic
4. Algorithms with inherent complexity

**Example**:
```python
def process_state_machine(state: str, event: str) -> str:
    """Process state machine transitions.

    Note: B-grade complexity accepted due to inherent state machine
    complexity. Splitting would make logic harder to understand.

    Args:
        state: Current state
        event: Event to process

    Returns:
        New state
    """
    # pylint: disable=too-many-branches
    # Justification: State machine requires many branches
    if state == "idle":
        if event == "start":
            return "running"
        elif event == "error":
            return "error"
    elif state == "running":
        if event == "pause":
            return "paused"
        elif event == "stop":
            return "idle"
        elif event == "error":
            return "error"
    # ... more states
    # pylint: enable=too-many-branches

# This is B-grade but documented and justified
```

**Requirements**:
1. Document why B-grade is necessary
2. Add pylint disable comment with justification
3. Get approval in code review
4. Keep exception list minimal

---

## Next Steps

After completing architectural refactoring:

### 1. Final Validation

```bash
# Run everything
make lint-full
make test

# Both must exit with code 0
```

### 2. Commit Changes

```bash
git add .
git commit -m "refactor: Improve code quality (complexity + SRP)"
```

### 3. Continuous Improvement

- Monitor complexity in new code
- Refactor proactively when adding features
- Keep classes focused and small
- Use composition over inheritance
- Write tests first (TDD helps prevent complexity)

---

## See Also

- **Basic linting**: `.ai/howtos/how-to-fix-linting-errors.md`
- **Quality standards**: `AGENTS.md` (Quality Gates section)
- **Testing**: `.ai/howtos/how-to-write-tests.md`
- **Makefile targets**: `Makefile` (quality check commands)
- **Complexity tools**: Radon, Xenon documentation
- **SRP linter**: `poetry run thai-lint srp --help`
