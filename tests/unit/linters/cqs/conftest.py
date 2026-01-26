"""
Purpose: Shared pytest fixtures for CQS linter tests

Scope: Fixtures for mock contexts, sample code, and configurations

Overview: Provides shared fixtures and helper functions for CQS linter testing. Includes
    mock context creation, configuration fixtures, and sample code constants for testing
    CQS violation detection. Supports TDD approach with test data for INPUT operations,
    OUTPUT operations, and functions that mix both (violations).

Dependencies: pytest, pathlib, unittest.mock

Exports: Fixture functions and test data constants

Interfaces: Factory functions for test setup

Implementation: pytest fixtures with factory pattern for flexible test setup
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from src.linters.cqs.config import CQSConfig


def create_mock_context(
    code: str,
    filename: str = "test.py",
    language: str = "python",
    metadata: dict[str, Any] | None = None,
) -> Mock:
    """Create mock lint context for testing."""
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = metadata or {}
    return context


@pytest.fixture
def default_config() -> CQSConfig:
    """Create default CQS configuration for testing."""
    return CQSConfig()


@pytest.fixture
def strict_config() -> CQSConfig:
    """Create strict config with no ignores for comprehensive testing."""
    return CQSConfig(
        ignore_methods=[],
        ignore_decorators=[],
        ignore_patterns=[],
    )


@pytest.fixture
def mock_context():
    """Factory for creating mock lint contexts."""

    def _create(code: str, filename: str = "test.py") -> Mock:
        context = Mock()
        context.file_path = Path(filename)
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        return context

    return _create


# =============================================================================
# TEST DATA - CQS VIOLATIONS (functions that mix INPUTs and OUTPUTs)
# =============================================================================

CQS_VIOLATION_BASIC = """
def process_and_save(user_id: int) -> None:
    data = fetch_data(user_id)  # INPUT: query returns value
    save_to_db(data)            # OUTPUT: command discards return
"""

CQS_VIOLATION_MULTIPLE_INPUTS_OUTPUTS = """
def complex_operation(config: dict) -> None:
    user = get_user(config["id"])      # INPUT
    settings = load_settings()          # INPUT
    update_user(user)                   # OUTPUT
    notify_admin()                      # OUTPUT
"""

CQS_VIOLATION_ASYNC = """
async def async_mixed(item_id: int) -> None:
    item = await fetch_item(item_id)    # INPUT
    await save_item(item)               # OUTPUT
"""

CQS_VIOLATION_METHOD = """
class DataProcessor:
    def process(self, data_id: int) -> None:
        self.data = self.load_data(data_id)  # INPUT
        self.persist()                        # OUTPUT
"""

CQS_VIOLATION_NESTED = """
def outer() -> None:
    def inner() -> None:
        result = query()   # INPUT
        command(result)    # OUTPUT
    inner()
"""

# =============================================================================
# TEST DATA - VALID PATTERNS (no CQS violation)
# =============================================================================

CQS_VALID_QUERY_ONLY = """
def get_user_data(user_id: int) -> dict:
    user = fetch_user(user_id)
    settings = load_user_settings(user_id)
    return {"user": user, "settings": settings}
"""

CQS_VALID_COMMAND_ONLY = """
def update_all_records() -> None:
    update_users()
    notify_admins()
    clear_cache()
"""

CQS_VALID_FLUENT_INTERFACE = """
def configure(self) -> "Builder":
    self.set_option("a", 1)
    self.set_option("b", 2)
    return self
"""

CQS_VALID_CONSTRUCTOR = """
class Service:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.data = load_initial_data(config)
        setup_logging()
"""

CQS_VALID_PROPERTY = """
class User:
    @property
    def full_name(self) -> str:
        first = self.get_first_name()
        last = self.get_last_name()
        return f"{first} {last}"
"""

CQS_VALID_RETURN_CALL = """
def get_processed_data(raw: dict) -> dict:
    transformed = transform(raw)
    return process(transformed)  # Not OUTPUT - return uses value
"""

# =============================================================================
# TEST DATA - INPUT PATTERNS
# =============================================================================

INPUT_SIMPLE_ASSIGNMENT = """
def example() -> None:
    x = func()
"""

INPUT_TUPLE_UNPACKING = """
def example() -> None:
    x, y = get_pair()
"""

INPUT_ASYNC_ASSIGNMENT = """
async def example() -> None:
    x = await async_func()
"""

INPUT_ATTRIBUTE_ASSIGNMENT = """
def example(self) -> None:
    self.data = fetch_data()
"""

INPUT_SUBSCRIPT_ASSIGNMENT = """
def example() -> None:
    cache[key] = compute_value()
"""

INPUT_ANNOTATED_ASSIGNMENT = """
def example() -> None:
    result: int = calculate()
"""

INPUT_WALRUS_OPERATOR = """
def example() -> None:
    if (data := get_data()) is not None:
        pass
"""

# =============================================================================
# TEST DATA - OUTPUT PATTERNS
# =============================================================================

OUTPUT_STATEMENT_CALL = """
def example() -> None:
    do_something()
"""

OUTPUT_ASYNC_STATEMENT = """
async def example() -> None:
    await send_notification()
"""

OUTPUT_METHOD_CALL = """
def example() -> None:
    obj.update_state()
"""

OUTPUT_CHAINED_CALL = """
def example() -> None:
    service.get_client().send_message()
"""

# =============================================================================
# TEST DATA - NOT OUTPUT (should not be detected as OUTPUT)
# =============================================================================

NOT_OUTPUT_RETURN = """
def example() -> int:
    return calculate()
