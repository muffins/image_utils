#!/usr/bin/env python3

import os
import sys

from unittest import TestCase

# Insert the src directory for our code to the beginning of the path
sys.path.insert(
    0, 
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../src"
        )
    )
)
from image_cache import ImageCache


class TestImageCache(TestCase):

    def setUp(self):
        self.ic = ImageCache()

    def tearDown(self):
        pass

    def test_ic_construction(self):
        self.assertIsInstance(self.ic, ImageCache)
    
    def test_ic_get_table_name(self):
        self.assertIsInstance(self.ic.get_table, str)