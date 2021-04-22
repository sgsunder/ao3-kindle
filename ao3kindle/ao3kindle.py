import logging
import os.path
import re
import requests
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from urllib import parse as urlparse
from getpass import getpass
from configparser import ConfigParser
from argparse import ArgumentParser

from appdirs import user_data_dir
from ao3 import AO3


def get_ebook(src_url: str, format: str = "mobi") -> object:
    logging.debug("URL Passed: %s" % src_url)
    logging.debug("File format %s" % format)

    # Start up the API
    api = AO3()

    # Parse the AO3 work url to get work id
    src_url_split = urlparse.urlparse(src_url).path.split("/")
    assert src_url_split.index("works")
    workid = src_url_split[src_url_split.index("works") + 1]

    assert int(workid)
    logging.debug("Post ID Number: %d" % int(workid))

    work = api.work(id=workid)
    logging.debug("Got API object")

    # Now to get the download URL
    workfilename = work.title
    workfilename = re.sub(r"[^\w _-]+", "", workfilename)
    workfilename = re.sub(r" +", " ", workfilename)
    # workfilename = re.sub(r"^(.{24}[\w.]*).*", '$1', workfilename)
    workfilename = urlparse.quote(workfilename)

    dl_url = "/".join(
        [
            "https://archiveofourown.org",
            "downloads",
            workid,
            workfilename + "." + format,
        ]
    )
    logging.info('Fetching from URL: "%s"' % dl_url)

    response = requests.get(dl_url)
    contents = response.content
    print("Downloaded .%s file from AO3..." % format)

    return contents


def email_attachment(
    sender: str,
    destination: str,
    attachment: object,
    server: str,
    password: str,
) -> None:
    # https://stackoverflow.com/a/3363538

    logging.debug("Generating message header")
    m = MIMEMultipart()
    m["Subject"] = "eBook from AO3"
    m["From"] = sender
    m["To"] = destination

    logging.debug("Generating message attachment")
    a = MIMEBase("application", "x-mobipocket-ebook")
    a.set_payload(attachment)
    encode_base64(a)

    logging.debug("Generating attachment header")
    a.add_header(
        "Content-Disposition", 'attachment; filename="ao3-ebook.mobi"'
    )

    logging.debug("Attaching to message")
    m.attach(a)

    logging.info("Connecting to SMTP server: %s" % server)
    s = smtplib.SMTP_SSL(server, 465)
    try:
        s.login(sender, password)
    except smtplib.SMTPAuthenticationError as auth_error:
        logging.error(auth_error)
        raise

    logging.info("Setting email")
    try:
        s.sendmail(sender, destination, m.as_string())
    except smtplib.SMTPException:
        logging.error("Failed to send email")
        raise

    print("Email sent!")


def generate_config(dest: str) -> None:
    print("Regenerating Configuration...")
    config = ConfigParser()
    config["DEFAULT"] = {}
    out_dict = config["DEFAULT"]

    while True:
        print("Email Address for Send-to-Kindle: ", end="")
        out_dict["kindle"] = input()

        print("SMTP Server to send from: ", end="")
        out_dict["smtp-server"] = input()

        print("SMTP sender email: ", end="")
        out_dict["smtp-sender"] = input()

        print("Store a password? Useful for ex. gmail app-specific passwords")
        print(
            "(WARNING: will be stored as plaintext,"
            + " not reccomended for general passwords)"
        )
        print("(y/n): ", end="")
        if input().lower().strip()[:1] == "y":
            print("SMTP Password: ", end="")
            out_dict["smtp-password"] = input()

        print("Is this correct?")
        print("  Kindle email: %s" % out_dict["kindle"])
        print(
            "  SMTP: %s on %s"
            % (out_dict["smtp-server"], out_dict["smtp-sender"])
        )
        print("(y/n): ", end="")
        if input().lower().strip()[:1] == "y":
            break

    logging.debug("Writing config file to %s" % dest)
    with open(dest, "w") as cfgfile:
        config.write(cfgfile)
    logging.debug("Write complete")


def read_config(dest: str) -> object:
    cfgfile = ConfigParser()
    logging.debug("Reading config file from %s" % dest)
    cfgfile.read(dest)
    logging.debug("Read complete")
    return cfgfile["DEFAULT"]


def main() -> None:
    cfgfile_default = os.path.join(
        user_data_dir(appname="ao3-kindle", appauthor=False, roaming=True),
        "conf",
    )

    cli = ArgumentParser(
        description="Upload ArchiveOfOurOwn (AO3) fanfics to an Amazon Kindle"
    )

    cli.add_argument(
        "-c",
        dest="cfgfile",
        default=cfgfile_default,
        nargs="?",
        help='Location of configuration file (default: "%s")'
        % cfgfile_default,
    )

    cli2 = cli.add_mutually_exclusive_group(required=True)
    cli2.add_argument(
        "--configure",
        action="store_true",
        dest="configure",
        help="(Re)generate the configuration File",
    )
    cli2.add_argument("url", nargs="?", help="AO3 Fanfic URL")

    cli.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Show verbose info",
    )
    cli.add_argument(
        "--debug", action="store_true", dest="debug", help="Show debug info"
    )

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
        cfg = read_config(args.cfgfile)
        attach = get_ebook(args.url)
        if "smtp-password" in cfg:
            p = cfg["smtp-password"]
        else:
            p = getpass('Password for "%s": ' % cfg["smtp-sender"])
        email_attachment(
            sender=cfg["smtp-sender"],
            destination=cfg["kindle"],
            attachment=attach,
            server=cfg["smtp-server"],
            password=p,
        )


if __name__ == "__main__":
    main()
