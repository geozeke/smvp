# Send Mail Via Python (smvp)

<br>

<img src="https://lh3.googleusercontent.com/d/1PpjTCw4T1HpHU_TacQSjZptzw67WqwIz"
alt="smvp logo" width="120"/>

The _smvp_ utility takes a file whose contents will be parsed and
packaged into the body of an email message, then sent to a designated
email address. The input file can be a text file with ANSI color codes,
HTML, or plain text. The resulting email will be sent as a multi-part
MIME message that renders properly in both plain text and HTML.

_Note: The file itself is not sent as an attachment; instead, the
contents of the file are put into into the body of the email._

## Use Case

There are probably a few, but I wrote _smvp_ for two primary reasons:

1. I found that fiddling with `postfix` and `sendmail` was a pain.
2. I want my cron scripts to email me status information and the
contents of various log files. Some of the files contain ANSI escape
sequences for terminal colors. The _smvp_ utility converts those ANSI
escape sequences into proper HTML tags, so the emails I get are nicely
formatted. You could set `$MAILTO` in your corntab, but you won't get
proper handling of ANSI escape sequences, and refer to number 1 above.

_smvp_ is not intended to be a bulk emailer for formatted messages.
There other (better) tools for that.

_PRO TIP: If you're sending mail with smvp from within a script, make
sure to include a line that exports the directory path where your python
tool installer puts things. For example, if you're using uv, you would
put somthing like this near the top of your bash script:_

```bash
# Setup PATH export so the script can find installed python tools
export PATH="$PATH:/home/<yourhome>/.local/bin"
```

## Installation

Use your preferred python package installer for command line tools, for
example:

```text
pipx install smvp
```

or

```text
uv tool install smvp
```

or

```text
python3 -m venv .venv
source .venv/bin/activate
pip3 install smvp
```

## Requirements

### First

Make sure the following environment variables are set and exported in
your current shell:

```text
export SMVP_USER="<your email>"    # e.g. "myemail@gmail.com"
export SMVP_TOKEN="<your token>"   # e.g. "<gmail app password>"
export SMVP_SERVER="<smtp server>" # e.g. "smtp.gmail.com"
```

It is recommended that you put the lines above in your "rc" file
(`.bashrc`, `.zshrc`, etc.) for use across multiple shell sessions and
processes. To confirm you have the environment variables correctly set
(with the correct spellings), run this in a terminal:

```text
set | grep ^SMVP_
```

_Note: If you make changes to your "rc" file, make sure to "source" it
or open a new terminal window before running smvp again._

### Second

The `SMVP_SERVER` you select must support secure TLS connections on
port `587`. Check the SMTP settings for your email provider. This is the
default TLS port on Gmail, so if you're using your Gmail account to send
emails, you're good-to-go.

## Styling

_smvp_ offers custom font and font size options for your email. The
default font for formatted HTML email is `Courier New`, `12px`. Beyond
the default you can choose any font size from `2px` up to and including
`100px`, from among these font families:

```text
"Andale Mono", "Arial", "Brush Script MT", "Comic Sans MS",
"Courier New", "Garamond", "Georgia", "Helvetica", "Impact",
"Luminari", "Monaco", "Tahoma", "Times New Roman", "Trebuchet MS",
"Verdana", "fantasy", "monospace", "sans-serif", "serif"
```

_NOTE: Not every font will render properly on every device. When in
doubt, fonts like: "monospace", "sans-serif", "fantasy", and "serif" are
pretty safe. You may just have try a few options to land on the right
one for your use case._

## Usage

```text
usage: smvp [-h] [-f FONT_FAMILY] [-s FONT_SIZE] [-v] recipient subject file
```

For example:

```text
smvp friend@gmail.com "Hello, Friend" ~/logfile.txt -f "Trebuchet MS" -s 14
```

For more details, run:

```text
smvp -h
```
