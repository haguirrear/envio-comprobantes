import logging
import zipfile
from pathlib import Path
import hashlib
import base64
from dataclasses import dataclass

from sunat_api.exceptions import FailHashFile, FailZipFile

logger = logging.getLogger(__name__)


def zip_single_file(zip_path: Path, filename: str):
    logger.debug(f"Zipping {filename}")

    try:
        with zipfile.ZipFile(str(zip_path), "w") as archive:
            archive.write(filename)
    except Exception as e:
        logger.exception("Fail to zip File")
        raise FailZipFile(str(e)) from e


@dataclass
class HashBase64:
    hash: str
    base64: str


def hash_base64_encode_file(filename: Path) -> HashBase64:
    sha256_hash = hashlib.sha256()
    base64_file = None
    try:
        with filename.open("rb") as f:
            file_bytes = f.read()
            sha256_hash.update(file_bytes)
            base64_file = base64.b64encode(file_bytes).decode("ASCII")

        hash = sha256_hash.hexdigest()
    except Exception as e:
        logger.exception("Fail to hash or encode base64 file")
        raise FailHashFile(str(e)) from e

    hash = HashBase64(hash=hash, base64=base64_file)
    return hash


def base64_to_file(base64_string: str, filepath: Path):
    with filepath.open("wb") as file:
        decoded_data = base64.decodebytes(base64_string.encode("ASCII"))
        file.write(decoded_data)