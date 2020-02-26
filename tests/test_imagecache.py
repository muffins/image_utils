#!/usr/bin/env python3

import os
import shutil
import sys
import tempfile

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
        self.rnm1 = "./tests/img/rick_and_morty_1.png"
        self.rnm2 = "./tests/img/rick_and_morty_2.png"
        self.not_an_image = "./tests/img/not_an_image.txt"

        self.ih = ImageHelper(self.rnm1)
        self.ih.read_image()

    def test_ih_construction(self):
        self.assertIsInstance(self.ih, ImageHelper)
        self.assertTrue(os.path.exists(self.ih.full_path))
        self.assertEqual(self.ih.size, 464461)
    
    def test_ih_native_values(self):
        # First check that the file we're processing is an image
        self.ih.check_image_type()
        self.assertIsInstance(self.ih.full_path, str)
        self.assertIsNot(self.ih.full_path, "")
        self.assertIsInstance(self.ih.filename, str)
        self.assertIsNot(self.ih.filename, "")

        self.assertIsInstance(self.ih.img_type, str)
        self.assertEqual(
            self.ih.img_type, 
            "png image data, 729 x 486, 8-bit/color rgba, non-interlaced"
        )

        self.assertGreater(len(self.ih.data), 0)

        self.assertIsInstance(self.ih.crc32, str)
        self.assertIsNot(self.ih.crc32, "17bfa65a")

    def test_ih_md5_computation(self):

        self.ih.compute_md5()
        self.assertIsInstance(self.ih.md5, str)
        self.assertEqual(self.ih.md5, "d0dc519b6b46614c390aea7a6b5ff8ae")

    def test_ih_image_hash_computations(self):
        # Verify we've actually got data first
        self.ih.check_image_type()
        self.ih.compute_image_hashes()

        self.assertIsInstance(self.ih.ahash, str)
        self.assertEqual(self.ih.ahash, "000068f8f8686f6e")
        self.assertIsInstance(self.ih.phash, str)
        self.assertEqual(self.ih.phash, "c10e372dce8369b5")
        self.assertIsInstance(self.ih.dhash, str)
        self.assertEqual(self.ih.dhash, "cbd6908193dadada")
        self.assertIsInstance(self.ih.whash, str)
        self.assertEqual(self.ih.whash, "00007cfcfc686fee")

    def test_do_not_process_non_image(self):
        # Check the file type
        non_img = ImageHelper(self.not_an_image)
        non_img.check_image_type()

        self.assertFalse(non_img.is_image)
        self.assertEqual(non_img.data, b'')


if __name__ == '__main__':
    unittest.main()