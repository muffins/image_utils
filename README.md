# Image Utils

[![Build Status](https://travis-ci.org/muffins/image_utils.svg?branch=master)](https://travis-ci.org/muffins/image_utils)

## About 

A simple Python application to help manage folders of pictures. The primary 
use case of this application is to read in a `source` directory, where one
might keep all of their pictures. The program then reads in a `target` directory
which contains new images, some of which may be duplicates from the `source`
directory. The application then iterates through all images in the target looking
for potential duplicate images which is determined using the pictures MD5 sum, or
simply the filename and size when `fast` mode is leveraged.

## Usage

Image Utils leverages `argparse`, so you can always use the `-h` flag to print out the full menu of options.
```
PS C:\Users\Nicholas\work\repos\image_utils> python3 .\src\image_utils.py -h
usage: image_utils.py [-h] [-s SOURCE] [-t TARGET] [--skip_cache_gen] [-g]
                      [--database DATABASE] [--sort_images] [-f]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        The 'source of truth' image directory. Should be ones
                        total image store. This is used for sorting, comparing
                        against, and generating image stats.
  -t TARGET, --target TARGET
                        The target folder containing potential duplicate
                        images
  --skip_cache_gen      Skips the generation of the source image cache. Use
                        this if you are sure that no image changes have taken
                        place since the last run of this program.
  -g, --genstats
  --database DATABASE   Optional path where the ImageCache database should be
                        stored. Defaults to the current working directory.
  --sort_images         When set, sort the images specified with '-d' by year
                        and as extracted from exif metadata on the image.
  -f, --fast
```

To have `image_utils` scan a given directory for duplicate images, use the `-s` 
and `-t` flag together. Note that you can skip the cache generation with 
`--skip_source_cache_generation` and further you can simply compute the
database for a given source directory with the `-g` or `--genstats` argument:
```
PS C:\Users\Nicholas\work\repos\image_utils> python3 .\src\image_utils.py -d F:\Library\Nick\Pictures --target="C:\Users\Nicholas\Desktop\Pictures Backup" --skip_source_cache_generation
```

By default, `image_utils` only uses the file name and size to check if a file
already exists in the cache. If you'd like to use the crc32 and md5 values of 
the file to check for dupes, use the `--deep` flag set to `1`
