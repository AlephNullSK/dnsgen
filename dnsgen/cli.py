# python3

import os
import sys
import click

from . import dnsgen

@click.command()
@click.option('-l', '--wordlen', default=6,
                help='Min length of custom words extracted from domains.',
                required=False, type=click.IntRange(1, 100))
@click.option('-w', '--wordlist', default=None, help='Path to custom wordlist.',
                type=click.Path(exists=True, readable=True), required=False)
@click.option('-f', '--fast', default=None, help='Fast generation.',
                is_flag=True, required=False)
@click.option('-o', '--output', default=None, help='Output file.', required=False)
@click.argument('filename', required=True, type=click.File(mode='r'))

def main(wordlen, wordlist, filename, fast, output):
    # read the input
    domains = filename.read().splitlines()

    # store output
    generated = []

    # generate domains
    for r in dnsgen.generate(domains, wordlist, wordlen, fast=fast):
        # ensure unique domains
        if r not in domains:
            generated.append(r)

    # echo output
    for domain in generated:
        click.echo(domain)

    # write to output file
    if output:
       with open(output, 'w') as f:
           for domain in generated:
               f.write("%s\n" % domain)