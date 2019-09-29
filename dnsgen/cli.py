# python3

import os
import sys

import click

from . import dnsgen

@click.command()
@click.option('-l', '--wordlen', default=6, help='Min length of custom words extracted from domains.', required=False, type=click.IntRange(1, 100))
@click.option('-w', '--wordlist', default=None, help='Path to custom wordlist.', type=click.Path(exists=True, readable=True), required=False)
@click.argument('filename', required=True, type=click.File(mode='r'))
def main(wordlen, wordlist, filename):
    # read the input
    domains = filename.read().splitlines()

    for r in dnsgen.generate(domains, wordlist, wordlen):
        print(r)
