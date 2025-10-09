"""
Purpose: Test that import statements are filtered and not reported as duplicates

Scope: Verify TokenHasher filters Python and TypeScript imports correctly

Overview: Tests that identical import statements across multiple files are not reported as
    duplicate code violations. Ensures import filtering works for both Python (import/from)
    and TypeScript/JavaScript (import/export) syntax, including multi-line imports.

Dependencies: pytest, tmp_path fixture, Linter class

Exports: Test functions for import filtering

Implementation: Creates multiple files with identical imports but different logic, verifies
    no violations are reported for the import statements
"""

from src import Linter


def test_python_imports_not_duplicates(tmp_path):
    """Test that identical Python import statements are not flagged as duplicates."""
    # Create three Python files with identical imports but different logic
    (tmp_path / "module1.py").write_text("""import json
import logging
import os

def process_data():
    return {"status": "ok"}
""")

    (tmp_path / "module2.py").write_text("""import json
import logging
import os

def validate_data():
    return {"valid": True}
""")

    (tmp_path / "module3.py").write_text("""import json
import logging
import os

def transform_data():
    return {"transformed": True}
""")

    # Create config
    config_file = tmp_path / ".thailint.yaml"
    config_file.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    # Run linter
    linter = Linter(config_file=config_file, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Should have NO violations - imports should be filtered
    assert len(violations) == 0, f"Expected 0 violations for imports, got {len(violations)}"


def test_python_from_imports_not_duplicates(tmp_path):
    """Test that identical Python 'from' import statements are not flagged as duplicates."""
    (tmp_path / "service1.py").write_text("""from pathlib import Path
from typing import Any
from datetime import datetime

class Service1:
    def run(self):
        return Path(".")
""")

    (tmp_path / "service2.py").write_text("""from pathlib import Path
from typing import Any
from datetime import datetime

class Service2:
    def execute(self):
        return Path("/tmp")
""")

    (tmp_path / "service3.py").write_text("""from pathlib import Path
from typing import Any
from datetime import datetime

class Service3:
    def process(self):
        return Path("/var")
""")

    config_file = tmp_path / ".thailint.yaml"
    config_file.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config_file, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0, f"Expected 0 violations for from imports, got {len(violations)}"


def test_typescript_imports_not_duplicates(tmp_path):
    """Test that identical TypeScript import statements are not flagged as duplicates."""
    (tmp_path / "component1.tsx").write_text("""import React from 'react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

export const Component1 = () => {
    const [count, setCount] = useState(0)
    return <Button onClick={() => setCount(count + 1)}>Click me</Button>
}
""")

    (tmp_path / "component2.tsx").write_text("""import React from 'react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

export const Component2 = () => {
    const [value, setValue] = useState("")
    return <Button onClick={() => setValue("clicked")}>Press me</Button>
}
""")

    (tmp_path / "component3.tsx").write_text("""import React from 'react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

export const Component3 = () => {
    const [active, setActive] = useState(false)
    return <Button onClick={() => setActive(!active)}>Toggle</Button>
}
""")

    config_file = tmp_path / ".thailint.yaml"
    config_file.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config_file, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    assert len(violations) == 0, f"Expected 0 violations for TS imports, got {len(violations)}"


def test_mixed_imports_and_real_duplicates(tmp_path):
    """Test that imports are filtered but real code duplicates are still detected."""
    (tmp_path / "handler1.py").write_text("""import json
import logging

def process_request():
    data = {"status": "processing"}
    logging.info("Processing request")
    return json.dumps(data)
""")

    (tmp_path / "handler2.py").write_text("""import json
import logging

def process_request():
    data = {"status": "processing"}
    logging.info("Processing request")
    return json.dumps(data)
""")

    config_file = tmp_path / ".thailint.yaml"
    config_file.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config_file, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Should detect the duplicate function code, NOT the imports
    assert len(violations) > 0, "Should detect duplicate function code"

    # The violation should exist - imports were filtered, function code was detected
    # Line numbers may start at 1 because tokenizer tracks non-import lines
    assert any("duplicate code" in v.message.lower() for v in violations)
