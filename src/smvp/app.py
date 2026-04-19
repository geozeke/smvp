import argparse
import re
from importlib.metadata import version

from smvp.utilities import task_runner

__version__ = version("smvp")


def font_size(size: str) -> str:
    """Validate a font size argument.

    Parameters
    ----------
    size : str
        User-provided font size value.

    Returns
    -------
    str
        Validated font size value.

    Raises
    ------
    argparse.ArgumentTypeError
        If ``size`` is not an integer string.
    argparse.ArgumentTypeError
        If ``size`` is outside the inclusive range ``[2, 100]``.
    """
    for c in size:
        if not c.isdigit():
            msg = "font size must be an integer"
            raise argparse.ArgumentTypeError(msg)

    int_size = int(size)
    min_size = 2
    max_size = 100
    if int_size >= min_size and int_size <= max_size:
        return size
    else:
        msg = f"font size must be between {min_size} and {max_size}"
        raise argparse.ArgumentTypeError(msg)


# ======================================================================


def font_family(font: str) -> str:
    """Validate a font family argument.

    Parameters
    ----------
    font : str
        User-provided font family value.

    Returns
    -------
    str
        Canonical font family value.

    Raises
    ------
    argparse.ArgumentTypeError
        If ``font`` is not a supported font family.
    """
    valid_fonts = {
        "ANDALE MONO": "Andale Mono",
        "ARIAL": "Arial",
        "BRUSH SCRIPT MT": "Brush Script MT",
        "COMIC SANS MS": "Comic Sans MS",
        "COURIER NEW": "Courier New",
        "FANTASY": "fantasy",
        "GARAMOND": "Garamond",
        "GEORGIA": "Georgia",
        "HELVETICA": "Helvetica",
        "IMPACT": "Impact",
        "LUMINARI": "Luminari",
        "MONACO": "Monaco",
        "MONOSPACE": "monospace",
        "SANS-SERIF": "sans-serif",
        "SERIF": "serif",
        "TAHOMA": "Tahoma",
        "TIMES NEW ROMAN": "Times New Roman",
        "TREBUCHET MS": "Trebuchet MS",
        "VERDANA": "Verdana",
    }
    user_input = " ".join([word.upper() for word in font.split()])
    if user_input in valid_fonts:
        return valid_fonts[user_input]
    else:
        raise argparse.ArgumentTypeError(
            f"unsupported font family: {font}; see README for supported values"
        )


# ======================================================================


def email_type(address: str) -> str:
    """Validate an email address argument.

    Parameters
    ----------
    address : str
        Email address to validate.

    Returns
    -------
    str
        Validated email address.

    Raises
    ------
    argparse.ArgumentTypeError
        If ``address`` does not match the expected email format.
    """
    S = r"[a-zA-Z"
    email = re.compile(rf"^{S}0-9._%+-]+@{S}0-9.-]+\.{S}]{{2,}}$")
    if not email.match(address):
        raise argparse.ArgumentTypeError(f"invalid email address: {address}")
    return address


# ======================================================================


def process_args() -> None:
    """Parse command-line arguments and run the mail task.

    Returns
    -------
    None
    """
    msg = """
    Send an email whose body is read from a text or HTML file.
    """
    epi = f"Version: {__version__}"
    parser = argparse.ArgumentParser(
        description=msg,
        epilog=epi,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    msg = """recipient email address"""
    parser.add_argument("recipient", type=email_type, help=msg)

    msg = """
    email subject; quote it if it contains spaces
    """
    parser.add_argument("subject", type=str, help=msg)

    msg = """
    text or HTML file to use as the email body
    """
    parser.add_argument("file", type=argparse.FileType("r"), help=msg)

    msg = """
    font family for HTML output; case-insensitive; see README for
    supported values
    """
    parser.add_argument(
        "-f", "--font_family", type=font_family, default="Courier New", help=msg
    )

    msg = """
    font size in pixels (2-100)
    """
    parser.add_argument("-s", "--font_size", type=font_size, default=12, help=msg)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"smvp {__version__}",
    )

    args = parser.parse_args()
    task_runner(args=args)
    return
