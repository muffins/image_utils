#!/usr/bin/env python3

from setuptools import setup

setup(
    name="image_utils",
    version="0.0.1",
    description="A utility CLI to help identify duplicate images.",
    author="Nick Anderson",
    author_email="nanderson7@gmail.com",
    python_requires=">=3",
    packages=["image_utils"],
    install_requires=[
        "ImageHash>=4.0",
        "Pillow>=7.0.0",
        "python-magic-bin>=0.4.14",
    ],
    test_suite="tests.test_image_utils",
)
