#!/usr/bin/env python3
"""Zad. 3 - Skrót krótkiego hasła + demonstracja zagrożenia."""
import hashlib

words = ["cat", "dog", "1234", "pass"]

print(f"{'Słowo':<8} {'MD5':}")
print("-" * 44)
for w in words:
    h = hashlib.md5(w.encode()).hexdigest()
    print(f"{w:<8} {h}")

print()
print("Sprawdź powyższe skróty np. na: https://crackstation.net")
print("lub wyszukując MD5 w Google – większość zostanie natychmiast rozpoznana.")
