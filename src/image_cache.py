#!/usr/bin/env python3

import hashlib
import ImageHash
import magic
import os
import sqlite3

from PIL import Image

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
    'jpeg',
    'png',
    'bmp',
)

class ImageCache:

    def __init__(self, db_name="image_cache.sqlite"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_cache (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                md5 TEXT NOT NULL,
                ahash TEXT NOT NULL,
                phash TEXT NOT NULL,
                dhash TEXT NOT NULL,
                whash TEXT NOT NULL
            )
            """
        )

    def __del__(self):
        self.conn.close()

    """
    Given a directory generate the 
    """
    def gen_cache_from_directory(self, source):
        for root, dirnames, filenames in os.walk(source):
            logger.info("Processing {} files in {}".format(len(filenames), root))
            for filename in filenames:
                full = os.path.join(root, filename)
                # first verify the file is of an image mime type
                m = set([x.lower() for x in magic.from_file(full).split()])
                if len(m.intersection(SUPPORTED_TYPES)) == 0:
                    continue

                # next, compute the ImageHashes of the file
                img = Image.open(full)

                # finally, compute the md5
                ahash = image_hash.average_hash(img)
                phash = image_hash.phash(img)
                dhash = image_hash.dhash(img)
                whash = image_hash.whash(img)
                img_md5 = None
                with open(full, 'rb') as fin:
                    img_md5 = hashlib.md5(fin.read()).hexdigest()

                # and store all of this information in our db
                self.insert(filename, full, img_md5, ahash, phash, dhash, whash)

    def insert(self, filename, path, md5, ahash, phash, dhash, whash):
        self.cursor.execute(
            """
            INSERT INTO image_cache (
                filename,
                path,
                md5,
                image_hash
            ) VALUES (
                {0},
                {1},
                {2},
                {3},
                {4},
                {5},
                {6}
            )
            """.format(filename, path, md5, ahash, phash, dhash, whash)
        )

    def lookup(self, where_clause=""):
        query = """
            SELECT * FROM image_cache
        """
        if where_clause:
            query += " " + where_clause
        query += ";"
        self.cursor.execute(query)
        return self.cursor.fetchall()
