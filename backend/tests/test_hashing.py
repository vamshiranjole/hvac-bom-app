import hashlib

def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

def test_same_input_same_hash():
    assert sha256_bytes(b"hello") == sha256_bytes(b"hello")

def test_different_input_different_hash():
    assert sha256_bytes(b"hello") != sha256_bytes(b"world")

def test_hash_format():
    result = sha256_bytes(b"test")
    assert result.startswith("sha256:")
    assert len(result) == 71
