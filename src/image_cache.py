#!/usr/bin/env python3

import hashlib
import imagehash
import logging
import magic
import os
import sqlite3

from PIL import Image
from typing import List

"""
    Image Cache Schema

    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    md5 TEXT NOT NULL,
    ahash TEXT NOT NULL,
    phash TEXT NOT NULL,
    dhash TEXT NOT NULL,
    whash TEXT NOT NULL
"""

SUPPORTED_TYPES = set(
    "jpeg",
    "png",
    "bmp",
)

logging.basicConfig(format="[%(asctime)-15s] %(message)s")
logger = logging.getLogger("image_cache")


class ImageCache:

    db_table = "image_cache"

    def __init__(self, db_name="image_cache.sqlite"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self) -> None:
        """
        Helper sqlite function to create our table
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS {0} (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                md5 TEXT NOT NULL,
                ahash TEXT NOT NULL,
                phash TEXT NOT NULL,
                dhash TEXT NOT NULL,
                whash TEXT NOT NULL,
                size INTEGER NOT NULL
            )
            """.format(self.db_table)
        )

    def __del__(self):
        self.conn.close()

    def gen_cache_from_directory(self, source: str) -> None:
        """
        Given a directory generate the image cache for all image files
        """
        for root, dirnames, filenames in os.walk(source):
            logger.info("Processing {} files in {}".format(len(filenames), root))
            for filename in filenames:
                full = os.path.join(root, filename)
                # first verify the file is of an image mime type
                img_type = magic.from_file(full).lower()
                mgc = set([x for x in img_type.split()])
                if len(mgc.intersection(SUPPORTED_TYPES)) == 0:
                    continue

                # next, compute the ImageHashes of the file
                img = Image.open(full)

                # finally, compute the md5
                ahash = imagehash.average_hash(img)
                phash = imagehash.phash(img)
                dhash = imagehash.dhash(img)
                whash = imagehash.whash(img)
                img_md5 = None
                with open(full, "rb") as fin:
                    data = fin.read()
                    size = len(data)
                    img_md5 = hashlib.md5(data).hexdigest()

                # and store all of this information in our db
                self.insert(filename, full, img_md5, ahash, phash, dhash, whash, size, img_type)
            
            # Recursively continue to generate the cache.
            for directory in dirnames:
                self.gen_cache_from_directory(directory)

    def insert(self, fname: str, 
                     path: str, 
                     md5: str, 
                     ahash: str, 
                     phash: str, 
                     dhash: str, 
                     whash: str, 
                     size: int,
                     img_type: str) -> None:
        """
        Helper sqlite function to insert a new row
        """
        self.cursor.execute(
            """
            INSERT INTO {0} (
                filename,
                path,
                md5,
                ahash,
                phash,
                dhash,
                whash,
                size,
                img_type
            ) VALUES ( {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9} )
            """.format(
                self.db_table, 
                fname, 
                path, 
                md5, 
                ahash, 
                phash, 
                dhash, 
                whash, 
                size, 
                img_type,
            )
        )

    def get_table(self) -> str:
        return self.db_table

    def lookup(self, where_clause: str = "") -> List[str]:
        """
        Helper sqlite function to look up any rows that might exist given
        a where clause
        """
        query = """
            SELECT * FROM {0}
        """.format(self.db_table)
        if where_clause:
            query += " " + where_clause
        query += ";"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def query(self, query: str = "") -> List[str]:
        """
        Helper sqlite function to exec an arbitrary query
        """
        self.cursor.execute(query + ";")
        return self.cursor.fetchall()