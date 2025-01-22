#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djspace.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User

import argparse
import logging

logger = logging.getLogger('debug_logfile')

# set up command-line options
desc = """
Accepts as input...
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument(
    '-u',
    '--user',
    required=True,
    help="Provide a username.",
    dest='user',
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test',
)


def main():
    """Main function description."""
    if test:
        print("this is a test eh")
        logger.debug("debug = %s" % test)
    else:
        print("this is not a test")
        user = User.objects.get(username=user)
        print(user)


if __name__ == '__main__':
    args = parser.parse_args()
    user = args.user
    test = args.test

    if test:
        print(args)

    sys.exit(main())
