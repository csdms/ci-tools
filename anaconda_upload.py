from __future__ import print_function

import os
import sys
import argparse
import subprocess
import traceback
import glob

from conda_build.render import bldpkg_path
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
    file_to_upload = bldpkg_path(meta)

    cmd = ['anaconda']
    if token is not None:
        cmd.extend(['-t', token])
    cmd.extend(['upload', '--force', '--user', org,
                '--channel', channel,
                file_to_upload.decode('utf-8')])

    if not os.path.isfile(file_to_upload):
        raise RuntimeError('{name}: not a file'.format(name=file_to_upload))

    cmd_to_print = [item for item in cmd]
    try:
        cmd_to_print[cmd_to_print.index('-t') + 1] = '<the-token>'
    except ValueError:
        pass
    finally:
        cmd_to_print = ' '.join(cmd_to_print)
    print(cmd_to_print)

    try:
        subprocess.check_call(' '.join(cmd), shell=True)
    except subprocess.CalledProcessError:
        print('{cmd}: returned non-zero exit status'.format(cmd=cmd_to_print),
              file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main())