"""

NOT_OUTPUT_IF_CONDITION = """
def example() -> None:
    if check_condition():
        pass
"""

NOT_OUTPUT_WHILE_CONDITION = """
def example() -> None:
    while has_more():
        pass
"""

NOT_OUTPUT_COMPREHENSION = """
def example() -> list:
    return [process(x) for x in items]
"""

NOT_OUTPUT_ASSIGNMENT = """
def example() -> None:
    result = compute()
"""

NOT_OUTPUT_ASSERT = """
def example() -> None:
    assert validate()
"""

# =============================================================================
# TEST DATA - EDGE CASES
# =============================================================================

EDGE_CASE_EMPTY_FUNCTION = """
def empty() -> None:
    pass
"""

EDGE_CASE_ONLY_DOCSTRING = """
def documented() -> None:
    '''This function does nothing.'''
    pass
"""

EDGE_CASE_NESTED_CLASS = """
class Outer:
    class Inner:
        def method(self) -> None:
            data = query()
            command(data)
"""

EDGE_CASE_LAMBDA = """
def example() -> None:
    fn = lambda x: process(x)
"""

EDGE_CASE_GENERATOR = """
def gen_example() -> None:
    data = fetch()
    yield from process(data)
"""

# =============================================================================
# TEST DATA - TYPESCRIPT CQS VIOLATIONS
# =============================================================================

TS_CQS_VIOLATION_BASIC = """
function processAndSave(userId: number): void {
    const data = fetchData(userId);  // INPUT
    saveToDb(data);                   // OUTPUT
}
"""

TS_CQS_VIOLATION_ARROW = """
const processAndSave = (userId: number): void => {
    const data = fetchData(userId);  // INPUT
    saveToDb(data);                   // OUTPUT
};
"""

TS_CQS_VIOLATION_ASYNC = """
async function asyncMixed(itemId: number): Promise<void> {
    const item = await fetchItem(itemId);  // INPUT
    await saveItem(item);                   // OUTPUT
}
"""

TS_CQS_VIOLATION_METHOD = """
class DataProcessor {
    process(dataId: number): void {
        const data = this.loadData(dataId);  // INPUT
        this.persist();                       // OUTPUT
    }
}
"""

TS_CQS_VIOLATION_DESTRUCTURING = """
function processUser(): void {
    const { name, email } = getUser();  // INPUT
    sendNotification(name, email);       // OUTPUT
}
"""

TS_CQS_VIOLATION_ARRAY_DESTRUCTURING = """
function processItems(): void {
    const [first, second] = getItems();  // INPUT
    processFirst(first);                  // OUTPUT
}
"""

TS_CQS_VIOLATION_MULTIPLE = """
function complexOperation(config: object): void {
    const user = getUser(config);     // INPUT
    const settings = loadSettings();  // INPUT
    updateUser(user);                 // OUTPUT
    notifyAdmin();                    // OUTPUT
}
"""

# =============================================================================
# TEST DATA - TYPESCRIPT VALID PATTERNS
# =============================================================================

TS_CQS_VALID_QUERY_ONLY = """
function getUserData(userId: number): object {
    const user = fetchUser(userId);
    const settings = loadUserSettings(userId);
    return { user, settings };
}
"""

TS_CQS_VALID_COMMAND_ONLY = """
function updateAllRecords(): void {
    updateUsers();
    notifyAdmins();
    clearCache();
}
"""

TS_CQS_VALID_FLUENT_INTERFACE = """
class Builder {
    configure(): Builder {
        this.setOption("a", 1);
        this.setOption("b", 2);
        return this;
    }
}
"""

TS_CQS_VALID_CONSTRUCTOR = """
class Service {
    constructor(config: object) {
        this.config = config;
        this.data = loadInitialData(config);
        setupLogging();
    }
}
"""

# =============================================================================
# TEST DATA - TYPESCRIPT INPUT PATTERNS
# =============================================================================

TS_INPUT_CONST_ASSIGNMENT = """
function example(): void {
    const x = func();
}
"""

TS_INPUT_LET_ASSIGNMENT = """
function example(): void {
    let x = func();
}
"""

TS_INPUT_OBJECT_DESTRUCTURING = """
function example(): void {
    const { a, b } = getData();
}
"""

TS_INPUT_ARRAY_DESTRUCTURING = """
function example(): void {
    const [first, second] = getPair();
}
"""

TS_INPUT_AWAIT_ASSIGNMENT = """
async function example(): Promise<void> {
    const x = await asyncFunc();
}
"""

TS_INPUT_THIS_ASSIGNMENT = """
class Example {
    load(): void {
        this.data = fetchData();
    }
}
"""

# =============================================================================
# TEST DATA - TYPESCRIPT OUTPUT PATTERNS
# =============================================================================

TS_OUTPUT_STATEMENT_CALL = """
function example(): void {
    doSomething();
}
"""

TS_OUTPUT_ASYNC_STATEMENT = """
async function example(): Promise<void> {
    await sendNotification();
}
"""

TS_OUTPUT_METHOD_CALL = """
function example(): void {
    obj.updateState();
}
"""

TS_OUTPUT_CHAINED_CALL = """
function example(): void {
    service.getClient().sendMessage();
}
"""

# =============================================================================
# TEST DATA - TYPESCRIPT NOT OUTPUT
# =============================================================================

TS_NOT_OUTPUT_RETURN = """
function example(): number {
    return calculate();
}
"""

TS_NOT_OUTPUT_IF_CONDITION = """
function example(): void {
    if (checkCondition()) {
        // do something
    }
}
"""

TS_NOT_OUTPUT_ASSIGNMENT = """
function example(): void {
    const result = compute();
}
"""
