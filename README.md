# :cyclone: dnsgen (DNS generator)

This tools generates combination of domains names from the provided input. Combinations are created based on wordlist. Custom words are extracted per execution. Refer to `Techniques` section to learn more.

`dnsgen` is very similar to [altdns](https://github.com/infosec-au/altdns). It does not contain DNS resolver. You should use [massdns](https://github.com/blechschmidt/massdns) for DNS resolution.

## Installation

```pip3 install dnsgen```

..or from GitHub:

```
git clone https://github.com/ProjectAnte/dnsgen
cd dnsgen
pip3 install -r requirements.txt
python3 setup.py install
```

## Usage

```$ dnsgen domains.txt``` (`domains.txt` contains list of active domain names)

* `-l` / `--wordlen`: minimum size of custom words to be extracted
* `-w` / `--wordlist`: path to custom wordlist
* `filename`: required parameter for input list of domains. `-` stands for STDIN

**Combination with massdns:**

`$ cat domains.txt | dnsgen - | massdns -r /path/to/resolvers.txt -t A -o J --flush 2>/dev/null`

## Techniques

*(For demo purposes, let's say that wordlist contains just one word: `stage`)*

* **Insert word on every index** — Creates new subdomain levels by inserting the words between existing levels. `foo.example.com` -> `stage.foo.example.com`, `foo.stage.example.com`

* **Insert num on every index** — Creates new subdomain levels by inserting the numbers between existing levels. `foo.bar.example.com` -> `1.foo.bar.example.com`, `foo.1.bar.example.com`, `01.foo.bar.example.com`, `...`

* **Increase/Decrease num found** — If number is found in an existing subdomain, increase/decrease this number without any other alteration. `foo01.example.com` -> `foo02.example.com`, `foo03.example.com`, `...`

* **Prepend word on every index** — On every subdomain level, prepend existing content with `WORD` and `WORD-`. `foo.example.com` -> `stagefoo.example.com`, `stage-foo.example.com`

* **Append word on every index** — On every subdomain level, append existing content with `WORD` and `WORD-`. `foo.example.com` -> `foostage.example.com`, `foo-stage.example.com`

* **Replace word with word** — If word longer than 3 is found in existing subdomain, replace it with other words from the wordlist. *(If we have more words than one in our wordlist)*. `stage.foo.example.com` -> `otherword.foo.example.com`, `anotherword.foo.example.com`, `...`

* **Extract custom words** — Extend the wordlist based on target's domain naming conventions. Such words are either whole subdomain levels, or `-` is used for split on some subdomain level. For instance `mapp1-current.datastream.example.com` has `mapp1`, `current`, `datastream` words. To prevent the overflow, user defined *word length* is used for word extraction. The default value is set to **6**. This means that only words strictly longer than **5** characters are included (from the previous example, `mapp1` does not satisfy this condition). 

## Resources

- [Subdomain Enumeration: 2019 Workflow](https://0xpatrik.com/subdomain-enumeration-2019/)
- [Subdomain Enumeration: Doing it a Bit Smarter](https://0xpatrik.com)

## TO DO

- Improve README
- Tests