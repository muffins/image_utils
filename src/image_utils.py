#!/usr/bin/env python3

import asyncio
import argparse
import datetime
import json
import logging
import os
import pprint
import sys
import shutil
import time

from image_cache import ImageCache
from image_cache import ImageHelper

from PIL import Image
from PIL.ExifTags import TAGS

from typing import Dict

# Setup a logger
logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt='[%Y-%m-%d %I:%M:%S]',
    level=logging.INFO,
)
logger = logging.getLogger("image_util")


async def gen_database(path: str, fast: bool) -> None:
    """
    Takes in a target directory and computes information about
    the images contained therin
    """
    ic = ImageCache(fast=fast)
    await ic.gen_cache_from_directory(path)

    report = {}

    queries = {
        #"all_data": "SELECT * FROM {};",
        "image_types": "SELECT COUNT(DISTINCT img_type) FROM {};",
        "total_images": "SELECT COUNT(*) FROM {};",
        "average_size": "SELECT AVG(size) FROM {};",
        "total_size": "SELECT SUM(size) FROM {};",
    }

    for k, v in queries.items():
        rows = ic.query(v.format(ic.get_table()))
        report[k] = rows[0][0]

    # Get duplicate and ambiguous images
    report['duplicates'] = ic.get_duplicates()
    report['ambiguous'] = ic.get_ambiguous()
    report["process_time"] = ic.processing_time

    pp = pprint.PrettyPrinter(indent=2, compact=False)
    pp.pprint(report)

    logger.info("Completed database generation.")
    logger.info(
        f"Processed {ic.get_count()} images in {ic.processing_time} seconds."
    )
    logger.info(f"Encountered {len(report['duplicates'])} duplicate images.")

    tstamp = datetime.datetime.now().strftime("gen_database_%Y-%m-%d.json")
    with open(tstamp, 'w') as fout:
        fout.write(json.dumps(report))
    logger.info(f"Report written to {tstamp}")

async def find_dupes(source: str, target: str, skip: bool, fast: bool) -> Dict[str, any]:
    """
    Use the Image Cache helper class to read in the source directory
    to an sqlite3 DB, compute hashes and any necessary pieces for checking
    if the two images are the same. Then given the target directory, check
    to see if the image already exists, if it does to a pprint report 
    about all potential dupes
    """
    ic = ImageCache(fast=fast)
    if not skip:
        await ic.gen_cache_from_directory(source)
        logger.info(f"Processing took {ic.processing_time} seconds.")
    
    logger.info(
        f"Beginning processing of {target} for potential duplicates. " +
        "Report will be displayed with duplicates, ambiguous files, " +
        "and suggested files for copying when finished. This may take a " +
        "long time."
    )

    report = {
        'duplicates': [],
        'ambiguous': [],
        'migrate': [],
    }
    
    for root, _, filenames in os.walk(target):
        logger.info(f"Processing {len(filenames)} files in {root}")
        for f in filenames:
            full: str = os.path.join(root, f)
            image: ImageHelper = ImageHelper(full)
            image.check_image_type()
            if not image.is_image:
                continue

            image.read_image()
            image.compute_md5()

            # Check if the file/size exists in the db.
            row = ic.lookup(f"WHERE md5 = '{image.md5}'")
            if len(row) > 0:

                # If file and size are the same, grab the crc32 and md5 to verify dupe
                logger.warning(
                        f"Duplicate image verified: {full} already exists in " + 
                        f"at {row[2]}"
                    )
                report['duplicates'].append(image.full_path)
                continue
            else:
                row = ic.lookup(f"WHERE crc32 = '{image.crc32}' and size = '{image.size}'")
                if len(row) > 0:
                    logger.warning(
                        f"Ambiguous files detected. {full} has same size and " +
                        f"crc32 as source directory file {row[2]}, but md5 " +
                        "does not match."
                    )
                    report['ambiguous'].append(image.full_path)
                    continue

            # Add the file to the list of potentials to migrate
            report['migrate'].append(image.full_path)

    pp = pprint.PrettyPrinter(indent=2, compact=False)
    pp.pprint(report)

    logger.info("Completed duplicate scan.")
    logger.info(
        f"Processed {ic.get_count()} images in {ic.processing_time} seconds."
    )
    logger.info(
        f"Report:\n\tDuplicates:\t{len(report['duplicates'])}" +
        f"\n\tAmbiguous:\t{len(report['ambiguous'])}" + 
        f"\n\tUnique:\t{len(report['migrate'])}"
    )
    tstamp = datetime.datetime.now().strftime("find_dupes_%Y-%m-%d.json")
    with open(tstamp, 'w') as fout:
        fout.write(json.dumps(report))
    logger.info(f"Report written to {tstamp}")
    
