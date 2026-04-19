import argparse
import re
from importlib.metadata import version

from smvp.utilities import task_runner

__version__ = version("smvp")


def font_size(size: str) -> str:
    """Validate size inputs.

    Parameters
    ----------
    size : str
        User input for a font size option.

    Returns
    -------
    str
        The validated user input.

    Raises
    ------
    argparse.ArgumentTypeError
        If the input is not a valid integer (for example is a float).
    argparse.ArgumentTypeError
        If the input is not between 2 and 100.
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
    """Validate font_family inputs.

    Parameters
    ----------
    font : str
        User input for a font family.

    Returns
    -------
    str
        The validated user input.

    Raises
    ------
    argparse.ArgumentTypeError
        If the the selected font family is not recognized.
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
        raise argparse.ArgumentTypeError(f"invalid email address: {address}")
    return address


# ======================================================================


def process_args() -> None:
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
