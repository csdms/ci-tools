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
    parser.add_argument('-c', action='append', type=str,
                        dest='channels', default=[],
                        help='additional channel to search for packages')

    args = parser.parse_args()

    if args.token is not None:
        token = args.token.read().strip()
    else:
        token = None

    channels = args.channels + ['csdms-stack', 'conda-forge']

    file_to_upload = render(args.recipe, numpy=args.numpy,
                            filename_hashing=args.filename_hashing,
                            channels=channels)
    if args.output:
        print(file_to_upload)
    else:
        upload(file_to_upload, token=token, channel=args.channel,
               org=args.org)


def render(recipe, numpy=None, filename_hashing=True, channels=[]):
    '''
    Render recipe

    Parameters
    ----------
    recipe : path
    numpy
    filename_hashing

    Returns
    -------
    path
        file path of rendered recipe
    '''
    config = Config(numpy=numpy, filename_hashing=filename_hashing)
    config.channel_urls.extend(channels)

    meta_tuples = api.render(recipe, config=config)
    file_to_upload = api.get_output_file_paths(meta_tuples, config=config)[0]

    return file_to_upload


def find_alternate(file_to_upload):
    '''
    Find alternative name for a file to upload

    Parameters
    ----------
    file_to_upload : path
        file to find alternative name for

    Returns
    -------
    file : string
        file to upload

    '''
    import re, glob

    pattern = re.sub('h[0-9a-f]{7}', 'h*', file_to_upload)
    alternatives = glob.glob(pattern)

    try:
        return alternatives[0]
    except IndexError:
        return file_to_upload


def upload(file_to_upload, channel='main', token=None, org=None):
    '''
    Upload file to Anaconda Cloud

    Parameters
    ----------
    channel : string
       Anaconda Cloud channel to upload file to
    token :  string
       Anaconda token or path to file containing token
    org : string
       Anaconda Cloud user/organiztion
    '''
    print('Using python: {prefix}'.format(prefix=sys.prefix))
    print('File to upload: {fn}'.format(fn=file_to_upload))

    if not os.path.isfile(file_to_upload):
        file_to_upload = find_alternate(file_to_upload)

    if not os.path.isfile(file_to_upload):
        raise RuntimeError('{name}: not a file'.format(name=file_to_upload))

    cmd = ['anaconda']
    if token is not None:
        cmd.extend(['-t', token])
    cmd.extend(['upload', '--force', '--user', org,
                '--channel', channel,
                file_to_upload])

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
