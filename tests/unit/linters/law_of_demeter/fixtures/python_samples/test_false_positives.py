"""
Purpose: False positive code samples for Law of Demeter filter testing

Scope: Python code patterns that should NOT be flagged as LoD violations

Overview: Contains inline Python code strings representing chains that look like LoD violations
    by depth but are legitimate patterns. Each sample maps to one of the 9 classifier filters.
    Derived from patterns observed in Flask, httpx, pydantic, Django, pandas, scikit-learn,
    SQLAlchemy, and other real-world codebases during prototype testing.

Dependencies: None (pure string constants)

Exports: String constants for false-positive test cases grouped by filter category

Interfaces: Import constants by name or filter category

Implementation: Each constant is a complete Python code snippet parseable by ast.parse()
"""

# =============================================================================
# FILTER 1: Safe prefix (self., cls., config., etc.)
# =============================================================================

SELF_ATTRIBUTE_ACCESS = """
class MyClass:
    def method(self):
        return self.config.database.host
"""

CLS_ATTRIBUTE_ACCESS = """
class MyClass:
    @classmethod
    def factory(cls):
        return cls.defaults.connection.timeout
"""

SETTINGS_ACCESS = """
def configure(settings):
    host = settings.database.connection.host
"""

CONFIG_ACCESS = """
def setup(config):
    timeout = config.http.client.timeout
"""

LOGGER_CHAIN = """
import logging
def do_work():
    logging.getLogger("app").handlers[0].setLevel(10)
"""

REQUEST_DATA_ACCESS = """
def handle(request):
    value = request.POST.get("key").strip()
"""

# =============================================================================
# FILTER 2: Module-qualified access (import-aware)
# =============================================================================

OS_PATH_ACCESS = """
import os
def get_home():
    return os.path.expanduser("~").strip()
"""

STDLIB_MODULE_CHAIN = """
import json
def parse(text):
    return json.loads(text).get("key").upper()
"""

THIRD_PARTY_MODULE = """
import flask
def create_app():
    return flask.Flask(__name__).register_blueprint(bp)
"""

FROM_IMPORT_MODULE = """
from pathlib import Path
def resolve(p):
    return Path(p).resolve().parent.name
"""

DATETIME_MODULE = """
import datetime
def now_str():
    return datetime.datetime.now().isoformat().split("T")[0]
"""

NUMPY_MODULE = """
import numpy as np
def compute(arr):
    return np.array(arr).reshape(-1, 1).tolist()
"""

# =============================================================================
# FILTER 3: Same-type string/bytes chaining
# =============================================================================

STRING_METHOD_CHAIN = """
def clean(text):
    return text.strip().lower().replace("-", "_")
"""

STRING_SPLIT_AND_PROCESS = """
def parse_version(version):
    return version.partition("+")[0].split(".")
"""

STRING_ATTR_THEN_METHODS = """
def get_clean_name(node):
    return node.name.strip().lower()
"""

REGEX_GROUP_CHAIN = """
import re
def extract(pattern, text):
    m = re.match(pattern, text)
    return m.group(1).strip().upper()
"""

# =============================================================================
# FILTER 4: Fluent/builder/collection pipeline
# =============================================================================

ORM_QUERY_CHAIN = """
def get_active_users(db):
    return db.query(User).filter(active=True).order_by("name").limit(10)
"""

BUILDER_PATTERN = """
def build_config(builder):
    return builder.set("host", "localhost").set("port", 8080).build()
"""

DJANGO_QUERYSET = """
def get_posts(request):
    return Post.objects.filter(published=True).exclude(draft=True).order_by("-date")
"""

PANDAS_PIPELINE = """
def transform(df):
    return df.filter(items=["a", "b"]).groupby("a").sum()
"""

# =============================================================================
# FILTER 5: AST / compiler node traversal
# =============================================================================

AST_NODE_WALK = """
import ast
def get_func_name(node):
    return node.func.value.attr
"""

AST_DEEP_TRAVERSAL = """
def extract_target(node):
    return node.targets[0].value.id
"""

MYPY_NODE_ACCESS = """
def get_type_info(node):
    return node.callee.node.fullname
"""

# =============================================================================
# FILTER 6: Dunder / protocol access
# =============================================================================

DUNDER_CLASS_ACCESS = """
def get_class_name(obj):
    return obj.__class__.__name__.lower()
"""

DUNDER_MODULE_ACCESS = """
def get_module(func):
    return func.__module__.__class__.__name__
"""

# =============================================================================
# FILTER 7: Subscript-heavy chains
# =============================================================================

DICT_NAVIGATION = """
def get_nested(data):
    return data["config"]["database"]["host"]
"""

LIST_INDEX_ACCESS = """
def first_word(lines):
    return lines[0].split()[0].strip()
"""

SUBSCRIPT_WITH_ATTR = """
def get_header(response):
    return response.headers["Content-Type"].split(";")[0]
"""

# =============================================================================
# FILTER 8: Safe terminal methods
# =============================================================================

ENDS_WITH_ITEMS = """
def get_entries(registry):
    return registry.store.data.items()
"""

ENDS_WITH_EXISTS = """
def check_file(project):
    return project.root.config_path.exists()
"""

ENDS_WITH_ENCODE = """
def to_bytes(record):
    return record.payload.body.encode()
"""

ENDS_WITH_TO_DICT = """
def serialize(model):
    return model.instance.data.to_dict()
"""

# =============================================================================
# FILTER 9: Test file leniency
# =============================================================================

TEST_ASSERTION_CHAIN = """
def test_response_body(client):
    assert client.get("/api").json()["data"].get("id") == 1
"""

TEST_MOCK_CHAIN = """
def test_setup(mocker):
    mocker.patch("module.Class").return_value.method.return_value = 42
"""

# =============================================================================
# PASSING (depth < 3, should never be flagged)
# =============================================================================

SIMPLE_ATTRIBUTE = """
def get_name(user):
    return user.name
"""

TWO_DEEP_CHAIN = """
def get_city(user):
    return user.address.city
"""

SINGLE_METHOD_CALL = """
def process(data):
    return data.transform()
"""
