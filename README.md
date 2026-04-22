# Send Mail Via Python (smvp)

[![PyPI version](https://img.shields.io/pypi/v/smvp)](https://pypi.org/project/smvp/)
[![Python versions](https://img.shields.io/pypi/pyversions/smvp)](https://pypi.org/project/smvp/)
[![License](https://img.shields.io/pypi/l/smvp)](https://github.com/geozeke/smvp/blob/main/LICENSE)
[![Status](https://img.shields.io/badge/status-beta-blue)](https://pypi.org/project/smvp/)
[![PyPI downloads](https://img.shields.io/pypi/dm/smvp)](https://pypi.org/project/smvp/)

<br>

<img
src="https://raw.githubusercontent.com/geozeke/smvp/main/assets/smvp-logo.png"
alt="smvp logo" width="120"/>

The _smvp_ utility reads a file, uses its contents as the body of an
email, and sends it to a specified recipient. The input file can be a
text file with ANSI color codes, HTML, or plain text. The resulting
message is sent as a multipart MIME email that renders properly in both
plain text and HTML. The `--content-type` option can auto-detect the
input type or force it to be handled as plain text or HTML.

> **Note:** The file itself is not sent as an attachment; instead, the
> contents of the file are put into the body of the email.

## Compatibility

The `smvp` runtime is supported on Windows and Linux.

Project tooling remains Linux-only. That includes the `just` recipes,
the Bash scripts in `scripts/`, the release workflow, and the `cron`
examples below.

## Use Case

There are probably several use cases, but I wrote _smvp_ for two
primary reasons:

1. Configuring `postfix` and `sendmail` was more trouble than I wanted.
2. I want my cron scripts to email me status information and the
   contents of various log files. Some of the files contain ANSI escape
   sequences for terminal colors. The _smvp_ utility converts those ANSI
   escape sequences into styled HTML, so the emails I get are nicely
   formatted. You could set `$MAILTO` in your crontab, but you would not
   get proper handling of ANSI escape sequences, and you would still
   have the problem mentioned in item 1.

## Installation

Use your preferred Python package installer for command line tools, for
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
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat

python -m pip install smvp
```

## Requirements

### SMTP Environment Variables

Set the following environment variables in the shell you are using
before running `smvp`.

Linux / macOS shells:

```bash
export SMVP_USER="<your email>"    # e.g. "myemail@gmail.com"
export SMVP_TOKEN="<your token>"   # e.g. "<gmail app password>"
export SMVP_SERVER="<smtp server>" # e.g. "smtp.gmail.com"
```

Windows PowerShell:

```powershell
$env:SMVP_USER = "<your email>"
$env:SMVP_TOKEN = "<your token>"
$env:SMVP_SERVER = "<smtp server>"
```

Windows Command Prompt:

```text
set SMVP_USER=<your email>
set SMVP_TOKEN=<your token>
set SMVP_SERVER=<smtp server>
```

If you want these variables to persist across sessions, add them to
your shell profile or your Windows user environment settings.

---

Linux automation note:

> **Tip:** If you're using `cron` and sending mail with _smvp_ from
> within a script, make sure to include the environment variables at the
> top of your `crontab` so your scripts will have access to them during
> execution. Also include a line in your script that exports the
> directory where your Python tool installer places executables. For
> example, if you're using `uv` on Ubuntu, you could put something like
> this near the top of your bash script:

```bash
# Setup PATH export so the script can find installed Python tools
export PATH="$PATH:/home/<yourhome>/.local/bin"
```

### SMTP Server

The `SMVP_SERVER` you select must support secure TLS connections on port
`587`. Check the SMTP settings for your email provider. This is the
default TLS port on Gmail, so if you are using your Gmail account to
send email, this requirement is usually already satisfied.

## Styling

_smvp_ offers custom font and font size options for your email. The
default font for formatted HTML email is `Courier New`, `12px`. Beyond
the default, you can choose any font size from `2px` up to and
including `100px`, from the following font families:

```text
"Andale Mono", "Arial", "Brush Script MT", "Comic Sans MS",
"Courier New", "Garamond", "Georgia", "Helvetica", "Impact",
"Luminari", "Monaco", "Tahoma", "Times New Roman", "Trebuchet MS",
"Verdana", "fantasy", "monospace", "sans-serif", "serif"
```

> **Note:** Not every font will render properly on every device. When in
> doubt, fonts like: "monospace", "sans-serif", "fantasy", and "serif"
> are pretty safe. You may just have to try a few options to land on the
> right one for your use case.

## Content Type

By default, _smvp_ uses `--content-type auto`, which inspects the input
and decides whether to treat it as plain text or HTML. You can override
that behavior when needed:

```text
auto  Auto-detect whether the input should be treated as text or HTML
text  Always treat the input as plain text, including HTML-like content
html  Always treat the input as HTML
```

This is useful when the input contains angle brackets that should be
sent literally, or when you want to force HTML rendering for a file that
would not otherwise be detected as HTML.

## Usage

```text
usage: smvp [-h] [-c {auto,text,html}] [-f FONT_FAMILY] [-s FONT_SIZE] [-v] recipient subject file
```

For example:

```text
smvp friend@gmail.com "Hello, Friend" ~/logfile.txt -f "Trebuchet MS" -s 14
```

On Windows, the same command works after installation. The only
difference is the path style, for example:

```text
smvp friend@gmail.com "Hello, Friend" .\logfile.txt -f "Trebuchet MS" -s 14
```

Force plain-text handling for HTML-like input:

```text
smvp friend@gmail.com "Raw Markup" ./snippet.txt --content-type text
```

Force HTML handling:

```text
smvp friend@gmail.com "Rendered Markup" ./fragment.txt --content-type html
```

For more details, run:

```text
smvp -h
```
