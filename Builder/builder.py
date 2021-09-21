#!/usr/bin/env python3
#
# SDSetup Complex Fetcher
# Copyright (C) 2020 Nichole Mattera
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
# 02110-1301, USA.
#

import argparse
import common
import config
import modules
from pathlib import Path
import shutil
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='Directory to output modules to.')
    parser.add_argument(
        '-a', '--auto',
        action='store_true',
        default=False,
        help='Perform an auto build.')

    # Parse arguments
    args = parser.parse_args()

    return args

def init_version_messages(args):
    if not args.auto:
        return [ 'SDSetup Modules built with:' ]
    return []

if __name__ == '__main__':
    args = parse_args()

    temp_directory = common.generate_temp_path()
    common.mkdir(temp_directory)

    auto_build = False
    if hasattr(args, 'auto'):
        auto_build = args.auto

    version_messages = init_version_messages(args)

    build_messages = modules.build(temp_directory, auto_build)

    common.delete(args.output)

    if build_messages is not None:
        version_messages += build_messages
        
        shutil.move(temp_directory, args.output)

        for message in version_messages:
            print(message)

    common.delete(Path.cwd().joinpath('tmp'))
