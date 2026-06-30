"""JSON helpers module.

This module provides JSON and JSONL file parsing and serialization utilities.
"""

from collections.abc import Iterable, Iterator
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from .logging import get_logger

_LOGGER = get_logger('helper.jsonl')


def load_json(string: str) -> dict | None:
    """Load item from json string.

    Args:
        string (str): JSON string to parse.

    Returns:
        dict | None: Parsed dictionary, or None if parsing failed.
    """
    try:
        return loads(string)
    except JSONDecodeError:
        _LOGGER.exception("failed to decode jsonl data!")
    return None


def dump_json(item: dict) -> str:
    """Dump item to json string.

    Args:
        item (dict): Dictionary to serialize.

    Returns:
        str: Compact JSON string representation.
    """
    return dumps(item, separators=(',', ':'))


def load_jsonl(filepath: Path) -> Iterator[dict]:
    """Load jsonl encoded data from file.

    Args:
        filepath (Path): Path to the JSONL file to read.

    Yields:
        dict: Each parsed JSON object from the file as a dictionary.
    """
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
    """Dump jsonl encoded data to file.

    Args:
        filepath (Path): Path to the JSONL file to write.
        items (Iterable[dict]): Iterable of dictionaries to write as JSONL.
    """
    _LOGGER.info("dumping jsonl data to %s", filepath)
    with filepath.open('w', encoding='utf-8') as fobj:
        for item in items:
            fobj.write(dump_json(item))
            fobj.write('\n')
