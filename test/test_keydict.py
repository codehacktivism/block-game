#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
import sys, os
sys.path.insert(0, os.path.abspath(__file__ + "/../.."))

from keydict import *

class TestKeyDict(unittest.TestCase):
    
    def test_has_key_pressed(self):
        keys = KeyDict()
        start_key = "a_key_is_pressed"
        
        keys.press_key(start_key)

        self.assertTrue(len(keys.keys) != 0)
        self.assertTrue(keys.keys.has_key(start_key))

    def test_has_key_released(self):
        keys = KeyDict()
        enter_key = "enter_is_pressed"

        keys.press_key(enter_key)
        keys.release_key(enter_key)

        self.assertEqual(0, keys.keys[enter_key])

    def test_clear_keys(self):
        keys = KeyDict()
        any_key = "a_key_is_pressed"
        
        keys.press_key(any_key)
        keys.clear()
        self.assertEqual(0, len(keys.keys))

    def test_poll_key(self):
        keys = KeyDict()

        not_the_poll_key = keys.poll_key("not the poll key")
        self.assertEqual(0, not_the_poll_key)

        keys.press_key("the poll key")
        poll_key = keys.poll_key("the poll key")
        self.assertNotEqual(0, poll_key)
        self.assertEqual(2, keys.keys["the poll key"])

    def test_poll_key_once(self):
        keys = KeyDict()

        keys.press_key("the poll key")
        poll_key = keys.poll_key_once("the poll key")
        self.assertNotEqual(0, poll_key)
        self.assertEqual(0, keys.keys["the poll key"])
    
        
if __name__ == '__main__':
    unittest.main()
