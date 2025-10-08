"""Integration tests for .artifacts directory generation.

Purpose: Verify that generated configs are written to <project_root>/.artifacts/
Scope: Test that .artifacts/ is created at the correct location with correct content
"""

import shutil


class TestArtifactsGeneration:
    """Test that .artifacts directory is generated at project root."""

    def test_artifacts_created_at_project_root_with_rules_flag(self, tmp_path):
        """When using --rules flag, .artifacts/generated-config.yaml should be created at project root."""
        from click.testing import CliRunner

        from src.cli import cli

        # Create a fake project structure
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        (project_root / ".git").mkdir()  # Mark as git repo
        src_dir = project_root / "src"
        src_dir.mkdir()
        test_file = src_dir / "test.py"
        test_file.write_text("print('test')")

        # Remove .artifacts and .ai if they exist
        artifacts_dir = project_root / ".artifacts"
        ai_dir = project_root / ".ai"
        src_artifacts_dir = src_dir / ".artifacts"
        src_ai_dir = src_dir / ".ai"

        for directory in [artifacts_dir, ai_dir, src_artifacts_dir, src_ai_dir]:
            if directory.exists():
                shutil.rmtree(directory)

        # Run linter with --rules flag from src directory
        runner = CliRunner()
        rules_json = '{"global_allow": [{"pattern": ".*\\\\.py$"}]}'
        result = runner.invoke(
            cli, ["file-placement", "--rules", rules_json, str(src_dir)], catch_exceptions=False
        )

        # Should succeed
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check that .artifacts was created at PROJECT ROOT, not in src/
        assert artifacts_dir.exists(), ".artifacts should exist at project root"
        assert not src_artifacts_dir.exists(), ".artifacts should NOT exist in src/"

        # Check that .ai was NEVER created (old location)
        assert not ai_dir.exists(), ".ai should NOT be created at project root"
        assert not src_ai_dir.exists(), ".ai should NOT be created in src/"
        assert not (project_root / ".ai" / "layout.yaml").exists(), (
            ".ai/layout.yaml should NOT be created"
        )
        assert not (src_dir / ".ai" / "layout.yaml").exists(), (
            "src/.ai/layout.yaml should NOT be created"
        )

        # Check the generated config file
        config_file = artifacts_dir / "generated-config.yaml"
        assert config_file.exists(), "generated-config.yaml should exist"

        # Verify content structure
        import yaml

        with config_file.open() as f:
            config = yaml.safe_load(f)

        # Should have file-placement wrapper
        assert "file-placement" in config, "Config should have file-placement key"
        assert "global_allow" in config["file-placement"], "Config should have global_allow"
        assert isinstance(config["file-placement"]["global_allow"], list), (
            "global_allow should be a list"
        )

    def test_artifacts_created_at_project_root_with_config_flag(self, tmp_path):
        """When using --config flag, .artifacts/generated-config.yaml should be created at project root."""
        from click.testing import CliRunner

        from src.cli import cli

        # Create a fake project structure
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        (project_root / ".git").mkdir()  # Mark as git repo
        src_dir = project_root / "src"
        src_dir.mkdir()
        test_file = src_dir / "test.py"
        test_file.write_text("print('test')")

        # Create external config file
        config_file = project_root / "custom-config.yaml"
        config_file.write_text(
            """file-placement:
  global_allow:
    - pattern: '.*\\.py$'
"""
        )

        # Remove .artifacts and .ai if they exist
        artifacts_dir = project_root / ".artifacts"
        ai_dir = project_root / ".ai"
        src_artifacts_dir = src_dir / ".artifacts"
        src_ai_dir = src_dir / ".ai"

        for directory in [artifacts_dir, ai_dir, src_artifacts_dir, src_ai_dir]:
            if directory.exists():
                shutil.rmtree(directory)

        # Run linter with --config flag from src directory
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["file-placement", "--config", str(config_file), str(src_dir)],
            catch_exceptions=False,
        )

        # Should succeed
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Check that .artifacts was created at PROJECT ROOT, not in src/
        assert artifacts_dir.exists(), ".artifacts should exist at project root"
        assert not src_artifacts_dir.exists(), ".artifacts should NOT exist in src/"

        # Check that .ai was NEVER created (old location)
        assert not ai_dir.exists(), ".ai should NOT be created at project root"
        assert not src_ai_dir.exists(), ".ai should NOT be created in src/"
        assert not (project_root / ".ai" / "layout.yaml").exists(), (
            ".ai/layout.yaml should NOT be created"
        )
        assert not (src_dir / ".ai" / "layout.yaml").exists(), (
            "src/.ai/layout.yaml should NOT be created"
        )

        # Check the generated config file
        generated_file = artifacts_dir / "generated-config.yaml"
        assert generated_file.exists(), "generated-config.yaml should exist"

        # Verify content structure
        import yaml

        with generated_file.open() as f:
            config = yaml.safe_load(f)

        # Should have file-placement key with the loaded config
        assert "file-placement" in config, "Config should have file-placement key"
        assert "global_allow" in config["file-placement"], "Config should have global_allow"

    def test_no_artifacts_created_without_rules_or_config_flags(self, tmp_path):
        """When neither --rules nor --config is used, .artifacts should not be created."""
        from click.testing import CliRunner

        from src.cli import cli

        # Create a fake project structure
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        (project_root / ".git").mkdir()  # Mark as git repo
        src_dir = project_root / "src"
        src_dir.mkdir()
        test_file = src_dir / "test.py"
        test_file.write_text("print('test')")

        # Ensure .artifacts doesn't exist
        artifacts_dir = project_root / ".artifacts"
        if artifacts_dir.exists():
            shutil.rmtree(artifacts_dir)

        # Run linter without --rules or --config
        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", str(test_file)], catch_exceptions=False)

        # Should succeed (no violations with defaults)
        assert result.exit_code in [0, 1], f"Command failed: {result.output}"

        # .artifacts should NOT be created
        assert not artifacts_dir.exists(), (
            ".artifacts should not be created without --rules or --config flags"
        )
