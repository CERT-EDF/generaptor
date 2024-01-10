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


def dump_list(lst):
    return dumps(sorted(lst), separators=(',',':'))


def app():
    # parse rules
    group_ruleids = defaultdict(set)
    all_ruleids = set()
    with RULES.open(newline='') as rules_fp:
        csv_reader = reader(
            rules_fp,
            delimiter=DELIMITER,
            quotechar=QUOTECHAR,
        )
        next(csv_reader)  # skip header
        for row in csv_reader:
            rule_id = int(row[0])
            all_ruleids.add(rule_id)
            group_ruleids[row[2]].add(rule_id)
    # write targets
    with TARGETS.open('w', newline='') as targets_fp:
        csv_writer = writer(
            targets_fp,
            delimiter=DELIMITER,
            quotechar=QUOTECHAR,
            quoting=QUOTE_MINIMAL,
        )
        csv_writer.writerow(['Group', 'RuleIds'])
        for group, ruleids in group_ruleids.items():
            csv_writer.writerow([group, dump_list(ruleids)])
        csv_writer.writerow(['LinuxTriage', dump_list(all_ruleids)])


if __name__ == '__main__':
    app()
