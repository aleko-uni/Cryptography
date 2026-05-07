#!/usr/bin/env python3
"""Zad. 1 - Pomiar czasów szyfrowania i deszyfrowania w 5 trybach AES."""

import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY   = os.urandom(16)
IV    = b'\x00' * 16
NONCE = b'\x00' * 8

NEEDS_PADDING = {'ECB', 'CBC'}


def make_cipher(mode: str):
    if mode == 'ECB': return AES.new(KEY, AES.MODE_ECB)
    if mode == 'CBC': return AES.new(KEY, AES.MODE_CBC, iv=IV)
    if mode == 'OFB': return AES.new(KEY, AES.MODE_OFB, iv=IV)
    if mode == 'CFB': return AES.new(KEY, AES.MODE_CFB, iv=IV, segment_size=128)
    if mode == 'CTR': return AES.new(KEY, AES.MODE_CTR, nonce=NONCE)


def encrypt(data: bytes, mode: str) -> bytes:
    c = make_cipher(mode)
    return c.encrypt(pad(data, 16) if mode in NEEDS_PADDING else data)


def decrypt(data: bytes, mode: str) -> bytes:
    c = make_cipher(mode)
    raw = c.decrypt(data)
    return unpad(raw, 16) if mode in NEEDS_PADDING else raw


def bench(size: int, mode: str, n: int) -> tuple[float, float]:
    data = os.urandom(size)
    ct   = encrypt(data, mode)

    t0 = time.perf_counter()
    for _ in range(n):
        encrypt(data, mode)
    enc_ms = (time.perf_counter() - t0) / n * 1000

    t0 = time.perf_counter()
    for _ in range(n):
        decrypt(ct, mode)
    dec_ms = (time.perf_counter() - t0) / n * 1000

    return enc_ms, dec_ms


SIZES = {'1 KB': 1_024, '100 KB': 102_400, '10 MB': 10_485_760}
MODES = ['ECB', 'CBC', 'OFB', 'CFB', 'CTR']

if __name__ == '__main__':
    print(f"{'Tryb':<6} {'Rozmiar':<8} {'Szyfr [ms]':>12} {'Deszyfr [ms]':>14}")
    print('-' * 44)
    for mode in MODES:
        for name, size in SIZES.items():
            iters = 20 if size <= 102_400 else 5
            e, d = bench(size, mode, iters)
            print(f"{mode:<6} {name:<8} {e:>12.3f} {d:>14.3f}")
        print()