def get_exif(img_path: str) -> Dict[str, str]:
    image = Image.open(img_path)
    exif = {}
    img_exif = image._getexif()
    if img_exif is not None:
        for (k, v) in img_exif.items():
            exif[TAGS.get(k)] = v
    return exif

async def sort_images(source: str, dest: str) -> None:
    # Helper function to read in a directory of pictures and sort them all
    # based off of exif metadata. By default the sorting happens by /YYYY/MM
    for root, _, filenames in os.walk(source):
        logger.info(f"Processing {len(filenames)} files in {root}")
        for f in filenames:
            full = os.path.join(root, f)
            # Use an ImageHelper for convenience
            ic = ImageHelper(full)
            ic.check_image_type()
            if not ic.is_image:
                logger.warning(
                    f"Encountered file which is not an image: {ic.full_path}"
                )
                continue
            exif = get_exif(full)
            if exif == {}:
                logger.warning(f"Failed to find exif data for {full}")
                continue

            dt = time.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
            new_dest = os.path.join(dest, str(dt.tm_year), str(dt.tm_mon))
            if not os.path.exists(new_dest):
                os.makedirs(new_dest)

            # Copy the file, including metadata
            shutil.copy(full, os.path.join(new_dest, f))
            shutil.copystat(full, os.path.join(new_dest, f))

async def main(source: str, target: str, genstats: bool, 
               should_sort: bool, skip: bool, fast: bool) -> None:
    
    if not os.path.exists(source):
        logger.error(f"Directory does not exist: {source}")
        sys.exit()

    # TODO: Might be able to immediate declare/make an ImageCache, as
    # everyone already takes the `source` dir...
    if should_sort:
        await sort_images(source, target)
    elif genstats:
        await gen_database(source, fast)
        return
    else:
        if not os.path.exists(target):
            logger.error(f"Directory does not exist: {target}")
            sys.exit()
        await find_dupes(source, target, skip, fast)


if __name__ == "__main__":
    # TODO: Argument parser groups for the different features
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--source",
        action="store",
        help="The 'source of truth' image directory. Should be ones total " +
             "image store. This is used for sorting, comparing against, and " +
             "generating image stats.",
    )
    parser.add_argument(
        "-t",
        "--target",
        action="store",
        help="The target folder containing potential duplicate images",
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
        "-g",
        "--genstats", 
        default=False,
        action="store_true"
    )
    parser.add_argument(
        "--database",
        action="store",
        help="Optional path where the ImageCache database should be stored. " + 
             "Defaults to the current working directory.",
    )
    parser.add_argument(
        "--sort_images",
        default=False,
        action="store_true",
        help="When set, sort the images specified with '-d' by year and " +
             "as extracted from exif metadata on the image.",
    )
    parser.add_argument(
        "-f",
        "--fast", 
        default=False,
        action="store_true"
    )
    args = parser.parse_args()

    # TODO: Use args/kwargs :P
    asyncio.run(main(
        args.source, 
        args.target, 
        args.genstats, 
        args.sort_images, 
        args.skip_cache_gen,
        args.fast,
    ))
