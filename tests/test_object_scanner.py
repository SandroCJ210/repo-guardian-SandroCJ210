import pytest
import zlib
from pathlib import Path
from src.guardian.object_scanner import read_loose, GitObject


FIXTURE_DIR = Path("fixtures/corrupt-blob.git/")

def find_loose_object_path():
    obj_dir = Path("fixtures/corrupt-blob.git/.git/objects")
    for subdir in obj_dir.iterdir():
        if subdir.name in ("info", "pack") or not subdir.is_dir():
            continue
        for obj_file in subdir.iterdir():
            return subdir / obj_file.name
    raise FileNotFoundError("No loose object found in corrupt-blob.git")


def test_valid_loose_object():
    obj_dir = Path("fixtures/corrupt-blob.git/.git/objects")
    if not obj_dir.exists():
        pytest.skip("Fixture not available — run generate_fixtures.py locally")

    obj_path = find_loose_object_path()
    obj = read_loose(obj_path)
    assert obj.type == "blob"
    assert obj.size == len(obj.content)


def test_missing_file():
    missing_path = FIXTURE_DIR / "ff" / "nonexistent"
    with pytest.raises(FileNotFoundError):
        read_loose(missing_path)


def test_invalid_compression():
    # Create a fake file with garbage content
    bad_path = Path("tests/temp_invalid_object")
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_bytes(b"not zlib")

    with pytest.raises(ValueError, match="Decompression failed"):
        read_loose(bad_path)

    bad_path.unlink()


def test_header_missing_separator(tmp_path):
    obj_data = zlib.compress(b"blob 10" + b"hello world")
    obj_file = tmp_path / "aa" / "badheader"
    obj_file.parent.mkdir(parents=True)
    obj_file.write_bytes(obj_data)

    with pytest.raises(ValueError, match="Missing null separator"):
        read_loose(obj_file)


def test_header_invalid_format(tmp_path):
    obj_data = zlib.compress(b"notvalid\0somecontent")
    obj_file = tmp_path / "aa" / "badformat"
    obj_file.parent.mkdir(parents=True)
    obj_file.write_bytes(obj_data)

    with pytest.raises(ValueError, match="Invalid header format"):
        read_loose(obj_file)


def test_size_mismatch(tmp_path):
    obj_data = zlib.compress(b"blob 5\0abc")
    obj_file = tmp_path / "aa" / "badsize"
    obj_file.parent.mkdir(parents=True)
    obj_file.write_bytes(obj_data)

    with pytest.raises(ValueError, match="does not match body size"):
        read_loose(obj_file)


def test_sha_mismatch(tmp_path):
    content = b"hello world"
    header = f"blob {len(content)}".encode()
    full_data = header + b"\x00" + content
    compressed = zlib.compress(full_data)

    wrong_path = tmp_path / "ab" / "cd1234567890"
    wrong_path.parent.mkdir(parents=True)
    wrong_path.write_bytes(compressed)

    with pytest.raises(ValueError, match="SHA mismatch"):
        read_loose(wrong_path)
