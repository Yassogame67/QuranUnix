#!/usr/bin/env python3
"""
إعداد تثبيت تطبيق مصحف المدينة
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mushaf-madinah",
    version="1.0.0",
    author="Quran App Team",
    author_email="",
    description="تطبيق بسيط وأنيق لقراءة القرآن الكريم بخط المصحف المدني",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mushaf-madinah",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Religion :: Islamic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mushaf-madinah=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.pdf", "*.png", "*.ico"],
    },
)
