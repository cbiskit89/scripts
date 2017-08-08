#!/usr/bin/env python3

import argparse
import itertools
import logging

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler())

class SudoersArgParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(SudoersArgParser, self).__init__(*args, **kwargs)
        self.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                help='enable debug output')
        self.add_argument('-f', '--file', dest='sudoers_file', required=True,
                help='relative or absolute path to sudoers file')


def print_table(d):
    l = itertools.zip_longest(*d.values(), fillvalue='')
    print(','.join(d.keys()))
    for i in l:
        print(','.join(i))


def compare_to_hr_users(d):
    hr_users = set()
    with open('/Users/cmiller/testspace/IE-3858/users_from_hr.txt', 'r') as fd:
        for line in fd:
            hr_users.add(line.strip().lower())
    for k in d.keys():
        l = [i for i in d[k] if i not in hr_users]
        d[k] = l
    print_table(d)

def merge_lines(line, fd):
    next_line = fd.readline().strip()
    if not next_line.endswith('\\'):
        line += next_line.strip()
    else:
        line += next_line.strip()[:-1]
        line = merge_lines(line, fd)
    return line


def parse_sudoers(line):
    alias, _, members = line.partition('=')
    alias_type, alias_name = tuple(alias.split(maxsplit=1))
    return (alias_type.strip().lower(), {alias_name.strip().lower(): [member.strip().lower() for member in members.split(',')]})


def parse_line(fd):
    user_alias = {}
    cmnd_alias = {}
    host_alias = {}
    for line in fd:
        if line.strip().endswith('\\'):
            line = merge_lines(line.strip()[:-1], fd)
        if len(line.strip()) > 0 and not line.startswith('#'):
            alias_type, parsed_result_dict = parse_sudoers(line.strip())

            if alias_type == 'user_alias':
                user_alias.update(parsed_result_dict)
            elif alias_type == 'cmnd_alias':
                cmnd_alias.update(parsed_result_dict)
            elif alias_type == 'host_alias':
                host_alias.update(parsed_result_dict)
    return (user_alias, cmnd_alias, host_alias)


def main():
    parser = SudoersArgParser(description='Process a sudoers file.')
    args = parser.parse_args()

    LOG.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    with open(args.sudoers_file, 'r') as fd:
        user, cmnd, host = parse_line(fd)

    compare_to_hr_users(user)
    #print_table(user)


if __name__ == '__main__':
    main()

