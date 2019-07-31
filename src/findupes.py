#!/usr/bin/env python3

import argparse
import json
import time

# Can maybe use this - https://pypi.org/project/ImageHash/
# import imagehash
# hash = imagehash.average_hash(Image.open('test.png'))
# otherhash = imagehash.average_hash(Image.open('other.bmp'))
# print(hash == otherhash)

# Takes in a target directory and computes information about
# the images contained therin
def genstats():
    # TODO: Generate the following
    #   - Image Count
    #   - Average image size
    #   - Total image size on disk
    #   - Break down of image format
    # Pretty print it?
    pass


def findupes():
    # Use the Image Cache helper class to read in the source directory
    # to an sqlite3 DB, compute hashes and any necessary pieces for checking
    # if the two images are the same. Then given the target directory, check to
    # see if the image already exists, if it does to a pprint report about all
    # potential dupes
    pass

def main():
    


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("source", type=str)
    parser.add_argument("target", type=str)
    parser.add_argument("genstats", type=bool)

    if args.genstats:
        genstats()
        return

    args = parser.parse_args()
    main(args.source, args.target, args.genstats)