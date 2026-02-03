"""
Purpose: Configuration constants for Rust validation trials

Scope: Repository definitions, rule lists, thresholds, and SSD storage paths

Overview: Defines all configuration constants for the Rust linter validation trial infrastructure.
    Includes pinned repository definitions with specific release tags for reproducibility,
    the list of linter rules to test, the false positive rate threshold (5%), and default
    storage paths on the external Toshiba SSD for cloned repos and result files. Pinned tags
    ensure identical results regardless of when trials are re-run.

Dependencies: pathlib for path construction

Exports: REPOS, RULES, FP_THRESHOLD, DEFAULT_BASE_DIR, DEFAULT_REPO_DIR, DEFAULT_RESULTS_DIR

Interfaces: Configuration constants consumed by run_trials.py, classify.py, and generate_report.py

Implementation: Simple constant definitions with Path objects for SSD storage locations
"""

from pathlib import Path

REPOS: list[dict[str, str]] = [
    {
        "name": "ripgrep",
        "url": "https://github.com/BurntSushi/ripgrep.git",
        "tag": "15.1.0",
        "description": "Gold standard Rust code, exemplary error handling",
    },
    {
        "name": "tokio",
        "url": "https://github.com/tokio-rs/tokio.git",
        "tag": "tokio-1.49.0",
        "description": "Async runtime, validates blocking-in-async detector",
    },
    {
        "name": "serde",
        "url": "https://github.com/serde-rs/serde.git",
        "tag": "v1.0.228",
        "description": "Macro-heavy serialization framework, tests parser robustness",
    },
    {
        "name": "clap",
        "url": "https://github.com/clap-rs/clap.git",
        "tag": "v4.5.57",
        "description": "CLI library with rich struct/impl patterns",
    },
    {
        "name": "reqwest",
        "url": "https://github.com/seanmonstar/reqwest.git",
        "tag": "v0.13.1",
        "description": "HTTP client with extensive async patterns",
    },
    {
        "name": "actix-web",
        "url": "https://github.com/actix/actix-web.git",
        "tag": "web-v4.12.1",
        "description": "Async-heavy web framework",
    },
]

RULES: list[str] = [
    "unwrap-abuse",
    "clone-abuse",
    "blocking-async",
    "srp",
    "nesting",
    "magic-numbers",
]

FP_THRESHOLD: float = 0.05

DEFAULT_BASE_DIR: Path = Path("/home/stevejackson/mnt/toshiba/thai-lint-eval/rust-trials")
DEFAULT_REPO_DIR: Path = DEFAULT_BASE_DIR / "repos"
DEFAULT_RESULTS_DIR: Path = DEFAULT_BASE_DIR / "results"
