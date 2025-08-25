"""CSV helper"""

from csv import reader
from pathlib import Path


def stream_csv(csv_filepath: Path):
    """Yield rows from CSV file"""
    with csv_filepath.open(newline='') as csv_fp:
        csv_reader = reader(csv_fp, delimiter=',', quotechar='"')
        try:
            next(csv_reader)  # skip csv header
        except StopIteration:
            return
        yield from csv_reader
