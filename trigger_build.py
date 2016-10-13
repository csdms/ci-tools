#! /usr/bin/env python
import argparse
import sys
import json
import requests


def get_travis_api_url(repo, org='csdms-stack'):
    TRAVIS_API_URL = 'https://api.travis-ci.org/repo/{org}%2F{repo}/requests'
    return TRAVIS_API_URL.format(org=org, repo=repo)


def post_to_travis(repo, token, org='csdms-stack'):
    url = get_travis_api_url(repo, org=org)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Travis-API-Version': 3,
        'Authorization': 'token {token}'.format(token=token),
    }
    payload = {'request': {'branch': 'master'}}

    return requests.post(url, headers=headers, data=json.dumps(payload))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', nargs='+', help='travis repositories to build')
    parser.add_argument('token_file', type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='file that contains secret travis token')
    parser.add_argument('--org', default='csdms-stack',
                        help='travis organization')

    args = parser.parse_args()

    token = args.token_file.read().strip()
    for repo in args.repo:
        print post_to_travis(repo, org=args.org, token=token).text


if __name__ == '__main__':
    sys.exit(main())
