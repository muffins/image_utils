#!/usr/bin/env python3

import hashlib
import imagehash
import logging
import magic
import os
import pprint
import sqlite3
import time
import threading
import zlib

from PIL import Image
from typing import List, Dict

"""
    Image Cache Schema

    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    full_path TEXT NOT NULL,
    crc32 TEXT NOT NULL,
    md5 TEXT NOT NULL,
    ahash TEXT,
    phash TEXT,
    dhash TEXT,
    whash TEXT,
    size INTEGER NOT NULL,
    img_type TEXT NOT NULL
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


class ImageHelper(object):
    """
    Helper class to process all of the data on an image we desire
    """
    crc_chunk_size = 65535
    magic_buffer = 4096

    def __init__(self, full_path: str) -> None:
        self.full_path = full_path
        self.filename = os.path.basename(self.full_path)
        self.data = b''
        self.size = 0
        self.crc32 = ''
        self.read_image()
        self.get_image_type()

    def get_image_type(self) -> None:
        """
        A helper to process the Magic MIME type from the buffer
        """
        self.img_type = magic.from_buffer(self.data[:self.magic_buffer]).lower()

    def read_image(self) -> None:
        """
        A helper function that reads the image one block at a time. We do this
        to compute the CRC32 as we go, which is used for 'Fast' dupe checking
        """
        crc32 = 0
        with open(self.full_path, "rb") as fin:
            while True:
                data = fin.read(self.crc_chunk_size)
                if not data:
                    break
                self.data += data
                self.size += len(data)
                crc32 = zlib.crc32(data, crc32)
        self.crc32 = f"{crc32:08x}"

    def compute_md5(self) -> None:
        """
        We use the MD5 as a slower "fast" mechanism to see if we've already 
        processed this file.
        """
        self.md5: str = hashlib.md5(self.data).hexdigest()

    def compute_image_hashes(self) -> None:
        """
        We use ImageHash values to help us identify if we've already seen this 
        file with higher levels of certainty
        """
        # first verify the file is of an image mime type
        imagic: set = set([x for x in self.img_type.split()])
        if len(imagic.intersection(SUPPORTED_TYPES)) == 0:
            logger.error(
                f"Inavlid MIME type encountered {self.img_type}. Will not " + 
                "compute ImageHash values."
            )
            return

        # next, compute the ImageHashes of the file
        img = Image.open(self.full_path)
        self.ahash: str = str(imagehash.average_hash(img))
        self.phash: str = str(imagehash.phash(img))
        self.dhash: str = str(imagehash.dhash(img))
        self.whash: str = str(imagehash.whash(img))

    def print_image_details(self) -> None:
        report = {
            "full_path": self.full_path,
            "filename": self.filename,
            "crc32": self.crc32,
            "size": self.size,
            "img_type": self.img_type,
            "md5": self.md5,
            "ahash": self.ahash,
            "phash": self.phash,
            "dhash": self.dhash,
            "whash": self.whash,
        }
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(report)


class ImageCache(object):

    dupe_count = 0
    duplicates = []

    def __init__(self, db_name: str = "image_cache.sqlite", 
                table_name: str = "image_cache"):
        self.db_name = db_name
        self.db_table = table_name
        
        self._lock = threading.Lock()

        self.db_conn = sqlite3.connect(self.db_name, check_same_thread=False)

        self.create_table()
        

    def create_table(self) -> None:
        """
        Helper sqlite function to create our table
        """
        self._lock.acquire()
        db_curr = self.db_conn.cursor()
        db_curr.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.db_table} (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                full_path TEXT NOT NULL,
                crc32 TEXT NOT NULL,
                md5 TEXT NOT NULL,
                ahash TEXT,
                phash TEXT,
                dhash TEXT,
                whash TEXT,
                size INTEGER NOT NULL,
                img_type TEXT NOT NULL
            )
            """
        )
        db_curr.close()
        self._lock.release()

    def __del__(self):
        self.db_conn.commit()
        self.db_conn.close()

    def gen_stats_for_file(self, full: str) -> Dict[str, any]:

        image = ImageHelper(full)
        image.process()
        
        # Only insert if we've not seen this image before
        if len(self.lookup(f"where md5 = '{image.md5}'")) > 0:
            logger.info(
                "Potential duplicate image found: " + 
                f"{image.full_path}:{image.md5}"
            )
            logger.debug(f"{full}:{image.md5} already exists in DB, skipping")
            self.dupe_count += 1
            self.duplicates += image
        else:
            # and store all of this information in our db
            self.insert(image)

    def gen_cache_from_directory(self, source: str) -> None:
        """
        Given a directory generate the image cache for all image files
        """
        start = time.time()
        for root, _, filenames in os.walk(source):
            logger.info(f"Processing {len(filenames)} files in {root}")
            for filename in filenames:
                full: str = os.path.join(root, filename)
                job = threading.Thread(
                    target=self.gen_stats_for_file, args=(full,)
                )
                job.start()
        
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()
        self.db_conn.commit()
        self.processing_time = int(time.time() - start)

    def insert(self, image: ImageHelper) -> None:
        """
        Helper sqlite function to insert a new row
        """
        self._lock.acquire()
        # TODO: This could probably be optimized somehow.
        db_curr = self.db_conn.cursor()
        db_curr.execute(
            f"""INSERT INTO {self.db_table} (
                filename, full_path, crc32, md5, ahash, 
                phash, dhash, whash, size, img_type
            ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )""",
            (
                image.filename,
                image.full_path,
                image.crc32,
                image.md5, 
                image.ahash, 
                image.phash, 
                image.dhash, 
                image.whash, 
                image.size, 
                image.img_type
            )
        )
        db_curr.close()
        self._lock.release()

    def get_table(self) -> str:
        return self.db_table

    def get_dupes(self) -> List[ImageHelper]:
        return self.duplicates

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
        db_curr = self.db_conn.cursor()
        return db_curr.execute(query).fetchall()

    def query(self, query: str = "") -> List[str]:
        """
        Helper sqlite function to exec an arbitrary query
        """
        if not query.endswith(';'):
            query += ';'
        db_curr = self.db_conn.cursor()
        return db_curr.execute(query).fetchall()