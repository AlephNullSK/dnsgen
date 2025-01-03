# coding=utf-8
from __future__ import annotations

import itertools
import pathlib
from typing import Callable, List, Set, Iterator, Optional
from dataclasses import dataclass
import re

import tldextract
from tldextract.tldextract import ExtractResult

# Type aliases
DomainPartsType = List[str]
PermutatorFunc = Callable[[DomainPartsType], List[str]]

from dataclasses import field


@dataclass
class DomainGenerator:
    """Main class for handling domain name permutations."""

    words: List[str]
    num_count: int = 3
    permutators: List[PermutatorFunc] = field(default_factory=list)
    fast_permutators: List[PermutatorFunc] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize permutator registries."""
        if self.permutators is None:
            self.permutators = []
        if self.fast_permutators is None:
            self.fast_permutators = []

    def register_permutator(self, fast: bool = False) -> Callable[[PermutatorFunc], PermutatorFunc]:
        """
        Decorator to register domain permutation functions.

        Args:
            fast: If True, the permutator is registered for fast generation mode

        Returns:
            Decorator function that registers the permutator
        """

        def decorator(func: PermutatorFunc) -> PermutatorFunc:
            if fast:
                self.fast_permutators.append(func)
            self.permutators.append(func)
            return func

        return decorator

    def partiate_domain(self, domain: str) -> DomainPartsType:
        """
        Split domain based on subdomain levels.
        Root+TLD is taken as one part, regardless of its levels.

        Args:
            domain: Domain name to split

        Returns:
            List of domain parts

        Example:
            >>> partiate_domain("test.1.foo.example.com")
            ['test', '1', 'foo', 'example.com']
        """
        ext: ExtractResult = tldextract.extract(domain.lower())
        parts: DomainPartsType = ext.subdomain.split(".") + [ext.registered_domain]
        return parts

    def extract_custom_words(self, domains: List[str], wordlen: int) -> Set[str]:
        """
        Extract custom words from domain names based on naming conventions.

        Args:
            domains: List of domain names to analyze
            wordlen: Minimum length of words to extract

        Returns:
            Set of extracted words meeting the length criterion
        """
        valid_tokens: Set[str] = set()

        for domain in domains:
            partition = self.partiate_domain(domain)[:-1]
            tokens = set(itertools.chain(*[word.lower().split("-") for word in partition]))
            tokens = tokens.union({word.lower() for word in partition})
            valid_tokens.update({t for t in tokens if len(t) >= wordlen})

        return valid_tokens

    @property
    def active_permutators(self) -> List[PermutatorFunc]:
        """Get the list of currently active permutators."""
        return self.fast_permutators if self.fast_mode else self.permutators

    def generate(self, domains: List[str], wordlen: int = 5,
                 fast_mode: bool = False) -> Iterator[str]:
        """
        Generate domain permutations from provided domains.

        Args:
            domains: List of base domains to permutate
            wordlen: Minimum length for custom word extraction
            fast_mode: If True, use only fast permutators

        Yields:
            Generated domain variations
        """
        self.fast_mode = fast_mode

        for domain in set(domains):
            parts = self.partiate_domain(domain)
            for permutator in self.active_permutators:
                yield from permutator(parts)


def create_generator(wordlist_path: Optional[str | pathlib.Path] = None) -> DomainGenerator:
    """
    Create and initialize a DomainGenerator instance.

    Args:
        wordlist_path: Optional path to custom wordlist file

    Returns:
        Configured DomainGenerator instance
    """
    if wordlist_path is None:
        wordlist_path = pathlib.Path(__file__).parent / "words.txt"

    # Convert to Path object if string
    if isinstance(wordlist_path, str):
        wordlist_path = pathlib.Path(wordlist_path)

    with open(wordlist_path) as f:
        # Filter out comments (lines starting with #) and empty lines
        lines = f.read().splitlines()
        # Filter out comments and empty lines
        words = [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith('#')
        ]

    generator = DomainGenerator(words=words)

    # Register permutators
    @generator.register_permutator()
    def insert_word_every_index(parts: DomainPartsType) -> List[str]:
        """
        Insert words between existing domain levels.

        Example:
            Input:  "api.example.com"
            Output: "staging.api.example.com"
                   "api.staging.example.com"
                   "admin.api.example.com"
                   "api.admin.example.com"
        """
        domains = []
        for w in generator.words:
            for i in range(len(parts)):
                tmp_parts = parts[:-1]
                tmp_parts.insert(i, w)
                domains.append(".".join(tmp_parts + [parts[-1]]))
        return domains

    @generator.register_permutator(fast=True)
    def modify_numbers(parts: DomainPartsType) -> List[str]:
        """
        Increase and decrease numbers found in domain parts.

        Example:
            Input:  "api2.example.com"
            Output: "api1.example.com"
                   "api3.example.com"
                   "api4.example.com"

            Input:  "v2.api.example.com"
            Output: "v1.api.example.com"
                   "v3.api.example.com"
                   "v4.api.example.com"
        """
        domains = []
        parts_joined = ".".join(parts[:-1])
        digits = re.findall(r"\d{1,3}", parts_joined)

        for d in digits:
            # Increase numbers
            for m in range(generator.num_count):
                replacement = str(int(d) + 1 + m).zfill(len(d))
                tmp_domain = parts_joined.replace(d, replacement)
                domains.append(f"{tmp_domain}.{parts[-1]}")

            # Decrease numbers
            for m in range(generator.num_count):
                new_digit = int(d) - 1 - m
                if new_digit >= 0:
                    replacement = str(new_digit).zfill(len(d))
                    tmp_domain = parts_joined.replace(d, replacement)
                    domains.append(f"{tmp_domain}.{parts[-1]}")

        return domains

    @generator.register_permutator()
    def environment_prefix(parts: DomainPartsType) -> List[str]:
        """
        Add common environment prefixes to domain parts.

        Example:
            Input:  "api.example.com"
            Output: "dev.api.example.com"
                   "staging.api.example.com"
                   "uat.api.example.com"
                   "prod.api.example.com"
                   "test.api.example.com"
        """
        environments = ['dev', 'staging', 'uat', 'prod', 'test']
        domains = []

        for env in environments:
            tmp_parts = parts[:-1]
            tmp_parts.insert(0, env)
            domains.append(".".join(tmp_parts + [parts[-1]]))

        return domains

    @generator.register_permutator()
    def cloud_provider_additions(parts: DomainPartsType) -> List[str]:
        """
        Add common cloud provider related subdomains.

        Example:
            Input:  "example.com"
            Output: "api-aws.example.com"
                   "cdn-aws.example.com"
                   "storage-aws.example.com"
                   "api-azure.example.com"
                   "cdn-azure.example.com"
                   "storage-azure.example.com"
                   "api-gcp.example.com"
                   ...
        """
        cloud_terms = ['aws', 'azure', 'gcp', 'k8s', 'cloud']
        service_terms = ['api', 'cdn', 'storage', 'auth', 'db']

        domains = []
        for term in cloud_terms:
            for service in service_terms:
                tmp_parts = parts[:-1]
                tmp_parts.insert(0, f"{service}-{term}")
                domains.append(".".join(tmp_parts + [parts[-1]]))

        return domains

    @generator.register_permutator()
    def region_prefixes(parts: DomainPartsType) -> List[str]:
        """
        Add common region/location prefixes to domain parts.

        Example:
            Input:  "api.example.com"
            Output: "us-east.api.example.com"
                   "us-west.api.example.com"
                   "eu-west.api.example.com"
                   "ap-south.api.example.com"
                   "eu-central.api.example.com"
        """
        regions = [
            'us-east', 'us-west', 'eu-west', 'eu-central',
            'ap-south', 'ap-northeast', 'sa-east', 'af-south'
        ]
        domains = []

        for region in regions:
            tmp_parts = parts[:-1]
            tmp_parts.insert(0, region)
            domains.append(".".join(tmp_parts + [parts[-1]]))

        return domains

    @generator.register_permutator()
    def microservice_patterns(parts: DomainPartsType) -> List[str]:
        """
        Add common microservice naming patterns.

        Example:
            Input:  "example.com"
            Output: "auth-service.example.com"
                   "user-service.example.com"
                   "payment-svc.example.com"
                   "notification-svc.example.com"
                   "auth-api.example.com"
                   "user-api.example.com"
        """
        services = ['auth', 'user', 'payment', 'notification', 'order', 'inventory']
        suffixes = ['service', 'svc', 'api', 'app']
        domains = []

        for service in services:
            for suffix in suffixes:
                tmp_parts = parts[:-1]
                tmp_parts.insert(0, f"{service}-{suffix}")
                domains.append(".".join(tmp_parts + [parts[-1]]))

        return domains

    @generator.register_permutator()
    def internal_tooling(parts: DomainPartsType) -> List[str]:
        """
        Add common internal tool and platform subdomains.

        Example:
            Input:  "example.com"
            Output: "jenkins.internal.example.com"
                   "gitlab.internal.example.com"
                   "monitoring.internal.example.com"
                   "jenkins.tools.example.com"
                   "gitlab.tools.example.com"
                   "monitoring.tools.example.com"
        """
        tools = ['jenkins', 'gitlab', 'grafana', 'kibana', 'prometheus', 'monitoring', 'jira']
        prefixes = ['internal', 'tools', 'admin']
        domains = []

        for tool in tools:
            for prefix in prefixes:
                tmp_parts = parts[:-1]
                tmp_parts.extend([prefix, tool])
                domains.append(".".join(tmp_parts + [parts[-1]]))
                # Also try tool first, then prefix
                tmp_parts = parts[:-1]
                tmp_parts.extend([tool, prefix])
                domains.append(".".join(tmp_parts + [parts[-1]]))

        return domains

    @generator.register_permutator(fast=True)
    def common_ports(parts: DomainPartsType) -> List[str]:
        """
        Add common port numbers as prefixes.

        Example:
            Input:  "api.example.com"
            Output: "8080.api.example.com"
                   "8443.api.example.com"
                   "3000.api.example.com"
                   "port-8080.api.example.com"
                   "port-8443.api.example.com"
        """
        ports = ['8080', '8443', '3000', '5000', '9000', '8888']
        domains = []

        for port in ports:
            # Add port directly as subdomain
            tmp_parts = parts[:-1]
            tmp_parts.insert(0, port)
            domains.append(".".join(tmp_parts + [parts[-1]]))

            # Add with 'port-' prefix
            tmp_parts = parts[:-1]
            tmp_parts.insert(0, f"port-{port}")
            domains.append(".".join(tmp_parts + [parts[-1]]))

        return domains

    return generator