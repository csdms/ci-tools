from __future__ import print_function

import os
import sys
import argparse
import subprocess
import traceback
import glob

from conda_build.config import Config
from conda_build.build import bldpkg_path
from conda_build.metadata import MetaData


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('recipe', help='path to recipe folder')
    parser.add_argument('--org', default='csdms-stack',
                        help='anaconda user/org')
    parser.add_argument('--channel', default='main',
                        help='channel tag for upload')
    parser.add_argument('--token', type=argparse.FileType('r'),
                        default=None,
                        help='secret anaconda token')

    args = parser.parse_args()

    if args.token is not None:
        token = args.token.read().strip()
    else:
        token = None
    upload(args.recipe, token=token, channel=args.channel, org=args.org)


def upload(recipe, channel='main', token=None, org=None):
    print('Using python: {prefix}'.format(prefix=sys.prefix))

    meta = MetaData(recipe)
    file_to_upload = bldpkg_path(meta, Config())

    cmd = ['anaconda']
    if token is not None:
        cmd.extend(['-t', token])
    cmd.extend(['upload', '--force', '--user', org,
                '--channel', channel,
                file_to_upload.decode('utf-8')])

    print(' '.join(cmd))

    if not os.path.isfile(file_to_upload):
        raise RuntimeError('{name}: not a file'.format(name=file_to_upload))

    try:
        subprocess.check_call(' '.join(cmd), shell=True)
    except subprocess.CalledProcessError:
        traceback.print_exc()


if __name__ == '__main__':
    sys.exit(main())
