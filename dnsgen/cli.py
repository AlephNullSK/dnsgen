#!/usr/bin/env python3
"""
DNSGen - DNS name permutation generator CLI.
Generates variations of domain names for discovery and security testing.
"""

import logging
import sys
from pathlib import Path
from typing import TextIO, Set, Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import dnsgen

# Configure logging with rich
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger("dnsgen")
console = Console()


def validate_wordlen(ctx: click.Context, param: click.Parameter, value: int) -> int:
    """Validate the word length parameter."""
    if value < 1 or value > 100:
        raise click.BadParameter("Word length must be between 1 and 100")
    return value


def setup_generator(wordlist: Optional[Path], wordlen: int, fast: bool) -> dnsgen.DomainGenerator:
    """
    Set up and configure the domain generator.

    Args:
        wordlist: Optional path to custom wordlist
        wordlen: Minimum length for word extraction
        fast: Whether to use fast generation mode

    Returns:
        Configured DomainGenerator instance
    """
    try:
        generator = dnsgen.create_generator(str(wordlist) if wordlist else None)
        logger.info("Generator initialized successfully")
        return generator
    except Exception as e:
        logger.error(f"Failed to initialize generator: {e}")
        sys.exit(1)


def process_domains(domains: Set[str], generator: dnsgen.DomainGenerator, wordlen: int, fast: bool) -> Set[str]:
    """
    Process input domains and generate variations.

    Args:
        domains: Set of input domains
        generator: Configured DomainGenerator instance
        wordlen: Minimum length for word extraction
        fast: Whether to use fast generation mode

    Returns:
        Set of generated domain variations
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating domain variations...", total=None)

        try:
            generated = set(generator.generate(list(domains), wordlen=wordlen, fast_mode=fast))
            progress.update(task, completed=True)
            return generated
        except Exception as e:
            logger.error(f"Error during domain generation: {e}")
            sys.exit(1)


def write_output(domains: Set[str], output_file: Optional[Path]) -> None:
    """
    Write generated domains to output file or stdout.

    Args:
        domains: Set of generated domains
        output_file: Optional path to output file
    """
    try:
        if output_file:
            with output_file.open("w") as f:
                for domain in sorted(domains):
                    f.write(f"{domain}\n")
            logger.info(f"Results written to {output_file}")
        else:
            for domain in sorted(domains):
                click.echo(domain)
    except Exception as e:
        logger.error(f"Error writing output: {e}")
        sys.exit(1)


@click.command(help="Generate DNS name permutations for domain discovery.")
@click.option(
    "-l",
    "--wordlen",
    default=6,
    help="Minimum length of custom words extracted from domains.",
    callback=validate_wordlen,
    show_default=True,
    type=int,
)
@click.option(
    "-w",
    "--wordlist",
    help="Path to custom wordlist file.",
    type=click.Path(exists=True, readable=True, path_type=Path),
)
@click.option(
    "-f",
    "--fast",
    is_flag=True,
    help="Use fast generation mode (fewer permutations).",
)
@click.option(
    "-o",
    "--output",
    help="Output file path.",
    type=click.Path(writable=True, path_type=Path),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose logging.",
)
@click.argument(
    "input_file",
    type=click.File(mode="r"),
)
def main(
    wordlen: int,
    wordlist: Optional[Path],
    input_file: TextIO,
    fast: bool,
    output: Optional[Path],
    verbose: bool,
) -> None:
    """
    DNSGen CLI main function.

    Reads domains from input file, generates variations, and outputs results.
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    # Read input domains
    try:
        input_domains = {line.strip() for line in input_file if line.strip()}
        logger.info(f"Read {len(input_domains)} domains from input file")
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        sys.exit(1)

    # Setup generator and process domains
    generator = setup_generator(wordlist, wordlen, fast)
    generated_domains = process_domains(input_domains, generator, wordlen, fast)

    # Output results
    logger.info(f"Generated {len(generated_domains)} unique domain variations")
    write_output(generated_domains, output)


if __name__ == "__main__":
    main()
