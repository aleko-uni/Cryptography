#!/usr/bin/env python3
"""Zad. 2 - Porównanie szybkości i długości skrótów."""
import hashlib
import time
import os

ALGORITHMS = [
    "md5", "sha1",
    "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
]

INPUT_SIZES = [10, 100, 1_000, 10_000, 100_000, 1_000_000]
ITERATIONS = 200

def benchmark():
    print(f"\n{'Algorytm':<14} {'Długość skrótu (bity)':<24}", end="")
    for size in INPUT_SIZES:
        label = f"{size}B"
        print(f"  {label:>10}", end="")
    print()
    print("-" * (14 + 24 + len(INPUT_SIZES) * 12))

    for alg in ALGORITHMS:
        bits = hashlib.new(alg, b"x").digest_size * 8
        print(f"{alg:<14} {bits:<24}", end="")
        for size in INPUT_SIZES:
            data = os.urandom(size)
            start = time.perf_counter()
            for _ in range(ITERATIONS):
                hashlib.new(alg, data).digest()
            elapsed = time.perf_counter() - start
            ms_per_call = (elapsed / ITERATIONS) * 1000
            print(f"  {ms_per_call:>9.4f}ms", end="")
        print()

if __name__ == "__main__":
    print("Czas haszowania (ms/wywołanie) dla różnych rozmiarów danych wejściowych:")
    benchmark()
