#!/usr/bin/env python3
import unittest
import requests
import json

import time, os

#locations are still hard-coded. I will work on changing that when neccessary

class TestServer(unittest.TestCase):
    def test_live(self):
        r = requests.get('http://0.0.0.0:5000')
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, "Chunkserver Flask API!")

class TestLease(unittest.TestCase):
    def setUp(self):
        self.test_string = '-1'
        self.false_string = '-2'

        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

        self.no_lease = b'0020200516210900'
        self.big_date = b'0120190516210900'
        self.big_time = b'0120200516200900'
        self.true_lease = b'0120200516212020'

    def test_lease_false(self):
        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.no_lease)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def test_lease_400(self):
        r = requests.post('http://0.0.0.0:5000/lease', json={'chunk_handle': self.false_string})
        self.assertTrue(r.status_code == 400)

    def test_lease_big_date(self):
        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.big_date)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def test_lease_big_time(self):
        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.big_time)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def test_lease_true(self):
        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.true_lease)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def tearDown(self):
        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

#simple chunk invent endpoint testing
#it's too much work to write a consistent random sample then cross check everything returned
#probably easier to just check it functions then check the content individually
class testChunkInventory(unittest.TestCase):
    def setUp(self):
        self.test_string = '-1'
        self.test_data = b'0020200516210900'

        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.test_data)
        self.test_chunk.close()

    def test_chunk_inventory(self):
        r = requests.post('http://0.0.0.0:5000/chunk-inventory')
        self.assertEqual(r.status_code, 200)

    def tearDown(self):
        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

#almost copy-pasted one-to-one from chunk invent
class testGarbageCollection(unittest.TestCase):
    def setUp(self):
        self.test_string = '0123'
        self.test_string2 = '0456'
        self.test_data = b'0020200516210900'

        self.test_chunk = open('../chunk/' + self.test_string + '.chunk', 'wb')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.test_data)
        self.test_chunk.close()

        self.test_chunk = open('../chunk/' + self.test_string2 + '.chunk', 'wb')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.test_data)
        self.test_chunk.close()

    def test_collect_garbage(self):
        r = requests.post('http://0.0.0.0:5000/collect-garbage', json={'deleted_chunks': [self.test_string, self.test_string2]})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(os.path.exists('../chunk/' + self.test_string + '.chunk'))
        self.assertFalse(os.path.exists('../chunk/' + self.test_string2 + '.chunk'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
