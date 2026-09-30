# Copyright 2026 - Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-only

"""Filter private command logs; this helper does not orchestrate the test."""

import argparse
import configparser
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote, quote_plus


def redact(text, secrets):
    for value in sorted(set(secrets), key=len, reverse=True):
        if len(value) >= 8:
            for encoded in (value, quote(value, safe=""), quote_plus(value)):
                text = text.replace(encoded, "<redacted>")
    text = re.sub(
        r"(?im)^.*(?:password|secret|token|authorization|credential).*?$",
        "<redacted credential line>",
        text,
    )
    text = re.sub(r"(\w+://[^\s/:]+:)[^\s@]+@", r"\1<redacted>@", text)
    # Terminal escapes and workflow commands must not act on runner output.
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    return text.replace("\0", "").replace("::", ": :")


def read_secrets(directory):
    secrets = []
    for path in directory.glob("node*.json"):
        values = json.loads(path.read_text())["values"]
        if not isinstance(values, dict) or not all(
            isinstance(value, str) for value in values.values()
        ):
            raise ValueError("Invalid credential inventory")
        secrets.extend(values.values())
    tempest = directory / "tempest.conf"
    if tempest.exists():
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string(tempest.read_text())
        for section in parser.sections():
            secrets.extend(
                value
                for key, value in parser.items(section)
                if any(word in key for word in ("password", "secret", "token"))
            )
    return secrets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials", type=Path)
    args = parser.parse_args()
    try:
        secrets = read_secrets(args.credentials) if args.credentials else []
    except (ValueError, KeyError, TypeError, OSError, configparser.Error):
        parser.exit(1, "Log withheld: credential inventory could not be read\n")
    sys.stdout.write(redact(sys.stdin.read(), secrets))


if __name__ == "__main__":
    main()
