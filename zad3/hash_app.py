#!/usr/bin/env python3
"""Zad. 1 - Aplikacja do generowania skrótów kryptograficznych."""
import hashlib

ALGORITHMS = [
    "md5",
    "sha1",
    "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
]

def compute_hashes(text: str) -> dict[str, str]:
    encoded = text.encode("utf-8")
    return {alg: hashlib.new(alg, encoded).hexdigest() for alg in ALGORITHMS}

def print_hashes(text: str) -> None:
    print(f"\nWejście: {text!r}")
    print("-" * 80)
    print(f"{'Algorytm':<14} {'Długość (hex)':<16} Skrót")
    print("-" * 80)
    for alg, digest in compute_hashes(text).items():
        print(f"{alg:<14} {len(digest):<16} {digest}")

if __name__ == "__main__":
    text = input("Podaj tekst: ")
    print_hashes(text)
