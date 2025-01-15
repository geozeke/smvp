import argparse
import re

from smvp.utilities import task_runner
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
