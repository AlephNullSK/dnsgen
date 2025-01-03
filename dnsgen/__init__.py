"""
DNSGen - DNS name permutation generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A tool for generating DNS name variations for domain discovery and security testing.

Basic usage:
    >>> from dnsgen import DomainGenerator, create_generator
    >>> generator = create_generator()
    >>> domains = ["api.example.com"]
    >>> variations = list(generator.generate(domains))

The package provides several ways to generate domain variations:
1. Using the DomainGenerator class directly
2. Using the create_generator factory function
3. Using the generate convenience function for simple cases
"""

from typing import List, Iterator, Optional
import warnings

from .dnsgen import (
    DomainGenerator,
    create_generator,
    DomainPartsType,
    PermutatorFunc,
)

__author__ = "Aleph Null s.r.o."
__all__ = [
    "DomainGenerator",
    "create_generator",
    "generate",
    "DomainPartsType",
    "PermutatorFunc",
]


def generate(
        domains: List[str],
        wordlist_path: Optional[str] = None,
        wordlen: int = 5,
        fast_mode: bool = False,
) -> Iterator[str]:
    """
    Convenience function to generate domain variations without explicit generator creation.

    Args:
        domains: List of domain names to generate variations from
        wordlist_path: Optional path to custom wordlist file
        wordlen: Minimum length for custom word extraction
        fast_mode: Whether to use fast generation mode

    Returns:
        Iterator yielding generated domain variations

    Examples:
        >>> from dnsgen import generate
        >>> domains = ["api.example.com"]
        >>> variations = list(generate(domains))

        # With custom wordlist and options
        >>> variations = list(generate(
        ...     domains,
        ...     wordlist_path="custom_words.txt",
        ...     wordlen=4,
        ...     fast_mode=True
        ... ))
    """
    generator = create_generator(wordlist_path)
    yield from generator.generate(domains, wordlen=wordlen, fast_mode=fast_mode)


# Version compatibility check
import sys

if sys.version_info < (3, 7):
    warnings.warn(
        "DNSGen requires Python 3.7 or higher for full functionality. "
        "Some features may not work correctly.",
        RuntimeWarning
    )

# Type checking availability notification
try:
    from typing import Protocol

    TYPING_EXTENSIONS_AVAILABLE = True
except ImportError:
    TYPING_EXTENSIONS_AVAILABLE = False
    warnings.warn(
        "typing_extensions not found. Type checking capabilities will be limited.",
        ImportWarning
    )