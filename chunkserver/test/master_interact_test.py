#!/usr/bin/env python3
import unittest
import requests
import json

import time

class TestServer(unittest.TestCase):
    def test_live(self):
        r = requests.get('http://0.0.0.0:5000')
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, "Chunkserver Flask API!")

class TestLease(unittest.TestCase):
    def setUp(self):
        self.test_chunk = open('../chunk/0123.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

        self.test_string = '0123'
        self.false_string = '9999'

        self.no_lease = b'0020200516210900'
        self.big_date = b'0120190516210900'
        self.big_time = b'0120200516200900'
        self.true_lease = b'0120200516212020'

    def test_lease_false(self):
        self.test_chunk = open('../chunk/0123.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.no_lease)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', data={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def test_lease_400(self):
        r = requests.post('http://0.0.0.0:5000/lease', data={'chunk_handle': self.false_string})
        self.assertTrue(r.status_code == 400)

    def test_lease_big_date(self):
        self.test_chunk = open('../chunk/0123.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.big_date)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', data={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def test_lease_big_time(self):
        self.test_chunk = open('../chunk/0123.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.big_time)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', data={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def test_lease_true(self):
        self.test_chunk = open('../chunk/0123.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.true_lease)
        self.test_chunk.close()

        r = requests.post('http://0.0.0.0:5000/lease', data={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, 'false')

    def tearDown(self):
        self.test_chunk = open('../chunk/0123.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

if __name__ == '__main__':
    unittest.main()
