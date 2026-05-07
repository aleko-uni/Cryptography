#!/usr/bin/env python3
"""Zad. 2 - Analiza propagacji błędów w trybach AES (ECB, CBC, OFB, CFB, CTR)."""

import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

KEY   = os.urandom(16)
IV    = b'\x00' * 16
NONCE = b'\x00' * 8
B     = AES.block_size  # 16


def encrypt(data: bytes, mode: str) -> bytes:
    if mode == 'ECB': return AES.new(KEY, AES.MODE_ECB).encrypt(pad(data, B))
    if mode == 'CBC': return AES.new(KEY, AES.MODE_CBC, iv=IV).encrypt(pad(data, B))
    if mode == 'OFB': return AES.new(KEY, AES.MODE_OFB, iv=IV).encrypt(pad(data, B))
    if mode == 'CFB': return AES.new(KEY, AES.MODE_CFB, iv=IV, segment_size=128).encrypt(pad(data, B))
    if mode == 'CTR': return AES.new(KEY, AES.MODE_CTR, nonce=NONCE).encrypt(pad(data, B))


def decrypt_raw(data: bytes, mode: str) -> bytes:
    if mode == 'ECB': return AES.new(KEY, AES.MODE_ECB).decrypt(data)
    if mode == 'CBC': return AES.new(KEY, AES.MODE_CBC, iv=IV).decrypt(data)
    if mode == 'OFB': return AES.new(KEY, AES.MODE_OFB, iv=IV).decrypt(data)
    if mode == 'CFB': return AES.new(KEY, AES.MODE_CFB, iv=IV, segment_size=128).decrypt(data)
    if mode == 'CTR': return AES.new(KEY, AES.MODE_CTR, nonce=NONCE).decrypt(data)


def flip_byte(data: bytes, pos: int) -> bytes:
    arr = bytearray(data)
    arr[pos] ^= 0xFF
    return bytes(arr)


def bad_blocks(orig: bytes, dec: bytes) -> list[int]:
    return [i // B for i in range(0, min(len(orig), len(dec)), B)
            if orig[i:i + B] != dec[i:i + B]]


PLAINTEXT = b'X' * (B * 5)   # 5 bloków = 80 B
FLIP_POS  = B + 7             # bajt #23 — środek bloku nr 1

if __name__ == '__main__':
    plain_padded = pad(PLAINTEXT, B)
    print(f"Tekst jawny: {len(PLAINTEXT)} B ({len(PLAINTEXT) // B} bloków po {B} B)")
    print(f"Błąd: bajt {FLIP_POS} szyfrogramu = blok nr {FLIP_POS // B}\n")
    print(f"{'Tryb':<6} {'Uszkodzone bloki':>16}  Opis propagacji")
    print('-' * 62)

    for mode in ('ECB', 'CBC', 'OFB', 'CFB', 'CTR'):
        ct     = encrypt(PLAINTEXT, mode)
        ct_err = flip_byte(ct, FLIP_POS)
        dec    = decrypt_raw(ct_err, mode)
        blocks = bad_blocks(plain_padded, dec)

        corrupted_bytes = sum(
            sum(1 for a, b in zip(plain_padded[i:i+B], dec[i:i+B]) if a != b)
            for i in range(0, min(len(plain_padded), len(dec)), B)
        )

        print(f"{mode:<6} {str(blocks):>16}  ({corrupted_bytes} B uszkodzonych)")
