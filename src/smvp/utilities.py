import argparse
import os
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ansi2html import Ansi2HTMLConverter
from bs4 import BeautifulSoup
from bs4.element import Tag

STYLE = "font-family: FF !important; font-size: FSpx !important;"


def print_docstring(msg: str) -> None:
    """Print a normalized multiline help message.

    Notes
    -----
    The input string is expected to start with a newline and use
    consistent indentation across lines.

    Parameters
    ----------
    msg : str
        Message text to normalize and print.

    Returns
    -------
    None
    """
    # Delete the first line ('\n' by itself), then strip any trailing
    # spaces. Remove leading padding, then print.
    clean = msg[1:].rstrip()
    lines = clean.split("\n")
    spaces = 0
    for c in lines[0]:
        if c.isspace():
            spaces += 1
        else:
            break
    formatted_docstring = "\n".join([line[spaces:] for line in lines])
    print(formatted_docstring)
    return


# ======================================================================


def file_is_html(file_to_test: str) -> bool:
    """Determine whether text appears to be HTML.

    Parameters
    ----------
    file_to_test : str
        Text content to inspect.

    Returns
    -------
    bool
        ``True`` if HTML markers are detected; otherwise, ``False``.
    """
    soup = BeautifulSoup(file_to_test, "html.parser")
    return soup.find(True) is not None


# ======================================================================


def validate_environment() -> bool:
    """Validate required SMTP environment variables.

    Returns
    -------
    bool
        ``True`` if all required variables are set; otherwise, ``False``.
    """
    try:
        os.environ["SMVP_USER"]
        os.environ["SMVP_TOKEN"]
        os.environ["SMVP_SERVER"]

    except KeyError:
        msg = """
        One or more credentials for sending email are missing from your
        environment. Set the following environment variables in the
        shell you are using before running smvp:

        Linux / macOS shells:
        export SMVP_USER="<your email>"
        export SMVP_TOKEN="<your token>"
        export SMVP_SERVER="<smtp server>"

        Windows PowerShell:
        $env:SMVP_USER = "<your email>"
        $env:SMVP_TOKEN = "<your token>"
        $env:SMVP_SERVER = "<smtp server>"

        Windows Command Prompt:
        set SMVP_USER=<your email>
        set SMVP_TOKEN=<your token>
        set SMVP_SERVER=<smtp server>

        The SMTP server must support STARTTLS on port 587.
        """
        print()
        print_docstring(msg=msg)
        return False

    return True


# ======================================================================


def task_runner(args: argparse.Namespace) -> None:
    """Build and send an email message from parsed arguments.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    None
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

    try:
        with args.file as f:
            text_in = f.read()
    except UnicodeDecodeError:
        msg = f"""
        Unable to process: {args.file.name}
        smvp can only process textfiles (including those with ANSI
        escape sequences) or html files. No email sent.
        """
        print_docstring(msg=msg)
        sys.exit(1)

    # Craft an HTML version compatible with Gmail. Plain-text input is
    # filtered through ansi2html so ANSI escape sequences become HTML.
    # The text replacement below removes ansi2html's dull-grey default.
    content_type = args.content_type
    if content_type == "auto":
        treat_as_html = file_is_html(text_in)
    else:
        treat_as_html = content_type == "html"

    if not treat_as_html:
        converter = Ansi2HTMLConverter(dark_bg=False)
        html_text = converter.convert(text_in, full=True)
        html_text = html_text.replace("color: #AAAAAA", "color: #FFFFFF")
    else:
        html_text = text_in

    # Set font family and size
    new_style = STYLE.replace("FF", args.font_family)
    new_style = new_style.replace("FS", str(args.font_size))

    soup = BeautifulSoup(html_text, "lxml")
    plain_text = soup.get_text().strip()

    # Gmail strips custom css, so we need to apply inline styles with
    # (!important) to the body tag.
    body_tag = soup.find("body")
    if isinstance(body_tag, Tag):
        body_tag["style"] = new_style

    # Also apply inline styles with (!important) to .ansi2html-content
    # tags
    ansi_content_tags = soup.find_all(class_="ansi2html-content")
    for tag in ansi_content_tags:
        if isinstance(tag, Tag):
            tag["style"] = new_style

    # ! Debug code goes here when testing.

    # Package both parts into a MIME multipart message.
    message = MIMEMultipart("alternative")
    message["Subject"] = email_subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(str(soup), "html"))

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
