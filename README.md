# :cyclone: dnsgen (DNS generator)

This tool generates a combination of domain names from the provided input. Combinations are created based on wordlist. Custom words are extracted per execution. Refer to [Techniques](#techniques) section to learn more.

`dnsgen` is very similar to [altdns](https://github.com/infosec-au/altdns). It does not contain DNS resolver. You should use [massdns](https://github.com/blechschmidt/massdns) for DNS resolution.

![dnsgen](https://0xpatrik.com/content/images/2019/09/dnsgen-1.png)

## Installation

```python -m pip install dnsgen```

..or from GitHub directly:

```
git clone https://github.com/AlephNullSK/dnsgen
cd dnsgen/
python -m poetry install
```

## Usage

```$ dnsgen domains.txt``` (`domains.txt` contains a list of active domain names)

* `-l` / `--wordlen`: minimum size of custom words to be extracted
* `-w` / `--wordlist`: path to custom wordlist
* `-f` / `--fast`: Generate lower amount of domains with most probable words only
* `-o`, `--output`: Store results to the output file.
* `filename`: required parameter for an input list of domains. The input file should contain domain names separated by newline character (`\n`). You can also use STDIN as an input method, providing `-` to this argument.

**Combination with massdns:**

```
$ cat domains.txt | dnsgen - | massdns -r /path/to/resolvers.txt -t A -o J --flush 2>/dev/null
```

**Get only resolved domains with massdns**:

```
$ dnsgen hosts.txt >> dnsgen_wordlist.txt
$ massdns -r ~/tools/massdns/lists/resolvers.txt -o S dnsgen_wordlist.txt | grep -e ' A ' | cut -d 'A' -f 1 | rev | cut -d "." -f1 --complement | rev | sort | uniq  > dnsgen_massdns_resolved
```

these will generate a file with domains without "text polution".

## Techniques

*(For demo purposes, let's say that wordlist contains just one word: `stage`)*

* **Insert word on every index** — Creates new subdomain levels by inserting the words between existing levels. `foo.example.com` -> `stage.foo.example.com`, `foo.stage.example.com`

* **Increase/Decrease num found** — *(In development)* If number is found in an existing subdomain, increase/decrease this number without any other alteration. `foo01.example.com` -> `foo02.example.com`, `foo03.example.com`, `...`

* **Prepend word on every index** — On every subdomain level, prepend existing content with `WORD` and `WORD-`. `foo.example.com` -> `stagefoo.example.com`, `stage-foo.example.com`

* **Append word on every index** — On every subdomain level, append existing content with `WORD` and `WORD-`. `foo.example.com` -> `foostage.example.com`, `foo-stage.example.com`

* **Replace the word with word** — If word longer than 3 is found in an existing subdomain, replace it with other words from the wordlist. *(If we have more words than one in our wordlist)*. `stage.foo.example.com` -> `otherword.foo.example.com`, `anotherword.foo.example.com`, `...`

* **Extract custom words** — Extend the wordlist based on target's domain naming conventions. Such words are either whole subdomain levels, or `-` is used for a split on some subdomain level. For instance `mapp1-current.datastream.example.com` has `mapp1`, `current`, `datastream` words. To prevent the overflow, user-defined *word length* is used for word extraction. The default value is set to **6**. This means that only words strictly longer than **5** characters are included (from the previous example, `mapp1` does not satisfy this condition). 

## Resources

- [Subdomain Enumeration: 2019 Workflow](https://0xpatrik.com/subdomain-enumeration-2019/)
- [Subdomain Enumeration: Doing it a Bit Smarter](https://0xpatrik.com/subdomain-enumeration-smarter/)

## TO DO

- Improve README
- Tests

## Author

[Aleph Null s.r.o.](https://alephnull.sk)
