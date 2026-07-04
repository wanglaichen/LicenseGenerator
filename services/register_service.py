import hashlib


MACHINE_MD5_SUFFIX = "_zhuojinchangzhou"

IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
]

IP_1 = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
]

PC_1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4,
]

PC_2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
]

EXPANSION = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1,
]

PBOX = [16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10, 2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25]

SBOX = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ],
]

LEFT_MOVES = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


def _latin1_bytes(value: str) -> bytes:
    return str(value).encode("latin1", errors="replace")


def _permute(value: int, table: list[int], source_bits: int) -> int:
    result = 0
    for position in table:
        result = (result << 1) | ((value >> (source_bits - position)) & 1)
    return result


def _left_rotate(value: int, shift: int, bits: int = 28) -> int:
    mask = (1 << bits) - 1
    return ((value << shift) & mask) | (value >> (bits - shift))


def _subkeys(key: bytes) -> list[int]:
    key_bits = int.from_bytes(key, "big")
    selected = _permute(key_bits, PC_1, 64)
    c = (selected >> 28) & 0x0FFFFFFF
    d = selected & 0x0FFFFFFF
    result = []

    for shift in LEFT_MOVES:
        c = _left_rotate(c, shift)
        d = _left_rotate(d, shift)
        result.append(_permute((c << 28) | d, PC_2, 56))

    return result


def _round_function(right: int, subkey: int) -> int:
    expanded = _permute(right, EXPANSION, 32) ^ subkey
    substituted = 0

    for index in range(8):
        six_bits = (expanded >> (42 - index * 6)) & 0x3F
        row = ((six_bits & 0x20) >> 4) | (six_bits & 0x01)
        column = (six_bits >> 1) & 0x0F
        substituted = (substituted << 4) | SBOX[index][row][column]

    return _permute(substituted, PBOX, 32)


def _des_encrypt_block(block: bytes, subkeys: list[int]) -> bytes:
    data = _permute(int.from_bytes(block, "big"), IP, 64)
    left = (data >> 32) & 0xFFFFFFFF
    right = data & 0xFFFFFFFF

    for subkey in subkeys:
        left, right = right, left ^ _round_function(right, subkey)

    encrypted = _permute((right << 32) | left, IP_1, 64)
    return encrypted.to_bytes(8, "big")


def xdes_hex(text: str, key: str) -> str:
    data = _latin1_bytes(text)
    key_bytes = _latin1_bytes(key)

    if not data:
        raise ValueError("请输入 SN。")
    if len(key_bytes) != 8:
        raise ValueError("密钥必须是 8 个 Latin-1 字节，旧版默认值为 tech2000。")

    padding_len = (-len(data)) % 8
    if padding_len:
        data += b"\x00" * padding_len

    subkeys = _subkeys(key_bytes)
    encrypted = b"".join(_des_encrypt_block(data[index:index + 8], subkeys) for index in range(0, len(data), 8))
    return encrypted.hex()


def machine_md5(
    machine_code: str,
    md5_length: int | None = None,
    suffix: str = MACHINE_MD5_SUFFIX,
) -> str:
    normalized = str(machine_code).strip()
    machine_bytes = _latin1_bytes(normalized)
    suffix_bytes = _latin1_bytes(suffix)
    length = len(machine_bytes) if md5_length is None else int(md5_length)

    if length < 0:
        raise ValueError("MD5 长度不能为负数。")

    buffer = machine_bytes + suffix_bytes
    return hashlib.md5(buffer[:length]).hexdigest()


def generate_machine_md5_payload(
    machine_code: str,
    md5_length: int | None = None,
) -> dict:
    normalized_machine_code = str(machine_code).strip()
    machine_bytes = _latin1_bytes(normalized_machine_code)
    effective_length = len(machine_bytes) if md5_length is None else int(md5_length)

    return {
        "machine_code": normalized_machine_code,
        "machine_md5_suffix": MACHINE_MD5_SUFFIX,
        "md5_length": effective_length,
        "machine_md5": machine_md5(
            normalized_machine_code,
            md5_length=md5_length,
        ),
        "compatibility_note": (
            f"复刻旧版 genbtn_2：先拼接 {MACHINE_MD5_SUFFIX!r}，"
            f"再按长度 {effective_length} 截断后做 MD5。"
            "C++ 原版长度取 innerGetMachineCode()（硬盘序列号）字节数；"
            "可通过 md5_length 手动指定。"
        ),
    }


def generate_register_payload(sn: str, key: str) -> dict:
    normalized_sn = str(sn).strip()

    return {
        "sn": normalized_sn,
        "key": key,
        "activation_code": xdes_hex(normalized_sn, key),
        "compatibility_note": (
            "复刻旧版 genbtn：对注册码输入执行 DES/XDES，"
            "密钥默认使用内置密钥，明文按 8 字节分组并以 0x00 补齐，"
            "输出小写十六进制激活码。"
        ),
    }


def generate_payload(
    machine_code: str,
    sn: str,
    key: str,
    md5_length: int | None = None,
) -> dict:
    md5_result = generate_machine_md5_payload(
        machine_code=machine_code,
        md5_length=md5_length,
    )
    register_result = generate_register_payload(sn=sn, key=key)

    return {
        "machine_code": md5_result["machine_code"],
        "sn": register_result["sn"],
        "key": register_result["key"],
        "machine_md5_suffix": md5_result["machine_md5_suffix"],
        "md5_length": md5_result["md5_length"],
        "machine_md5": md5_result["machine_md5"],
        "register_code": register_result["activation_code"],
        "activation_code": register_result["activation_code"],
        "compatibility_note": (
            f"{md5_result['compatibility_note']} "
            f"{register_result['compatibility_note']}"
        ),
    }
