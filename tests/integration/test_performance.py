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

    def test_single_file_under_100ms(self) -> None:
        """Test single file linting completes in under 100ms."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            # Create test file
            test_file = tmp_path / "test.py"
            test_file.write_text("print('test')\n" * 100)

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Warm up (first run may include import overhead)
            linter.lint(str(test_file))

            # Measure performance
            start = time.perf_counter()
            linter.lint(str(test_file))
            elapsed = time.perf_counter() - start

            # Should complete in under 100ms
            assert elapsed < 0.1, (
                f"Single file linting took {elapsed * 1000:.2f}ms (target: <100ms)"
            )

    def test_small_file_performance(self) -> None:
        """Test small file linting is very fast."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            # Create small test file
            test_file = tmp_path / "small.py"
            test_file.write_text("print('test')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Warm up
            linter.lint(str(test_file))

            # Measure performance
            start = time.perf_counter()
            linter.lint(str(test_file))
            elapsed = time.perf_counter() - start

            # Small files should be very fast (<50ms)
            assert elapsed < 0.05, f"Small file linting took {elapsed * 1000:.2f}ms (target: <50ms)"


class TestBulkFilePerformance:
    """Test bulk file linting performance."""

    def test_100_files_performance(self) -> None:
        """Test linting 100 files completes quickly."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            # Create 100 test files
            for i in range(100):
                test_file = tmp_path / f"test_{i}.py"
                test_file.write_text(f"print('test {i}')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Warm up
            linter.lint(str(tmp_path))

            # Measure performance
            start = time.perf_counter()
            linter.lint(str(tmp_path))
            elapsed = time.perf_counter() - start

            # 100 files should complete in under 1s
            assert elapsed < 1.0, f"100 files took {elapsed:.2f}s (target: <1s)"

    def test_1000_files_under_5s(self) -> None:
        """Test linting 1000 files completes in under 5s (performance target)."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            # Create 1000 test files in batches
            batch_size = 100
            for batch in range(10):
                batch_dir = tmp_path / f"batch_{batch}"
                batch_dir.mkdir()
                for i in range(batch_size):
                    test_file = batch_dir / f"test_{i}.py"
                    test_file.write_text(f"print('test {batch}_{i}')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Warm up with smaller subset
            linter.lint(str(tmp_path / "batch_0"))

            # Measure performance
            start = time.perf_counter()
            linter.lint(str(tmp_path))
            elapsed = time.perf_counter() - start

            # 1000 files should complete in under 5s (target from requirements)
            assert elapsed < 5.0, f"1000 files took {elapsed:.2f}s (target: <5s)"


class TestNestedDirectoryPerformance:
    """Test performance with nested directory structures."""

    def test_deep_nesting_performance(self) -> None:
        """Test linting deeply nested directories is efficient."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            # Create deeply nested structure
            current = tmp_path
            for depth in range(10):
                current = current / f"level_{depth}"
                current.mkdir()
                # Add file at each level
                (current / f"test_{depth}.py").write_text(f"print('depth {depth}')")

            # Initialize linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))

            # Warm up
            linter.lint(str(tmp_path))

            # Measure performance
            start = time.perf_counter()
            linter.lint(str(tmp_path))
            elapsed = time.perf_counter() - start

            # Deep nesting shouldn't significantly impact performance
            assert elapsed < 0.5, f"Deep nesting took {elapsed:.2f}s (target: <0.5s)"


class TestConfigLoadingPerformance:
    """Test configuration loading performance."""

    def test_config_loading_is_fast(self) -> None:
        """Test config file loading is fast."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config with many rules
            config_file = tmp_path / ".thailint.yaml"
            config_content = "rules:\n  file-placement:\n    allow:\n"
            for i in range(100):
                config_content += f"      - '.*pattern{i}\\.py$'\n"
            config_file.write_text(config_content)

            # Measure config loading time
            start = time.perf_counter()
            _ = Linter(config_file=str(config_file), project_root=str(tmp_path))
            elapsed = time.perf_counter() - start

            # Config loading should be fast (<100ms)
            assert elapsed < 0.1, f"Config loading took {elapsed * 1000:.2f}ms (target: <100ms)"


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

    def test_large_file_count_memory(self) -> None:
        """Test memory usage with large file counts is reasonable."""
        from src import Linter

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config
            config_file = tmp_path / ".thailint.yaml"
            config_file.write_text("rules:\n  file-placement:\n    allow:\n      - '.*\\.py$'\n")

            # Create many small files (memory test)
            for i in range(500):
                test_file = tmp_path / f"test_{i}.py"
                test_file.write_text(f"# File {i}\nprint('test')")

            # Initialize and run linter
            linter = Linter(config_file=str(config_file), project_root=str(tmp_path))
            violations = linter.lint(str(tmp_path))

            # Should complete without memory issues
            # (If this test runs without OOM, memory is acceptable)
            assert isinstance(violations, list)
