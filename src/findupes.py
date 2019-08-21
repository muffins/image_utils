#!/usr/bin/env python3

import argparse
import json
import logging
import pprint
import time

from image_cache import ImageCache
from typing import Dict

logging.basicConfig(format="[%(asctime)-15s] %(message)s")
logger = logging.getLogger("findupes")


# Takes in a target directory and computes information about
# the images contained therin
def genstats(path: str) -> None:
    ic = ImageCache()
    logger.info
    ic.gen_cache_from_directory(path)

    report = {}

    querys = {
        "image_types": "SELECT COUNT(DISTINCT img_type) FROM {};",
        "total_images": "SELECT COUNT(*) FROM {};",
        "average_size": "SELECT AVG(size) FROM {}",
        "total_size": "SELECT SUM(size) FROM {}",
    }

    for k, v in querys.items():
        report[k] = ic.query(v.format(ic.get_table()))

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(report)

def findupes(source: str, target: str) -> Dict[str, any]:
    # Use the Image Cache helper class to read in the source directory
    # to an sqlite3 DB, compute hashes and any necessary pieces for checking
    # if the two images are the same. Then given the target directory, check to
    # see if the image already exists, if it does to a pprint report about all
    # potential dupes
    pass

def main(source: str, target: str, genstats: bool) -> None:

    if genstats:
        genstats(source)
        return
    else:
        findupes(source, target)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s",
        "source", 
        type=str
    )
    parser.add_argument(
        "-t",
        "target", 
        type=str
    )
    parser.add_argument(
        "-g",
        "genstats", 
        default=False,
        action="store_true",
        type=bool
    )

    args = parser.parse_args()
    main(args.source, args.target, args.genstats)