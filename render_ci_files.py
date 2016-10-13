#! /usr/bin/env python
import os
import sys
import argparse
from glob import glob

from jinja2 import Environment, FileSystemLoader
from conda_build.metadata import MetaData

THIS_DIR = os.path.dirname(__file__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('recipe', help='path to recipe folder')
    parser.add_argument('--templates',
                        default=os.path.join(THIS_DIR, 'templates'),
                        help='path to folder of templates')
    parser.add_argument('--org', default='csdms-stack',
                        help='organization name')

    args = parser.parse_args()

    env = Environment(loader=FileSystemLoader(args.templates))

    md = MetaData(os.path.join(args.recipe, 'meta.yaml'))

    for name in os.listdir(args.templates):
        base, ext = os.path.splitext(name)
        if ext == '.tmpl':
            template = env.get_template(name)

            with open(base, 'w') as fp:
                fp.write(template.render(dict(meta=md.meta, org=args.org)))

    return 0

if __name__ == '__main__':
    sys.exit(main())

