#!/usr/bin/env python3
import unittest
import requests
import json

import time, os

#locations are still hard-coded. I will work on changing that when neccessary

SERVER_ADDRESS = 'http://0.0.0.0:8000/'
CHUNK_DIR = '../chunk/'

class TestServer(unittest.TestCase):
    def test_live(self):
        r = requests.get(SERVER_ADDRESS)
        self.assertTrue(r.status_code == 200)
        self.assertEqual(r.text, "Chunkserver Flask API!")

class TestCreate(unittest.TestCase):
    def setUp(self):
        self.test_string = '-1'

    def test_create(self):
        r = requests.post(SERVER_ADDRESS + 'create', json={'chunk_handle': self.test_string})
        self.assertEqual(r.status_code, 200)
        with open(CHUNK_DIR + self.test_string + '.chunk', 'rb') as f:
            self.assertEqual(f.read(), b'\x00\x00\x00\x00\x00\x00\x00\x00\x00')

class TestLease(unittest.TestCase):
    def setUp(self):
        self.test_string = '-1'
        self.false_string = '-2'

        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

        self.no_lease = b'\x00\x00\x07\xe3\x05\x14\x14\x3b\x00' #2019/05/20 20:59:00
        self.big_date = b'\x00\x01\x07\xe3\x05\x14\x14\x3b\x00' #2019/05/20 20:59:00
        self.big_time = b'\x00\x01\x07\xe4\x05\x14\x00\x00\x00' #2020/05/20 00:00:00
        self.true_lease = b'\x00\x01\x07\xe4\x05\x16\x0d\x1b\x00' #2020/05/22 13:27:00

    def test_lease_false(self):
        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.no_lease)
        self.test_chunk.close()

        r = requests.post(SERVER_ADDRESS + 'lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertFalse(r.json())

    def test_lease_400(self):
        r = requests.post(SERVER_ADDRESS + 'lease', json={'chunk_handle': self.false_string})
        self.assertTrue(r.status_code == 400)

    def test_lease_big_date(self):
        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.big_date)
        self.test_chunk.close()

        r = requests.post(SERVER_ADDRESS + 'lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertFalse(r.json())

    def test_lease_big_time(self):
        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.big_time)
        self.test_chunk.close()

        r = requests.post(SERVER_ADDRESS + 'lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertFalse(r.json())

    def test_lease_true(self):
        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.true_lease)
        self.test_chunk.close()

        r = requests.post(SERVER_ADDRESS + 'lease', json={'chunk_handle': self.test_string})
        self.assertTrue(r.status_code == 200)
        self.assertTrue(r.json())

    def tearDown(self):
        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

#simple chunk invent endpoint testing
#it's too much work to write a consistent random sample then cross check everything returned
#probably easier to just check it functions then check the content individually
class testChunkInventory(unittest.TestCase):
    def setUp(self):
        self.test_string = '-1'
        self.test_data = b'\x00\x00\x07\xe3\x05\x14\x14\x3b\x00' #2019/05/20 20:59:00

        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'wb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.test_data)
        self.test_chunk.close()

    def test_chunk_inventory(self):
        r = requests.post(SERVER_ADDRESS + 'chunk-inventory')
        self.assertEqual(r.status_code, 200)

    def tearDown(self):
        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

#almost copy-pasted one-to-one from chunk invent
class testGarbageCollection(unittest.TestCase):
    def setUp(self):
        self.test_string = '-1'
        self.test_string2 = '-2'
        self.test_data = b'\x00\x00\x07\xe3\x05\x14\x14\x3b\x00'

        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'wb')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.test_data)
        self.test_chunk.close()

        self.test_chunk = open(CHUNK_DIR + self.test_string2 + '.chunk', 'wb')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.test_data)
        self.test_chunk.close()

    def test_collect_garbage(self):
        r = requests.post(SERVER_ADDRESS + 'collect-garbage', json={'deleted_chunks': [self.test_string, self.test_string2]})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(os.path.exists(CHUNK_DIR + self.test_string + '.chunk'))
        self.assertFalse(os.path.exists(CHUNK_DIR + self.test_string2 + '.chunk'))

    def tearDown(self):
        pass

#not implemented replica
class testLeaseGrant(unittest.TestCase):
    def setUp(self):
        self.test_string = '-1'
        self.test_old_data = b'\x00\x00\x07\xe3\x05\x14\x14\x3b\x00' #2019/05/20 20:59:00

        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'wb')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.write(self.test_old_data)
        self.test_chunk.close()

        self.new_timestamp = "2020-05-20T00:00:00Z"

    def test_lease_grant(self):
        r = requests.post(SERVER_ADDRESS + 'lease-grant', json={'chunk_handle': self.test_string, 'timestamp': self.new_timestamp, 'replica': ''})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), 0)

        with open(CHUNK_DIR + self.test_string + '.chunk', 'rb') as f:
            self.assertEqual(f.read(), b'\x00\x01\x07\xe4\x05\x14\x00\x00\x00')

    def tearDown(self):
        self.test_chunk = open(CHUNK_DIR + self.test_string + '.chunk', 'rb+')
        self.test_chunk.seek(0)
        self.test_chunk.truncate(0)
        self.test_chunk.close()

if __name__ == '__main__':
    unittest.main()
