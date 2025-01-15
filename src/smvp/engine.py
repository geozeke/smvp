import argparse
import os
import re
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ansi2html import Ansi2HTMLConverter
from bs4 import BeautifulSoup

from smvp.utilities import file_is_html
from smvp.utilities import validate_environment
from smvp.version import get_version

# ======================================================================


def email_type(address: str) -> str:
    """Validate user input of email addresses.

    Parameters
    ----------
    address : str
        An email address.

    Returns
    -------
    str
        If the address is valid, it's returned.

    Raises
    ------
    argparse.ArgumentTypeError
        This is raised for an invalid email address.
    """
    S = r"[a-zA-Z"
    email = re.compile(rf"^{S}0-9._%+-]+@{S}0-9.-]+\.{S}]{{2,}}$")
    if not email.match(address):
        raise argparse.ArgumentTypeError(f"'{address}' is not a valid email address")
    return address


# ======================================================================


def task_runner(args: argparse.Namespace) -> None:
    """Package email contents and send message

    Parameters
    ----------
    args : argparse.Namespace
        The collection of command line arguments.
    """
    if not validate_environment():
        sys.exit(1)

    # Initialize
    sender_email = os.environ["SMVP_USER"]
    email_server = os.environ["SMVP_SERVER"]
    email_token = os.environ["SMVP_TOKEN"]
    receiver_email = args.recipient
    email_subject = args.subject
    email_port = 587

    with args.file as f:
        text_in = f.read()

    # Create separate plantext and html versions of the input
    if not file_is_html(text_in):
        converter = Ansi2HTMLConverter(dark_bg=False)
        html_text = converter.convert(text_in, full=True)
        # Replace the dull-grey default
        html_text = html_text.replace("color: #AAAAAA", "color: #FFFFFF")
    else:
        html_text = text_in
    plain_text = BeautifulSoup(html_text, "lxml").get_text().strip()

    # Package both parts into a MIME multipart message.
    message = MIMEMultipart("alternative")
    message["Subject"] = email_subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_text, "html"))

    # Create a secure context for the TLS connection
    context = ssl.create_default_context()

    # Send the email
    try:
        server = smtplib.SMTP(email_server, email_port)
        server.starttls(context=context)
        server.login(sender_email, email_token)
        server.sendmail(
            from_addr=sender_email,
            to_addrs=receiver_email,
            msg=message.as_string(),
        )
        print("Message successfully sent.")
    except Exception as e:
        print(e)
    finally:
        server.quit()

    return


# ======================================================================


def process_args() -> None:
    msg = """
    Send Mail Via Python (smvp). This tool will send an email from the
    command line, with the body of the email taken from a specified
    file. There are many use cases. For example, it's handy to use smvp
    to have automated Linux scripts (i.e. cron jobs) email you status
    updates and the contents of log files.
    """
    epi = f"Version: {get_version()}"
    parser = argparse.ArgumentParser(description=msg, epilog=epi)

    msg = """The email address of the recipient."""
    parser.add_argument("recipient", type=email_type, help=msg)

    msg = """
    The subject of the email. IMPORTANT: Make sure to enclose the entire
    subject in double quotes for proper processing on the command line.
    """
    parser.add_argument("subject", type=str, help=msg)

    msg = """
    The file containing the text which will make up the body of the
    email message. The input file can be a text file with ANSI color
    codes, HTML, or plain text. The resulting email will be sent as a
    multi-part MIME message that renders properly in both plain text and
    HTML.
    """
    parser.add_argument("file", type=argparse.FileType("r"), help=msg)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"smvp {get_version()}",
    )

    args = parser.parse_args()
    task_runner(args=args)
