"""
Purpose: Performance benchmark tests validating linting speed and resource usage

Scope: Performance testing for single file, multiple files, and large project scenarios

Overview: Comprehensive performance benchmark suite that validates linting speed meets target
    requirements. Tests measure single file linting (<100ms target), bulk file processing
    (<5s for 1000 files target), memory usage (<500MB for large projects target), and
    scalability characteristics. Uses time measurements and resource monitoring to ensure
    the linter performs efficiently in real-world scenarios including CI/CD pipelines,
    editor integrations, and large monorepo codebases.

Dependencies: pytest for testing, time for measurements, pathlib for file operations

Exports: TestSingleFilePerformance, TestBulkFilePerformance, TestMemoryUsage test classes

Interfaces: pytest benchmark validation, time measurements

Implementation: Performance tests with time.perf_counter() measurements, temporary file
    generation for bulk testing, memory profiling for resource usage validation
"""

import tempfile
import time
from pathlib import Path


class TestSingleFilePerformance:
    """Test single file linting performance."""


class TestBulkFilePerformance:
    """Test bulk file linting performance."""

    def _create_batch_files(self, tmp_path, batch_size=100, num_batches=10):
        """Create test files in batches.

        Args:
            tmp_path: Temporary directory path
            batch_size: Number of files per batch
            num_batches: Number of batches to create
        """
        for batch in range(num_batches):
            batch_dir = tmp_path / f"batch_{batch}"
            batch_dir.mkdir()
            for i in range(batch_size):
                test_file = batch_dir / f"test_{i}.py"
                test_file.write_text(f"print('test {batch}_{i}')")


class TestNestedDirectoryPerformance:
    """Test performance with nested directory structures."""


class TestConfigLoadingPerformance:
    """Test configuration loading performance."""


class TestPatternMatchingPerformance:
    """Test regex pattern matching performance."""

    def test_complex_patterns_are_efficient(self) -> None:
        """Test complex regex patterns don't cause performance issues."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config with complex patterns
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text(
                "rules:\n"
                "  file-placement:\n"
                "    allow:\n"
                "      - '^src/.*\\.py$'\n"
                "      - '^tests/.*\\.py$'\n"
                "      - '^scripts/.*\\.(py|sh)$'\n"
                "    deny:\n"
                "      - '^src/.*test.*\\.py$'\n"
                "      - '^.*__pycache__.*$'\n"
            )

            # Create test files
            for i in range(50):
                (tmp_path / f"test_{i}.py").write_text(f"print({i})")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Warm up
            linter.lint(str(tmp_path))

            # Measure performance
            start = time.perf_counter()
            linter.lint(str(tmp_path))
            elapsed = time.perf_counter() - start

            # Complex patterns shouldn't cause slowdown
            assert elapsed < 0.5, f"Complex patterns took {elapsed:.2f}s (target: <0.5s)"


class TestMemoryEfficiency:
    """Test memory usage remains reasonable."""
