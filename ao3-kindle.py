#!/usr/bin/env python3

import logging
from typing import Tuple

import json
import re
from urllib import parse as urlparse
import requests
from os.path import expanduser
from getpass import getpass
from configparser import ConfigParser
from argparse import ArgumentParser

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import mimetypes

from ao3 import AO3



def get_ebook(src_url: str, format: str = 'mobi') -> object:
	logging.debug('URL Passed: %s' % src_url)
	logging.debug('File format %s' % format)

	# Start up the API
	api = AO3()

	workid = src_url.split('/')[-1]
	assert int(workid)
	logging.debug('Post ID Number: %d' % int(workid))

	work = api.work(id=workid)
	logging.debug('Got API object')


	# Now to get the download URL
	workfilename = work.title
	workfilename = re.sub(r"[^\w _-]+", '', workfilename)
	workfilename = re.sub(r" +", ' ', workfilename)
	# workfilename = re.sub(r"^(.{24}[\w.]*).*", '$1', workfilename)
	workfilename = urlparse.quote(workfilename)

	dl_url = '/'.join([
		'https://archiveofourown.org',
		'downloads',
		work.author[:2],
		work.author,
		workid,
		workfilename + '.' + format])
	logging.info('Fetching from URL: %s' % dl_url)

	response = requests.get(dl_url)
	contents = response.content
	logging.info('Downloaded file from AO3')

	return contents



def email_attachment(sender: str, destination: str, attachment: object, server: str) -> None:
	# TODO
	# https://stackoverflow.com/a/3363254
	logging.error('TODO')



def generate_config(dest: str) -> None:
	print('Regenerating Configuration...')
	config = ConfigParser()
	config['DEFAULT'] = {}
	out_dict = config['DEFAULT']

	while True:
		print('Email Address for Send-to-Kindle:')
		out_dict['kindle'] = input()

		print('SMTP Server to send from:')
		out_dict['smtp-server'] = input()

		print('SMTP sender email:')
		out_dict['smtp-sender'] = input()

		print('Is this correct? (y/n):')
		print('  Kindle email: %s' % out_dict['kindle'])
		print('  SMTP: %s on %s' % (out_dict['smtp-server'], out_dict['smtp-sender']))
		if input().lower().strip()[:1] == 'y':
			break

	with open(dest, 'w') as cfgfile:
		logging.debug('Writing config file to %s' % dest)
		config.write(cfgfile)
		logging.debug('Write complete')



def read_config(dest: str) -> Tuple[str, str, str]:
	cfgfile = ConfigParser()
	logging.debug('Reading config file from %s' % dest)
	cfgfile.read(dest)
	logging.debug('Read complete')
	return (cfgfile['DEFAULT']['kindle'], 
		cfgfile['DEFAULT']['smtp-server'], 
		cfgfile['DEFAULT']['smtp-sender'])



if __name__ == "__main__":
	cfgfile_default = expanduser("~") + '/.config/ao3-kindle'
	cli = ArgumentParser(
		description='Upload ArchiveOfOurOwn (AO3) fanfics to an Amazon Kindle')
	cli.add_argument('-c', dest='cfgfile', 
		default=cfgfile_default, nargs='?',
		help='Location of config file (default: %s)' % cfgfile_default)
	cli2 = cli.add_mutually_exclusive_group(required=True)
	cli2.add_argument('--configure', action='store_true',
		dest='configure',
		help='(Re)Generate the Configuration File')
	cli2.add_argument('url', nargs='?',
		help='AO3 Fanfic URL')
	cli.add_argument('-v', '--verbose', action='store_true',
		dest='verbose',
		help='Show verbose info')
	cli.add_argument('--debug', action='store_true',
		dest='debug',
		help='Show debug info')

	args = cli.parse_args()

	if args.debug:
		logging.basicConfig(level=logging.DEBUG)
	elif args.verbose:
		logging.basicConfig(level=logging.INFO)
	else:
		logging.basicConfig(level=logging.WARNING)

	if args.configure:
		generate_config(args.cfgfile)
	else:
		kindle, src_addr, src_server = read_config(args.cfgfile)

		attach = get_ebook(args.url)
		email_attachment(
			sender=src_addr, destination=kindle,
			attachment=attach, server=src_server)
