# python3

import itertools
import os
import re

import tldextract

HERE = os.path.abspath(os.path.dirname(__file__))
WORDS = None
NUM_COUNT = 2

def create_registrar():
	registry = []
	def registrar(func):
		registry.append(func)
		return func

	registrar.members = registry
	return registrar

PERMUTATOR = create_registrar()

def partiate_domain(domain):
	'''
	Split domain base on subdomain levels.
	TLD is taken as one part, regardless of its levels (.co.uk, .com, ...)
	'''

	# test.1.foo.example.com -> [test, 1, foo, example, com]
	# test.2.foo.example.com.cn -> [test, 2, foo, example, com.cn]
	# test.example.co.uk -> [test, example, co.uk]

	ext = tldextract.extract(domain.lower())
	parts = (ext.subdomain.split('.') + [ext.domain, ext.suffix])

	return [p for p in parts if p]

@PERMUTATOR
def insert_word_every_index(parts):
	'''
	Create new subdomain levels by inserting the words between existing levels
	'''

	# test.1.foo.example.com -> WORD.test.1.foo.example.com, test.WORD.1.foo.example.com, 
	#                           test.1.WORD.foo.example.com, test.1.foo.WORD.example.com, ...

	domains = []

	for w in WORDS:
		for i in range(len(parts) - 1):
			tmp_parts = parts[:-2]
			tmp_parts.insert(i, w)
			domains.append('{}.{}'.format('.'.join(tmp_parts), '.'.join(parts[-2:])))

	return domains

# TODO: optimize
#@PERMUTATOR
def insert_num_every_index(parts):
	'''
	Create new subdomain levels by inserting the numbers between existing levels
	'''

	# foo.test.example.com ->   1.foo.test.example.com, foo.1.test.example.com, 
	#                           foo.test.1.example.com, 01.foo.test.example.com, ...

	domains = []

	for num in range(NUM_COUNT):
		for i in range(len(parts) - 1):
			# Single digit
			tmp_parts = parts[:-2]
			tmp_parts.insert(i, str(num))
			domains.append('{}.{}'.format('.'.join(tmp_parts), '.'.join(parts[-2:])))

			# Double digit
			tmp_parts = parts[:-2]
			tmp_parts.insert(i, '{:0>2}'.format(num))
			domains.append('{}.{}'.format('.'.join(tmp_parts), '.'.join(parts[-2:])))

	return domains

@PERMUTATOR
def increase_num_found(parts):
	'''
	If number is found in existing subdomain, increase this number without any other alteration
	'''

	# test.1.foo.example.com -> test.2.foo.example.com, test.3.foo.example.com, ...
	# test1.example.com -> test2.example.com, test3.example.com, ...
	# test01.example.com -> test02.example.com, test03.example.com, ...

	domains = []
	parts_joined = '.'.join(parts[:-2])
	digits = re.findall(r'\d{1,3}', parts_joined)

	for d in digits:
		for m in range(NUM_COUNT):
			replacement = str(int(d) + 1 + m).zfill(len(d))
			tmp_domain = parts_joined.replace(d, replacement)
			domains.append('{}.{}'.format(tmp_domain, '.'.join(parts[-2:])))
   
	return domains

@PERMUTATOR
def decrease_num_found(parts):
	'''
	If number is found in existing subdomain, decrease this number without any other alteration
	'''

	# test.4.foo.example.com -> test.3.foo.example.com, test.2.foo.example.com, ...
	# test4.example.com -> test3.example.com, test2.example.com, ...
	# test04.example.com -> test03.example.com, test02.example.com, ...

	domains = []
	parts_joined = '.'.join(parts[:-2])
	digits = re.findall(r'\d{1,3}', parts_joined)

	for d in digits:
		for m in range(NUM_COUNT):
			new_digit = (int(d) - 1 - m)
			if new_digit < 0:
				break

			replacement = str(new_digit).zfill(len(d))
			tmp_domain = parts_joined.replace(d, replacement)
			domains.append('{}.{}'.format(tmp_domain, '.'.join(parts[-2:])))
   
	return domains

