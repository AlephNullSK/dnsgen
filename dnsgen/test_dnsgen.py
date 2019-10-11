
import unittest
import tldextract

import dnsgen


# domain = "....."
# domain = ".?@#3.fde!.@.qweqw"
# domain = "1.?@#3.fde!.@.qweqw"
# domain = "www.letter.com.cn"

# def partiate_domain(domain):
# 	'''
# 	Split domain base on subdomain levels.
# 	TLD is taken as one part, regardless of its levels (.co.uk, .com, ...)
# 	'''

# 	# test.1.foo.example.com -> [test, 1, foo, example, com]
# 	# test.2.foo.example.com.cn -> [test, 2, foo, example, com.cn]
# 	# test.example.co.uk -> [test, example, co.uk]

# 	ext = tldextract.extract(domain.lower())
# 	parts = (ext.subdomain.split('.') + [ext.domain, ext.suffix])

# 	return [p for p in parts if p]
	
# print(partiate_domain(domain))


class Test_PartiateDomain(unittest.TestCase):
    def test_generalDomains(self):
    	self.assertEqual(dnsgen.partiate_domain("test.1.foo.example.com"),['test', '1', 'foo', 'example', 'com'])
    	self.assertEqual(dnsgen.partiate_domain("test.2.foo.example.com.cn"),['test', '2', 'foo', 'example', 'com.cn'])
    	self.assertEqual(dnsgen.partiate_domain("test.example.co.uk"),['test', 'example', 'co.uk'])

    def test_websiteDomains(self):
        self.assertEqual(dnsgen.partiate_domain("https://www.google.com"),['www', 'google', 'com'])
        self.assertEqual(dnsgen.partiate_domain("www.letter.com.1.cn"),['www','letter', 'com', '1','cn'])
        self.assertEqual(dnsgen.partiate_domain(".test.com.1."),['test', 'com', '1'])
        self.assertEqual(dnsgen.partiate_domain(".test.com.1.c.a/b"),['test', 'com', '1','c','a'])

    def test_specialCharDomains(self):
        self.assertEqual(dnsgen.partiate_domain("....."),[])
        self.assertEqual(dnsgen.partiate_domain(".?@#3.fde!.@.qwepo"),[])
        self.assertEqual(dnsgen.partiate_domain("1.?@#3.fde!.@.qwetg"),['1'])
        self.assertEqual(dnsgen.partiate_domain("test.?@#3.fde!.@.qwedg"),['test'])
        self.assertEqual(dnsgen.partiate_domain(".1...."),['1'])
        self.assertEqual(dnsgen.partiate_domain(".1../..c.."),['1'])


if __name__ == '__main__':
    unittest.main()


