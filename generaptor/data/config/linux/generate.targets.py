#!/usr/bin/env python3
"""Generate targets.csv from rules.csv"""
from collections import defaultdict
from collections.abc import Iterator
from csv import DictReader, DictWriter
from json import dumps
from pathlib import Path

RULES = Path('rules.csv')
TARGETS = Path('targets.csv')
DELIMITER = ','
QUOTECHAR = '"'
LINETERMINATOR = '\n'


IdSet = set[int]
Record = dict[str, str]
RecordIterator = Iterator[Record]


def _read_csv(filepath: Path) -> RecordIterator:
    with filepath.open('r', encoding='utf-8', newline='') as fobj:
        reader = DictReader(fobj)
        yield from reader


def _write_csv(filepath: Path, fieldnames: list[str], records: RecordIterator):
    with filepath.open('w', encoding='utf-8', newline='') as fobj:
        writer = DictWriter(
            fobj,
            fieldnames,
            delimiter=DELIMITER,
            quotechar=QUOTECHAR,
            lineterminator=LINETERMINATOR,
        )
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def _dumps(items) -> str:
    return dumps(sorted(items), separators=(',', ':'))


def _generate_rows(
    rules_all: IdSet,
    rules_by_group: dict[str, IdSet],
) -> RecordIterator:
    for group in sorted(rules_by_group.keys()):
        yield {'Group': group, 'RuleIds': _dumps(rules_by_group[group])}
    yield {'Group': 'Triage/Full', 'RuleIds': _dumps(rules_all)}


def app():
    """Main routine"""
    # parse rules
    rules_all = set()
    rules_by_group = defaultdict(set)
    for record in _read_csv(RULES):
        rid, group = int(record['Id']), record['Category']
        rules_all.add(rid)
        rules_by_group[group].add(rid)
    # write targets
    _write_csv(
        TARGETS,
        ['Group', 'RuleIds'],
        _generate_rows(rules_all, rules_by_group),
    )


if __name__ == '__main__':
    app()
