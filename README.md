# finddupes

[![Build Status](https://travis-ci.org/muffins/finddupes.svg?branch=master)](https://travis-ci.org/muffins/finddupes)

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

```
PS C:\Users\Nicholas\work\repos\finddupes> python3 .\src\findupes.py --help
usage: findupes.py [-h] [-d IMAGE_DIR] [-t TARGET] [-b DATABASE] [-s] [-g]

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