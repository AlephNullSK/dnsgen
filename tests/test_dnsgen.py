# tests/test_dnsgen.py
import os
from pathlib import Path
from typing import List, Set
import pytest
from dnsgen.dnsgen import DomainGenerator, create_generator


@pytest.fixture
def sample_domains() -> List[str]:
	"""Fixture providing sample domain names for testing."""
	return [
		"api.example.com",
		"dev-api01.test.com",
		"staging-auth.prod.company.com",
		"v2.api.service.org"
	]


@pytest.fixture
def sample_wordlist(tmp_path: Path) -> Path:
	"""Fixture creating a temporary wordlist file."""
	content = """
# Environment
dev
staging
prod

# Services
api
auth
service

# Version
v1
v2
v3
"""
	wordlist_path = tmp_path / "test_wordlist.txt"
	wordlist_path.write_text(content)
	return wordlist_path


@pytest.fixture
def generator(sample_wordlist: Path) -> DomainGenerator:
	"""Fixture providing a configured DomainGenerator instance."""
	return create_generator(sample_wordlist)


def test_partiate_domain(generator: DomainGenerator):
	"""Test domain partitioning functionality."""
	test_cases = [
		("api.example.com", ["api", "example.com"]),
		("dev.api.example.com", ["dev", "api", "example.com"]),
		("test.sub.domain.example.co.uk", ["test", "sub", "domain", "example.co.uk"])
	]

	for domain, expected in test_cases:
		assert generator.partiate_domain(domain) == expected


def test_extract_custom_words(generator: DomainGenerator):
	"""Test custom word extraction from domains."""
	domains = [
		"development-api.example.com",
		"staging-auth.test.com",
		"prod-service.company.com"
	]

	# Test with different word lengths
	assert "development" in generator.extract_custom_words(domains, 6)
	assert "staging" in generator.extract_custom_words(domains, 4)
	assert "api" not in generator.extract_custom_words(domains, 4)  # Too short


def test_word_insertion_permutator(generator: DomainGenerator):
	"""Test word insertion permutation technique."""
	domain = "api.example.com"
	parts = generator.partiate_domain(domain)

	variations = generator.generate([domain])
	variations_list = list(variations)

	# Check some expected variations
	assert "dev.api.example.com" in variations_list
	assert "api.staging.example.com" in variations_list


def test_number_manipulation_permutator(generator: DomainGenerator):
	"""Test number manipulation in domains."""
	domain = "api2.example.com"
	variations = list(generator.generate([domain]))

	# Check number increments and decrements
	assert "api1.example.com" in variations
	assert "api3.example.com" in variations


def test_region_prefix_permutator(generator: DomainGenerator):
	"""Test region prefix permutations."""
	domain = "api.example.com"
	variations = list(generator.generate([domain]))

	# Check region patterns
	assert "us-east.api.example.com" in variations
	assert "eu-west.api.example.com" in variations


def test_fast_mode_generation(generator: DomainGenerator):
	"""Test fast mode generation with fewer permutations."""
	domain = "api.example.com"

	# Compare number of variations between normal and fast mode
	normal_variations = set(generator.generate([domain], fast_mode=False))
	fast_variations = set(generator.generate([domain], fast_mode=True))

	# Fast mode should generate fewer variations
	assert len(fast_variations) < len(normal_variations)


def test_invalid_wordlist_handling():
	"""Test handling of invalid wordlist path."""
	with pytest.raises(FileNotFoundError):
		create_generator("nonexistent_wordlist.txt")


# Integration Tests

def test_full_generation_pipeline(sample_domains: List[str], generator: DomainGenerator):
	"""Integration test for the full generation pipeline."""
	# Test complete pipeline
	variations = list(generator.generate(sample_domains))

	# Basic validation
	assert len(variations) > 0
	assert all(isinstance(domain, str) for domain in variations)
	assert all("." in domain for domain in variations)


# Edge Cases

def test_empty_domain_handling(generator: DomainGenerator):
	"""Test handling of empty domain input."""
	variations = list(generator.generate([]))
	assert len(variations) == 0


def test_special_character_domains(generator: DomainGenerator):
	"""Test handling of domains with special characters."""
	domain = "api-test_01.example.com"
	variations = list(generator.generate([domain]))
	assert len(variations) > 0


def test_very_long_domain(generator: DomainGenerator):
	"""Test handling of very long domain names."""
	long_domain = "a" * 30 + ".example.com"
	variations = list(generator.generate([long_domain]))
	assert len(variations) > 0
	assert all(len(domain) <= 253 for domain in variations)  # DNS max length


# Performance Tests

@pytest.mark.slow
@pytest.mark.integration
def test_large_input_performance(generator: DomainGenerator):
	"""Test performance with large input (marked as slow test)."""
	large_domains = [f"test{i}.example.com" for i in range(100)]
	variations = list(generator.generate(large_domains))
	assert len(variations) > 0