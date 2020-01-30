#!/usr/bin/env python3

import argparse
import json
import logging
import os
import pprint
import sys
import time

from image_cache import ImageCache
from image_cache import ImageHelper
from typing import Dict

logging.basicConfig(format="[%(asctime)-15s] %(message)s")
logger = logging.getLogger("findupes")


# Takes in a target directory and computes information about
# the images contained therin
def generate_report(path: str) -> None:
    ic = ImageCache()
    ic.gen_cache_from_directory(path)

    report = {}

    queries = {
        "all_data": "SELECT * FROM {};",
        "image_types": "SELECT COUNT(DISTINCT img_type) FROM {};",
        "total_images": "SELECT COUNT(*) FROM {};",
        "average_size": "SELECT AVG(size) FROM {};",
        "total_size": "SELECT SUM(size) FROM {};",
    }

    for k, v in queries.items():
        report[k] = ic.query(v.format(ic.get_table()))

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(report)
    logger.info(f"Processing took {ic.processing_time} seconds.")
    logger.info(f"Encountered {ic.dupe_count} duplicate images.")

def findupes(source: str, target: str, skip: bool) -> Dict[str, any]:
    # Use the Image Cache helper class to read in the source directory
    # to an sqlite3 DB, compute hashes and any necessary pieces for checking
    # if the two images are the same. Then given the target directory, check to
    # see if the image already exists, if it does to a pprint report about all
    # potential dupes
    ic = ImageCache()
    if not skip:
        ic.gen_cache_from_directory(source)

    logger.info(f"Processing took {ic.processing_time} seconds.")
    logger.info(f"Encountered {ic.dupe_count} duplicate images:")

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(ic.get_dupes())

    logger.info(
        f"Beginning processing of {target} for potential duplicates. " +
        "Report will be displayed with duplicates, ambiguous files, and " +
        "suggested files for copying when finished. This may take a long time."
    )

    report = {
        'duplicates': [],
        'ambiguous': [],
        'migrate': [],
    }
    
    for root, _, filenames in os.walk(source):
        logger.info(f"Processing {len(filenames)} files in {root}")
        for f in filenames:
            full: str = os.path.join(root, f)
            
            # Check if the file/size exists in the db.
            row = ic.lookup(
                f"WHERE filename = '{f}'"
            )
            image: ImageHelper = ImageHelper(full)
            if len(row) > 0:
                logger.warning(f"Possible duplicate image found: {full}")
                logger.warning("Checking CRC32 and MD5 of image. . .")
                image.compute_md5()
                
                # TODO: Consider swapping this with just size. If a file has 
                # the same name, and the same size... Odds are it's the same.
                
                if row[3] == image.crc32 and row[4] == image.md5:
                    logger.warning(
                        f"Duplicate image verified, {full} already exists in " +
                        f"{source} at {row[2]}"
                    )
                    report['duplicates'].append(image.full_path)
                else:
                    logger.warning(
                        f"Ambiguous files detected. {full} has same size and " +
                        f"name as source directory file {row[2]}, but md5 or " +
                        "crc32 do not match."
                    )
                    report['ambiguous'].append(image.full_path)
                continue

            # If no file name check for md5

            # If no md5, check for ahash
            report['migrate'].append(image.full_path)
    
    pp.pprint(report)


def sort_images(source: str) -> None:
    # TODO:
    # Helper function to read in a directory of pictures and sort them all
    # based off of exif metadata
    pass


def main(source: str, target: str, genstats: bool, 
         should_sort: bool, skip: bool) -> None:

    if not os.path.exists(source):
        logger.error(f"Directory does not exist: {source}")
        sys.exit()

    if genstats:
        generate_report(source)
        return
    else:
        if not os.path.exists(target):
            logger.error(f"Directory does not exist: {target}")
            sys.exit()
        findupes(source, target, skip)

    if should_sort:
        sort_images(source)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()

    # TODO: These arguments don't really make sense.
    parser.add_argument(
        "-d",
        "--image_dir",
        action="store",
        help="The 'source of truth' image directory. Should be ones total " +
             "image store. This is used for sorting, comparing against, and " +
             "generating image stats.",
    )
    parser.add_argument(
        "--skip_cache_gen",
        action="store_true",
        default=False,
        help="Skips the generation of the source image cache. Use this if you" +
             " are sure that no image changes have taken place since the last" +
             " run of this program.",
    )
    parser.add_argument(
        "-t",
        "--target",
        action="store",
        help="The target folder containing potential duplicate images",
    )
    parser.add_argument(
        "-b",
        "--database",
        action="store",
        help="Optional path where the ImageCache database should be stored. " + 
             "Defaults to the current working directory.",
    )
    parser.add_argument(
        "-s",
        "--sort_images",
        default=False,
        action="store_true",
        help="When set, sort the images specified with '-d' by year, month, " +
             "day as extracted from exif metadata on the image.",
    )
    parser.add_argument(
        "-g",
        "--genstats", 
        default=False,
        action="store_true"
    )

    args = parser.parse_args()
    main(
        args.image_dir, 
        args.target, 
        args.genstats, 
        args.sort_images, 
        args.skip_cache_gen
    )