**Python script to upload [ArchiveOfOurOwn](https://archiveofourown.org/) (AO3) fanfics to an Amazon Kindle**

## Installation

`pip3 install ao3kindle`

## Configuration

To interactively generate a configuration, run `ao3-kindle --configure`

Ensure that you have the sender email address
[approved](https://www.amazon.com/gp/help/customer/display.html?nodeId=201974240)
on your Amazon account. Gmail users may need to
[allow less secure apps](https://support.google.com/accounts/answer/6010255?hl=en)
and/or
[use an app password](https://support.google.com/accounts/answer/185833?hl=en)

## Help

From `ao3-kindle --help`:
```
usage: ao3-kindle [-h] [-c [CFGFILE]] [--configure] [-v] [--debug] [url]

Upload ArchiveOfOurOwn (AO3) fanfics to an Amazon Kindle

positional arguments:
  url            AO3 Fanfic URL

optional arguments:
  -h, --help     show this help message and exit
  -c [CFGFILE]   Location of config file (default:
                 ~/.config/ao3-kindle)
  --configure    (Re)Generate the Configuration File
  -v, --verbose  Show verbose info
  --debug        Show debug info
```

## Building

```
python3 setup.py sdist bdist_wheel
twine upload dist/*
```
