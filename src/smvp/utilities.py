import os
import re


def print_docstring(msg: str) -> None:
    """Print a formatted docstring.

    This function assumes the docstring is in a very specific format:

    >>> msg = \"\"\"
    >>> First line (non-blank)
    >>>
    >>> Subsequent lines
    >>> Subsequent lines
    >>> Subsequent lines
    >>> ...
    >>> Can include empty lines after the first.
    >>> \"\"\"

    Parameters
    ----------
    msg : str
        The docstring to be printed.
    """
    # Delete the first line ('\n' by itself), then strip any trailing
    # spaces. Remove leading padding, then print.
    clean = msg[1:].rstrip()
    lines = clean.split("\n")
    spaces = 0
    for c in lines[0]:
        if c in ["\n", " ", "\t"]:
            spaces += 1
        else:
            break
    formatted_docstring = "\n".join([line[spaces:] for line in lines])
    print(formatted_docstring)
    return


# ======================================================================


def file_is_html(file_to_test: str) -> bool:
    """Determine if a file is HTML

    Parameters
    ----------
    file_to_test : str
        The text of a file to test.

    Returns
    -------
    bool
        True if the file is HTML; else False
    """
    if re.search(
        r"<!DOCTYPE\s+html>|<(html|head|body|title|div|p|span)",
        file_to_test,
        re.IGNORECASE,
    ):
        return True
    return False


# ======================================================================


def validate_environment() -> bool:
    """Ensure the correct environment variables are in place.

    Returns
    -------
    bool
        True if the correct variables are set; else False.
    """
    try:
        os.environ["SMVP_USER"]
        os.environ["SMVP_TOKEN"]
        os.environ["SMVP_SERVER"]

    except KeyError:
        msg = """
        One or more credentials for sending email are missing from your
        environment. Make sure the following environment variables are
        set and exported in your current shell:
        
        export SMVP_USER="<your email>"    # e.g. "myemail@gmail.com"
        export SMVP_TOKEN="<your token>"   # e.g. "<gmail app password>"
        export SMVP_SERVER="<smtp server>" # e.g. "smtp.gmail.com"

        It's recommended that you put the lines above in your "rc" file
        (.bashrc, .zshrc, etc.) for use across multiple shell sessions
        and processes. To confirm you have the environment variables
        correctly set (with the correct spellings), run this in a
        terminal:

        set | grep ^SMVP_

        Note: If you make changes to your "rc" file, make sure to
        "source" it before running smvp again. Also, the SMVP_SERVER you
        select must support secure TLS connections on port 587.
        """
        print()
        print_docstring(msg=msg)
        return False

    return True


# ======================================================================
