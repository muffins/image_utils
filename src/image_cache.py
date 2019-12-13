#!/usr/bin/env python3

import hashlib
import imagehash
import logging
import magic
import os
import sqlite3
import threading

from PIL import Image
from typing import List, Dict

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

SUPPORTED_TYPES = set([
    "jpeg",
    "png",
    "bmp",
])

logging.basicConfig(
    format="[%(asctime)-15s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("image_cache")


class ImageCache:

    db_table = "image_cache"

    def __init__(self, db_name="image_cache.sqlite"):
        self.db = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        self._lock = threading.Lock()

    def create_table(self) -> None:
        """
        Helper sqlite function to create our table
        """
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.db_table} (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                md5 TEXT NOT NULL,
                ahash TEXT NOT NULL,
                phash TEXT NOT NULL,
                dhash TEXT NOT NULL,
                whash TEXT NOT NULL,
                size INTEGER NOT NULL,
                img_type TEXT NOT NULL
            )
            """
        )

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def gen_stats_for_file(self, full: str) -> Dict[str, any]:

        # first verify the file is of an image mime type
        img_type: str = magic.from_file(full).lower()
        mgc: set = set([x for x in img_type.split()])
        if len(mgc.intersection(SUPPORTED_TYPES)) == 0:
            return

        # next, compute the ImageHashes of the file
        img = Image.open(full)

        # finally, compute the md5
        ahash: str = str(imagehash.average_hash(img))
        phash: str = str(imagehash.phash(img))
        dhash: str = str(imagehash.dhash(img))
        whash: str = str(imagehash.whash(img))
        with open(full, "rb") as fin:
            data = fin.read()
            size: int = len(data)
            img_md5: str = hashlib.md5(data).hexdigest()
        
         # and store all of this information in our db
        self.insert(
            full, os.path.basename(full), img_md5, 
            ahash, phash, dhash, whash, size, img_type
        )

    def gen_cache_from_directory(self, source: str) -> None:
        """
        Given a directory generate the image cache for all image files
        """
        for root, dirnames, filenames in os.walk(source):
            logger.info(f"Processing {len(filenames)} files in {root}")
            for filename in filenames:
                full: str = os.path.join(root, filename)
                
                job = threading.Thread(
                    target=self.gen_stats_for_file, args=(full,)
                )
                job.start()

            # Recursively continue to generate the cache.
            for directory in dirnames:
                self.gen_cache_from_directory(directory)
        
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()

    def insert(self, fname: str, path: str, md5: str, ahash: str, phash: str, 
                     dhash: str, whash: str, size: int, img_type: str) -> None:
        """
        Helper sqlite function to insert a new row
        """
        self._lock.acquire()
        thread_conn = sqlite3.connect(self.db)
        thread_curr = thread_conn.cursor()
        thread_curr.execute(
            f"""INSERT INTO {self.db_table} (
                filename, path, md5, ahash, phash, dhash, whash, size, img_type
            ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )""",
            (fname, path, md5, ahash, phash, dhash, whash, size, img_type)
        )
        thread_conn.commit()
        thread_curr.close()
        thread_conn.close()
        self._lock.release()


    def get_table(self) -> str:
        return self.db_table

    def lookup(self, where_clause: str = "") -> List[str]:
        """
        Helper sqlite function to look up any rows that might exist given
        a where clause
        """
        query = f"""
            SELECT * FROM {self.db_table}
        """
        if where_clause:
            query += " " + where_clause
        query += ";"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def query(self, query: str = "") -> List[str]:
        """
        Helper sqlite function to exec an arbitrary query
        """
        if not query.endswith(';'):
            query += ';'
        self.cursor.execute(query)
        return self.cursor.fetchall()