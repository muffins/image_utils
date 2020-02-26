#!/usr/bin/env python3

import asyncio
import logging
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

from image_utils import sort_images


# TODO: We should likely move this into the setUp function of our class...
def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

class TestImageUtils(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='iu-tests')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    @async_test
    async def test_sort_images(self):
        await sort_images('./tests/img', self.tmpdir)

        for root, _, filenames in os.walk(self.tmpdir):
            for f in filenames:
                print(os.path.join(root, f))


if __name__ == '__main__':
    unittest.main()