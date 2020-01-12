# finddupes

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