@PERMUTATOR
def prepend_word_every_index(parts):
	'''
	On every subdomain level, prepend existing content with `WORD` and `WORD-`
	'''

	# test.1.foo.example.com -> WORDtest.1.foo.example.com, test.WORD1.foo.example.com, 
	#                           test.1.WORDfoo.example.com, WORD-test.1.foo.example.com, 
	#                           test.WORD-1.foo.example.com, test.1.WORD-foo.example.com, ...

	domains = []

	for w in WORDS:
		for i in range(len(parts[:-2])):
			# prepend normal
			tmp_parts = parts[:-2]
			tmp_parts[i] = '{}{}'.format(w, tmp_parts[i])
			domains.append('{}.{}'.format('.'.join(tmp_parts), '.'.join(parts[-2:])))

			# prepend with dash
			tmp_parts = parts[:-2]
			tmp_parts[i] = '{}-{}'.format(w, tmp_parts[i])
			domains.append('{}.{}'.format('.'.join(tmp_parts), '.'.join(parts[-2:])))     

	return domains

@PERMUTATOR
def append_word_every_index(parts):
	'''
	On every subdomain level, append existing content with `WORD` and `WORD-`
	'''

	# test.1.foo.example.com -> testWORD.1.foo.example.com, test.1WORD.foo.example.com, 
	#                           test.1.fooWORD.example.com, test-WORD.1.foo.example.com, 
	#                           test.1-WORD.foo.example.com, test.1.foo-WORD.example.com, ...

	domains = []

	for w in WORDS:
		for i in range(len(parts[:-2])):
			# Append normal
			tmp_parts = parts[:-2]
			tmp_parts[i] = '{}{}'.format(tmp_parts[i], w)
			domains.append('{}.{}'.format('.'.join(tmp_parts), '.'.join(parts[-2:])))

			# Append with dash
			tmp_parts = parts[:-2]
			tmp_parts[i] = '{}-{}'.format(tmp_parts[i], w)
			domains.append('{}.{}'.format('.'.join(tmp_parts), '.'.join(parts[-2:])))

	return domains

@PERMUTATOR
def replace_word_with_word(parts):
	'''
	If word longer than 3 is found in existing subdomain, replace it with other words from the dictionary
	'''

	# WORD1.1.foo.example.com -> WORD2.1.foo.example.com, WORD3.1.foo.example.com, 
	#                            WORD4.1.foo.example.com, ...

	domains = []

	for w in WORDS:
		if len(w) <= 3:
			continue

		if w in '.'.join(parts[:-2]):
			for w_alt in WORDS:
				if w == w_alt:
					continue

				domains.append('{}.{}'.format('.'.join(parts[:-2]).replace(w, w_alt), '.'.join(parts[-2:])))

	return domains

def extract_custom_words(domains, wordlen):
	'''
	Extend the dictionary based on target's domain naming conventions
	'''

	valid_tokens = set()

	for domain in domains:
		partition = partiate_domain(domain)[:-2]
		tokens = set(itertools.chain(*[word.lower().split('-') for word in partition]))
		tokens = tokens.union({word.lower() for word in partition})
		for t in tokens:
			# delete all numbers
			t = re.sub(r'\d', '', t)

			if len(t) >= wordlen:
				valid_tokens.add(t)

	return list(valid_tokens)

def generate(domains, wordlist=None, wordlen=6, fast=False):
	# generate_markov_matrix()
	global WORDS

	if wordlist is None:
		WORDS = open(os.path.join(HERE, 'words.txt')).read().splitlines()
	else:
		WORDS = open(wordlist).read().splitlines()

	if fast:
		WORDS = WORDS[:10]
	
	WORDS += extract_custom_words(domains, wordlen)
	WORDS = list(set(WORDS))

	for domain in set(domains):
		parts = partiate_domain(domain)

		for perm in PERMUTATOR.members:
			for possible_domain in perm(parts):
				yield possible_domain
