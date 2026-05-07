#!/usr/bin/env python3
"""Zad. 5 - Kolizje na pierwszych 12 bitach skrótu SHA-256."""
import hashlib
import os
import time

MASK_BITS = 12


def prefix_12(data: bytes) -> int:
    digest = hashlib.sha256(data).digest()
    return (digest[0] << 4) | (digest[1] >> 4)


def find_collisions(target_pairs: int = 5):
    seen: dict[int, bytes] = {}
    collisions_found = 0
    attempts = 0
    results = []

    print(f"Szukam {target_pairs} kolizji na pierwszych {MASK_BITS} bitach SHA-256...\n")
    start = time.perf_counter()

    while collisions_found < target_pairs:
        data = os.urandom(8)
        prefix = prefix_12(data)
        attempts += 1

        if prefix in seen and seen[prefix] != data:
            m1, m2 = seen[prefix], data
            h1 = hashlib.sha256(m1).hexdigest()
            h2 = hashlib.sha256(m2).hexdigest()
            results.append((m1.hex(), m2.hex(), h1, h2))
            collisions_found += 1
            print(f"Kolizja #{collisions_found} (po {attempts} próbach):")
            print(f"  wejście 1 : {m1.hex()}")
            print(f"  wejście 2 : {m2.hex()}")
            print(f"  sha256(1) : {h1}")
            print(f"  sha256(2) : {h2}")
            print(f"  pierwsze 12 bitów: {bin(prefix_12(m1))[2:].zfill(12)}")
            print()
            seen = {}
            attempts = 0
        else:
            seen[prefix] = data

    elapsed = time.perf_counter() - start
    print(f"Łączny czas: {elapsed:.3f}s")
    expected = 2 ** (MASK_BITS / 2)
    print(f"Oczekiwana liczba prób (birthday): ~{expected:.0f}")


if __name__ == "__main__":
    find_collisions()
