#!/usr/bin/env python3
"""Generate linux.targets.csv from linux.rules.csv
"""
from csv import reader, writer, QUOTE_MINIMAL
from json import dumps
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
RULES = HERE / 'linux.rules.csv'
TARGETS = HERE / 'linux.targets.csv'
DELIMITER = ','
QUOTECHAR = '"'
LINETERMINATOR = '\n'


def _dump_list(lst):
    return dumps(sorted(lst), separators=(',', ':'))


def app():
    """Main routine"""
    # parse rules
    all_rids = set()
    group_rids = defaultdict(set)
    with RULES.open(newline='') as rules_fp:
        csv_reader = reader(
            rules_fp,
            delimiter=DELIMITER,
            quotechar=QUOTECHAR,
        )
        next(csv_reader)  # skip header
        for row in csv_reader:
            rid, group = int(row[0]), row[2]
            all_rids.add(rid)
            group_rids[group].add(rid)
    # write targets
    with TARGETS.open('w', newline='', encoding='utf-8') as targets_fp:
        csv_writer = writer(
            targets_fp,
            delimiter=DELIMITER,
            quotechar=QUOTECHAR,
            lineterminator=LINETERMINATOR,
            quoting=QUOTE_MINIMAL,
        )
        csv_writer.writerow(['Group', 'RuleIds'])
        for group in sorted(group_rids.keys()):
            csv_writer.writerow([group, _dump_list(group_rids[group])])
        # add hardcoded target
        csv_writer.writerow(['Triage/Full', _dump_list(all_rids)])


if __name__ == '__main__':
    app()
