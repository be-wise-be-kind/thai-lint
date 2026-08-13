"""
Purpose: Storage initialization for DRY linter

Scope: Initializes DuplicateStorage with SQLite storage

Overview: Handles storage initialization based on DRY configuration. Creates SQLite storage in
    memory, tempfile, or persistent mode based on config.storage_mode. Resolves the on-disk path
    for persistent mode to a stable, project-relative location so it survives between separate
    CLI invocations. Separated from the main linter rule to maintain SRP compliance.

Dependencies: DRYConfig, DRYCache, DuplicateStorage, pathlib.Path

Exports: initialize_storage function, DEFAULT_CACHE_DIR_NAME, DEFAULT_CACHE_FILE_NAME constants

Interfaces: initialize_storage(config, project_root) -> DuplicateStorage

Implementation: Module-level functions (no state to justify a class) creating DRYCache with
    storage_mode, delegating to DuplicateStorage for management
"""

from pathlib import Path

from .cache import DRYCache
from .config import DRYConfig
from .duplicate_storage import DuplicateStorage

# Default location for the persistent cross-run duplicate index, relative to project root.
DEFAULT_CACHE_DIR_NAME = ".thailint-cache"
DEFAULT_CACHE_FILE_NAME = "dry.db"


def initialize_storage(config: DRYConfig, project_root: Path | None = None) -> DuplicateStorage:
    """Initialize storage based on configuration.

    Args:
        config: DRY configuration
        project_root: Project root, used to resolve the default persistent cache path.
            Ignored unless storage_mode is "persistent" and no explicit shared_db_path
            override is set.

    Returns:
        DuplicateStorage instance with SQLite storage
    """
    db_path = _resolve_db_path(config, project_root)
    cache = DRYCache(storage_mode=config.storage_mode, db_path=db_path)

    return DuplicateStorage(cache)


def _resolve_db_path(config: DRYConfig, project_root: Path | None) -> Path | None:
    """Resolve the on-disk path to connect to, if any.

    config.shared_db_path (set by the orchestrator under --parallel) always takes
    precedence, since it points every worker at the same run-scoped shared file
    regardless of the configured storage_mode.
    """
    if config.shared_db_path:
        return Path(config.shared_db_path)
    if config.storage_mode == "persistent":
        root = project_root or Path.cwd()
        return root / DEFAULT_CACHE_DIR_NAME / DEFAULT_CACHE_FILE_NAME
    return None
