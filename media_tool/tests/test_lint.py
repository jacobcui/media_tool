import subprocess
import pytest


def test_black_formatting():
    """Test that black formatting passes"""
    result = subprocess.run(
        ["black", ".", "../"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Black formatting failed:\n{result.stdout}\n{result.stderr}"


def test_flake8_compliance():
    """Test that flake8 passes"""
    result = subprocess.run(
        ["flake8", "."],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Flake8 check failed:\n{result.stdout}\n{result.stderr}"


def test_isort_check():
    """Test that imports are sorted correctly"""
    result = subprocess.run(
        ["isort", ".", "../"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Import sorting check failed:\n{result.stdout}\n{result.stderr}"
