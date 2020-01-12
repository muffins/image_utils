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

    def test_ih_construction(self):
        self.assertIsInstance(self.ic, ImageHelper)
    
    def test_ih_native_values(self):
        self.assertIsInstance(self.ic.full_path, str)
        self.assertIsNot(self.ic.full_path, "")
        self.assertIsInstance(self.ic.filename, str)
        self.assertIsNot(self.ic.filename, "")

        self.assertIsInstance(self.ic.img_type, str)
        self.assertEqual(
            self.ic.img_type, 
            "png image data, 729 x 486, 8-bit/color rgba, non-interlaced"
        )

        self.assertGreater(len(self.ic.data), 0)
        self.assertEqual(self.ic.size, 464461)

        self.assertIsInstance(self.ic.crc32, str)
        self.assertIsNot(self.ic.crc32, "17bfa65a")

    def test_ih_md5_computation(self):

        self.ic.compute_md5()
        self.assertIsInstance(self.ic.md5, str)
        self.assertEqual(self.ic.md5, "d0dc519b6b46614c390aea7a6b5ff8ae")

    def test_ih_image_hash_computations(self):

        self.ic.compute_image_hashes()

        self.assertIsInstance(self.ic.ahash, str)
        self.assertEqual(self.ic.ahash, "000068f8f8686f6e")
        self.assertIsInstance(self.ic.phash, str)
        self.assertEqual(self.ic.phash, "c10e372dce8369b5")
        self.assertIsInstance(self.ic.dhash, str)
        self.assertEqual(self.ic.dhash, "cbd6908193dadada")
        self.assertIsInstance(self.ic.whash, str)
        self.assertEqual(self.ic.whash, "00007cfcfc686fee")


if __name__ == '__main__':
    unittest.main()