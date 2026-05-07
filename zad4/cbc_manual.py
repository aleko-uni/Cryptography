#!/usr/bin/env python3
"""Zad. 3 - Ręczna implementacja trybu CBC przy użyciu trybu ECB."""

import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

B = AES.block_size  # 16


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    blocks = pad(plaintext, B)
    prev, ct = iv, b''
    for i in range(0, len(blocks), B):
        block = xor_bytes(blocks[i:i + B], prev)
        prev  = AES.new(key, AES.MODE_ECB).encrypt(block)
        ct   += prev
    return ct


def cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    prev, pt = iv, b''
    for i in range(0, len(ciphertext), B):
        block = ciphertext[i:i + B]
        dec   = AES.new(key, AES.MODE_ECB).decrypt(block)
        pt   += xor_bytes(dec, prev)
        prev  = block
    return unpad(pt, B)


if __name__ == '__main__':
    key = os.urandom(16)
    iv  = os.urandom(16)
    msg = b'Testowa wiadomosc do weryfikacji implementacji CBC.'

    ct_manual = cbc_encrypt(msg, key, iv)
    pt_manual = cbc_decrypt(ct_manual, key, iv)

    ct_lib = AES.new(key, AES.MODE_CBC, iv=iv).encrypt(pad(msg, B))

    print(f"Wiadomość:           {msg.decode()}")
    print(f"Szyfr (ręczny):      {ct_manual.hex()}")
    print(f"Szyfr (biblioteka):  {ct_lib.hex()}")
    print(f"Zgodność szyfrów:    {ct_manual == ct_lib}")
    print(f"Odszyfrowany tekst:  {pt_manual.decode()}")
