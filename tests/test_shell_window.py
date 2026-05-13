from app.ui.dialogs.shell_window import DANGEROUS_PATTERNS


def test_dangerous_shell_patterns_include_destructive_commands() -> None:
    patterns = set(DANGEROUS_PATTERNS)
    assert "pm uninstall" in patterns
    assert "settings put" in patterns
    assert "rm -rf" in patterns
    assert "su" in patterns
