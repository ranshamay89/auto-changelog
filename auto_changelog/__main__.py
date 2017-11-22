"""
Generage a changelog straight from your git commits.

Usage: auto-changelog [options]

Options:
    -r=REPO --repo=REPO     Path to the repository's root directory
    -t=TITLE --title=TITLE  The changelog's title [Default: CHANGELOG]
    -d=DESC --description=DESC
                            Your project's description
    -o=OUTFILE --output=OUTFILE
                            The place to save the generated changelog
                            [Default: CHANGELOG.md]
    -t=TEMPLATEDIR --template-dir=TEMPLATEDIR
                            The directory containing the templates used for
                            rendering the changelog
    -h --help               Print this help text
    -V --version            Print the version number
    -n --repo-name=REPO_NAME Repo name
"""

import os
import sys

import docopt

from parser import group_commits, traverse, Tag
from generator import generate_changelog
from auto_changelog import __version__


def generate_changelog_for_repo(args):
    sys.argv = [sys.argv[0]] + args
    args = parse_args()
    return generate(args)


def parse_args():
    args = docopt.docopt(__doc__, version=__version__)

    if args.get('--template-dir'):
        template_dir = args['--template-dir']
    else:
        # The templates are sitting at ./templates/*.jinja2
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(BASE_DIR, 'templates')
    if args.get('--repo'):
        repo = os.path.abspath(args['--repo'])
    else:
        repo = os.path.dirname(os.path.realpath(__file__))
    return args


def generate(args):
    try:
        # Traverse the repository and group all commits to master by release
        tags, unreleased = traverse(args['--repo'])
    except ValueError as e:
        print('ERROR:', e)
        sys.exit(1)
    if unreleased:
        tags.append(Tag(
            name=unreleased.name,
            date=unreleased.commit.committed_date,
            commit=unreleased.commit))
    changelog = generate_changelog(
        template_dir=args['--template-dir'],
        title=args['--title'],
        description=args.get('--description'),
        unreleased=unreleased,
        tags=tags,
        repo_name=args.get('--repo-name'))
    return changelog
    # Get rid of some of those unnecessary newlines
    # changelog = changelog.replace('\n\n\n', '\n')


def save_changelog(changelog_content, path):
    with open(path, 'w') as f:
        f.write(changelog_content)


def main():
    args = parse_args()
    changelog_txt = generate(args)
    save_changelog(changelog_content=changelog_txt, path=args['--output'])


if __name__ == "__main__":
    main()
