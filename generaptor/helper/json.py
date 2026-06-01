"""JSON helpers"""

from collections.abc import Iterable, Iterator
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from .logging import get_logger

_LOGGER = get_logger('helper.jsonl')


def load_json(string: str) -> dict | None:
    """Load item from json string"""
    try:
        return loads(string)
    except JSONDecodeError:
        _LOGGER.exception("failed to decode jsonl data!")
    return None


def dump_json(item: dict) -> str:
    """Dump item to json string"""
    return dumps(item, separators=(',', ':'))


def load_jsonl(filepath: Path) -> Iterator[dict]:
    """Load jsonl encoded data from file"""
    _LOGGER.info("loading jsonl data from %s", filepath)
    with filepath.open('r', encoding='utf-8') as fobj:
        for line in fobj:
            line = line.strip()
            if not line:
                continue
            item = load_json(line)
            if not item:
                continue
            yield item


def dump_jsonl(filepath: Path, items: Iterable[dict]):
    """Dump jsonl encoded data to file"""
    _LOGGER.info("dumping jsonl data to %s", filepath)
    with filepath.open('w', encoding='utf-8') as fobj:
        for item in items:
            fobj.write(dump_json(item))
            fobj.write('\n')
