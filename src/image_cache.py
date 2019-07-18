#!/usr/bin/env python3

import hashlib
import os
import sqlite3

"""
    Image Cache Schema

    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    md5 TEXT NOT NULL,
    image_hash TEXT NOT NULL

"""

class ImageCache(object):

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
                image_hash TEXT NOT NULL
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
            for filename in filenames:

    def insert(self, filename, path, md5, image_hash):
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
                {3}
            )
            """.format(filename, path, md5, image_hash)
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
