# tests/test_cli.py
import os
from pathlib import Path
from click.testing import CliRunner
import pytest
from dnsgen.cli import main


@pytest.fixture
def runner():
	"""Fixture providing a Click CLI test runner."""
	return CliRunner()


@pytest.fixture
def input_file(tmp_path: Path) -> Path:
	"""Fixture creating a temporary input file with domain names."""
	content = """
api.example.com
dev.test.com
staging.company.com
"""
	input_path = tmp_path / "input_domains.txt"
	input_path.write_text(content.strip())
	return input_path


@pytest.fixture
def wordlist_file(tmp_path: Path) -> Path:
	"""Fixture creating a temporary wordlist file."""
	content = """
# Test wordlist
dev
staging
prod
api
"""
	wordlist_path = tmp_path / "test_wordlist.txt"
	wordlist_path.write_text(content)
	return wordlist_path


def test_basic_cli_execution(runner: CliRunner, input_file: Path):
	"""Test basic CLI execution with minimal arguments."""
	result = runner.invoke(main, [str(input_file)])
	assert result.exit_code == 0
	assert len(result.output.splitlines()) > 0


def test_cli_with_wordlist(runner: CliRunner, input_file: Path, wordlist_file: Path):
	"""Test CLI execution with custom wordlist."""
	result = runner.invoke(main, [
		'-w', str(wordlist_file),
		str(input_file)
	])
	assert result.exit_code == 0
	assert len(result.output.splitlines()) > 0


def test_cli_with_output_file(runner: CliRunner, input_file: Path, tmp_path: Path):
	"""Test CLI execution with output file."""
	output_file = tmp_path / "output.txt"
	result = runner.invoke(main, [
		'-o', str(output_file),
		str(input_file)
	])
	assert result.exit_code == 0
	assert output_file.exists()
	assert len(output_file.read_text().splitlines()) > 0


def test_cli_fast_mode(runner: CliRunner, input_file: Path):
	"""Test CLI execution in fast mode."""
	result = runner.invoke(main, [
		'-f',
		str(input_file)
	])
	assert result.exit_code == 0
	assert len(result.output.splitlines()) > 0


def test_cli_invalid_input_file(runner: CliRunner):
	"""Test CLI handling of nonexistent input file."""
	result = runner.invoke(main, ['nonexistent.txt'])
	assert result.exit_code != 0
	assert "Error" in result.output


def test_cli_invalid_wordlist(runner: CliRunner, input_file: Path):
	"""Test CLI handling of nonexistent wordlist."""
	result = runner.invoke(main, [
		'-w', 'nonexistent_wordlist.txt',
		str(input_file)
	])
	assert result.exit_code != 0
	assert "Error" in result.output


def test_cli_invalid_wordlen(runner: CliRunner, input_file: Path):
	"""Test CLI handling of invalid word length."""
	result = runner.invoke(main, [
		'-l', '0',  # Invalid length
		str(input_file)
	])
	assert result.exit_code != 0
	assert "Error" in result.output


def test_cli_stdin_input(runner: CliRunner):
	"""Test CLI handling of stdin input."""
	input_data = "api.example.com\ndev.test.com\n"
	result = runner.invoke(main, ['-'], input=input_data)
	assert result.exit_code == 0
	assert len(result.output.splitlines()) > 0


@pytest.mark.slow
def test_cli_large_input(runner: CliRunner, tmp_path: Path):
	"""Test CLI handling of large input (marked as slow test)."""
	# Create large input file
	input_file = tmp_path / "large_input.txt"
	domains = [f"test{i}.example.com\n" for i in range(100)]
	input_file.write_text("".join(domains))

	result = runner.invoke(main, [str(input_file)])
	assert result.exit_code == 0
	assert len(result.output.splitlines()) > 0
