from __future__ import print_function

import os
import sys
import argparse
import subprocess
import traceback
import glob

from conda_build.render import bldpkg_path
from conda_build.metadata import Config
from conda_build import api


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
    parser.add_argument('--numpy',
                        default=os.environ.get('NUMPY_VERSION', None),
                        help='version of numpy used')
    parser.add_argument('--old-build-string', dest="filename_hashing",
                        action='store_false',
                        help='disable addition of requirements hash')
    parser.add_argument('--output', action='store_true',
                        help='print name of file to upload')

    args = parser.parse_args()

    if args.token is not None:
        token = args.token.read().strip()
    else:
        token = None
    file_to_upload = render(args.recipe, numpy=args.numpy,
                            filename_hashing=args.filename_hashing)
    if args.output:
        print(file_to_upload)
    else:
        upload(file_to_upload, token=token, channel=args.channel,
               org=args.org)


def render(recipe, numpy=None, filename_hashing=True):
    config = Config(numpy=numpy, filename_hashing=filename_hashing)
    meta_tuples = api.render(recipe, config=config)
    file_to_upload = api.get_output_file_paths(meta_tuples, config=config)[0]

    return file_to_upload


def upload(file_to_upload, channel='main', token=None, org=None):
    print('Using python: {prefix}'.format(prefix=sys.prefix))

    cmd = ['anaconda']
    if token is not None:
        cmd.extend(['-t', token])
    cmd.extend(['upload', '--force', '--user', org,
                '--channel', channel,
                file_to_upload])

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
