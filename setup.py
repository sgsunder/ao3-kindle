import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ao3kindle",
    version="0.1.2",
    author="Shyam Sunder",
    author_email="sgsunder1@gmail.com",
    description="Upload AO3 fanfics to an Amazon Kindle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sgsunder/ao3-kindle",
    packages=setuptools.find_packages(),
    scripts=['bin/ao3-kindle'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
