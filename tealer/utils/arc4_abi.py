from Cryptodome.Hash import SHA512


def get_method_selector(method_signature: str) -> str:
    hash_obj = SHA512.new(truncate="256")
    hash_obj.update(method_signature.encode("utf-8"))
    return f"0x{hash_obj.hexdigest()[:8]}"
