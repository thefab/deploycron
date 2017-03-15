#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import os
import sys
import deploycron


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath",
                        help="Complete file path of the cron to deploy")
    args = parser.parse_args()
    filepath = args.filepath
    if not os.path.isfile(filepath):
        print("ERROR: filepath [%s] is not a file" % filepath, file=sys.stderr)
        sys.exit(1)
    deploycron.deploycron(filename=filepath)


if __name__ == "__main__":
    main()
