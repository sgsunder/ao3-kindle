import setuptools
import subprocess


def get_git_version():
    return subprocess.run(
        ["git", "describe", "--abbrev=0"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh.readlines()]

setuptools.setup(
    name="ao3kindle",
    version=get_git_version(),
    author="Shyam Sunder",
    author_email="sgsunder1@gmail.com",
    description="Upload AO3 fanfics to an Amazon Kindle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sgsunder/ao3-kindle",
    packages=setuptools.find_packages(),
    scripts=["bin/ao3-kindle"],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    install_requires=requirements,
    python_requires=">=3.5",
)
