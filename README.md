# Image Utils

[![Build Status](https://travis-ci.org/muffins/image_utils.svg?branch=master)](https://travis-ci.org/muffins/image_utils)

## About 

A simple Python application to help manage folders of pictures. The primary 
use case of this application is to read in a `source` directory, where one
might keep all of their pictures. The program then reads in a `target` directory
which contains new images, some of which may be duplicates from the `source`
directory. The application then iterates through all images in the target looking
for potential duplicate images. This application leverages the `ImageMagic`
libraries, as the desired intent is that if an image has been modified slightly
it will still be identified as a duplicate. We first check via the filename and
size, then MD5, then using ahash, dhash, whash, and phash of the image. The 
objective is to first quickly determine if the image already exists in our
cache, and then leverage slower more robust mechanisms to verify if the image
already exists.

## Usage

Image Utils leverages `argparse`, so you can always use the `-h` flag to print out the full menu of options.
```
PS C:\Users\Nicholas\work\repos\image_utils> python3 .\src\image_utils.py --help
usage: image_utils.py [-h] [-d IMAGE_DIR] [-t TARGET] [-b DATABASE] [-s] [-g]

optional arguments:
  -h, --help            show this help message and exit
  -d IMAGE_DIR, --image_dir IMAGE_DIR
                        The 'source of truth' image directory. Should be ones
                        total image store. This is used for sorting, comparing
                        against, and generating image stats.
  -t TARGET, --target TARGET
                        The target folder containing potential duplicate
                        images
  -b DATABASE, --database DATABASE
                        Optional path where the ImageCache database should be
                        stored. Defaults to the current working directory.
  -s, --sort_images     When set, sort the images specified with '-d' by year,
                        month, day as extracted from exif metadata on the
                        image.
  -g, --genstats
```

To have image_utils scan a given directory for duplicate images, use the `-d` and `-t` flag together. Note that you can skip the cache generation with `--skip_source_cache_generation`:
```
PS C:\Users\Nicholas\work\repos\image_utils> python3 .\src\image_utils.py -d F:\Library\Nick\Pictures --target="C:\Users\Nicholas\Desktop\Pictures Backup" --skip_source_cache_generation
```

By default, `image_utils` only uses the file name and size to check if a file
already exists in the cache. If you'd like to use the crc32 and md5 values of 
the file to check for dupes, use the `--deep` flag set to `1`