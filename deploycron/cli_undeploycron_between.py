#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import deploycron


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_line",
                        help="start line to delimit the crontab block to "
                             "remove")
    parser.add_argument("stop_line",
                        help="stop line to delimit the crontab block to "
                             "remove")
    args = parser.parse_args()
    start_line = args.start_line
    stop_line = args.stop_line
    deploycron.undeploycron_between(start_line, stop_line)


if __name__ == "__main__":
    main()
