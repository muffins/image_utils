#!/usr/bin/env python3

import os
import sys

import unittest

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
from image_cache import ImageHelper


class TestImageCache(unittest.TestCase):

    def setUp(self):
        self.ic = ImageCache()

    def tearDown(self):
        pass

    def test_ic_construction(self):
        self.assertIsInstance(self.ic, ImageCache)
    
    def test_ic_get_table_name(self):
        self.assertIsInstance(self.ic.get_table(), str)


class TestImageHelper(unittest.TestCase):

    def setUp(self):
        self.ic = ImageHelper("./tests/rick_and_morty.png")
        self.ic.process()

    def tearDown(self):
        pass

    def test_ih_construction(self):
        self.assertIsInstance(self.ic, ImageHelper)
    
    def test_ih_get_values(self):
        self.assertIsInstance(self.ic.full_path, str)
        self.assertIsNot(self.ic.full_path, "")
        self.assertIsInstance(self.ic.filename, str)
        self.assertIsNot(self.ic.filename, "")

        self.assertIsInstance(self.ic.img_type, str)
        self.assertEqual(
            self.ic.img_type, 
            "png image data, 729 x 486, 8-bit/color rgba, non-interlaced"
        )

        self.assertIsInstance(self.ic.ahash, str)
        self.assertIsNot(self.ic.ahash, "")
        self.assertIsInstance(self.ic.phash, str)
        self.assertIsNot(self.ic.phash, "")
        self.assertIsInstance(self.ic.dhash, str)
        self.assertIsNot(self.ic.dhash, "")
        self.assertIsInstance(self.ic.whash, str)
        self.assertIsNot(self.ic.whash, "")

        self.assertIsInstance(self.ic.md5, str)
        self.assertIsNot(self.ic.md5, "")

        self.assertGreater(len(self.ic.data), 0)
        self.assertGreater(self.ic.size, 0)


if __name__ == '__main__':
    unittest.main()