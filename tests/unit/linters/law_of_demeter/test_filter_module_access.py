"""
Purpose: Test module-access filter for Law of Demeter classifier

Scope: Filtering chains that start with known module names (import-aware)

Overview: Validates the module-access filter that allows chains rooted in module names.
    Chains like os.path.expanduser().strip() or json.loads().get().upper() are module-qualified
    access, not object navigation. The filter uses both known module roots (stdlib, common
    third-party) and file-specific import tracking to identify module names.

Dependencies: pytest, src.linters.law_of_demeter.chain_classifier,
    src.linters.law_of_demeter.python_analyzer

Exports: TestModuleAccessFilter (6 tests)

Interfaces: Tests classify_chain() returning "module-access:*" for module-rooted chains

Implementation: Creates FileImports with module names, calls classify_chain(),
    verifies module-access filter fires for known modules and imported names
"""

from src.linters.law_of_demeter.python_analyzer import FileImports


class TestModuleAccessFilter:
    """Test module-access filter identifies module-qualified chains."""

    def test_stdlib_module_allowed(self) -> None:
        """json.loads().get().upper() should be module-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        imports = FileImports()
        imports.module_names.add("json")
        parts = ["json", "loads()", "get()", "upper()"]
        result = classify_chain(parts, imports, "app.py")
        assert result.startswith("module-access")

    def test_known_module_root_without_import(self) -> None:
        """Known module roots should be recognized even without explicit import."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        imports = FileImports()
        parts = ["json", "loads()", "get()", "upper()"]
        result = classify_chain(parts, imports, "app.py")
        assert result.startswith("module-access")

    def test_third_party_module(self) -> None:
        """flask.Flask(__name__).register_blueprint() should be module-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        imports = FileImports()
        imports.module_names.add("flask")
        parts = ["flask", "Flask()", "register_blueprint()"]
        result = classify_chain(parts, imports, "app.py")
        assert result.startswith("module-access")

    def test_aliased_import(self) -> None:
        """np.array().reshape().tolist() should be module-access when np imported."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        imports = FileImports()
        imports.module_names.add("np")
        parts = ["np", "array()", "reshape()", "tolist()"]
        result = classify_chain(parts, imports, "compute.py")
        assert result.startswith("module-access")

    def test_datetime_module(self) -> None:
        """datetime.datetime.now().isoformat() should be module-access."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        imports = FileImports()
        imports.module_names.add("datetime")
        parts = ["datetime", "datetime", "now()", "isoformat()"]
        result = classify_chain(parts, imports, "utils.py")
        assert result.startswith("module-access")

    def test_non_module_not_filtered(self) -> None:
        """Non-module rooted chains should not be caught by this filter."""
        from src.linters.law_of_demeter.chain_classifier import classify_chain

        imports = FileImports()
        parts = ["order", "customer", "address", "city"]
        result = classify_chain(parts, imports, "app.py")
        assert not result.startswith("module-access")
