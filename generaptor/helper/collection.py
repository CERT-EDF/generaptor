"""Collection archive helper
"""
from json import loads
from zipfile import ZipFile
from pathlib import Path


def collection_metadata(archive: Path):
    """Load JSON metadata from archive"""
    with ZipFile(archive) as zipf:
        try:
            zipinf = zipf.getinfo('metadata.json')
        except KeyError:
            return None
        data = zipf.read(zipinf)
        metadata_objects = loads(data.decode())
        return metadata_objects[0]
