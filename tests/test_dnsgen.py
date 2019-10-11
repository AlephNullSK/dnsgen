
import unittest
import dnsgen

class Test_PartiateDomain(unittest.TestCase):
	# Test cases for valid domain names
    def test_generalDomains(self):
    	self.assertEqual(dnsgen.partiate_domain("test.1.foo.example.com"),['test', '1', 'foo', 'example', 'com'])
    	self.assertEqual(dnsgen.partiate_domain("test.2.foo.example.com.cn"),['test', '2', 'foo', 'example', 'com.cn'])
    	self.assertEqual(dnsgen.partiate_domain("test.example.co.uk"),['test', 'example', 'co.uk'])

	# Test cases for domain names with special characters
    def test_websiteDomains(self):
        self.assertEqual(dnsgen.partiate_domain("https://www.google.com"),['www', 'google', 'com'])
        self.assertEqual(dnsgen.partiate_domain("www.letter.com.1.cn"),['www','letter', 'com', '1','cn'])
        self.assertEqual(dnsgen.partiate_domain(".test.com.1."),['test', 'com', '1'])
        self.assertEqual(dnsgen.partiate_domain(".test.com.1.c.a/b"),['test', 'com', '1','c','a'])

	# Test cases for invalid domain names 
    def test_specialCharDomains(self):
        self.assertEqual(dnsgen.partiate_domain("....."),[])
        self.assertEqual(dnsgen.partiate_domain(".?@#3.fde!.@.qwepo"),[])
        self.assertEqual(dnsgen.partiate_domain("test.?@#3.fde!.@.qwedg"),['test'])
        self.assertEqual(dnsgen.partiate_domain(".1...."),['1'])
        self.assertEqual(dnsgen.partiate_domain(".1../..c.."),['1'])

if __name__ == '__main__':
    unittest.main()

