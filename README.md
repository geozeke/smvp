# Send Mail Via Python (smvp)

<br>

<img src="https://lh3.googleusercontent.com/d/1PpjTCw4T1HpHU_TacQSjZptzw67WqwIz"
alt="smvp logo" width="120"/>

The _smvp_ utility takes a file whose contents will be parsed and packaged
into the body of an email message, then sent to a designated email
address. The input file can be a text file with ANSI color codes, HTML,
or plain text. The resulting email will be sent as a multi-part MIME
message that renders properly in both plain text and HTML.

_Note: The file itself is not sent as an attachment; instead, the
contents of the file are put into into the body of the email._

## Use Case

There are probably many, but I wrote _smvp_ so my cron scripts can email
me status information and the contents of log files. Some of the files
contain ANSI escape sequences for terminal colors. The _smvp_ utility
converts those ANSI escape sequences into proper HTML tags, so the
emails I get are nicely formatted.

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

## Usage

```text
usage: smvp [-h] recipient subject file
```

For example:

```text
smvp friend@gmail.com "Hello, Friend" ~/logfile.txt
```

For more details, run:

```text
smvp -h
```
