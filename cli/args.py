#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse


def create_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser()


def create_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        '-v', '--version', 
        action="store_true", 
        help='show this application version and exit'
    )
    parser.add_argument(
        '-e', '--export',
        dest='user_id',
        action="store_true",
        help='export user music in JSON format'
    )

    return parser


def get_args() -> argparse.Namespace:
    return create_args(create_parser()).parse_args()
