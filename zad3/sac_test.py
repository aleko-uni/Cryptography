#!/usr/bin/env python3
"""Zad. 6 - Strict Avalanche Criteria dla SHA-256."""
import hashlib
import os
import random

SAMPLES = 5000
DIGEST_BITS = 256


def sha256_bits(data: bytes) -> list[int]:
    digest = hashlib.sha256(data).digest()
    return [(b >> (7 - i)) & 1 for b in digest for i in range(8)]


def flip_bit(data: bytes, bit_pos: int) -> bytes:
    arr = bytearray(data)
    byte_idx, bit_idx = divmod(bit_pos, 8)
    arr[byte_idx] ^= 1 << (7 - bit_idx)
    return bytes(arr)


def sac_analysis():
    INPUT_BITS = 64
    input_bytes = INPUT_BITS // 8

    # change_prob[i][j] = fraction of samples where output bit j changed
    # when input bit i was flipped
    change_counts = [[0] * DIGEST_BITS for _ in range(INPUT_BITS)]

    for _ in range(SAMPLES):
        original = os.urandom(input_bytes)
        bits_orig = sha256_bits(original)
        for i in range(INPUT_BITS):
            flipped = flip_bit(original, i)
            bits_flip = sha256_bits(flipped)
            for j in range(DIGEST_BITS):
                if bits_orig[j] != bits_flip[j]:
                    change_counts[i][j] += 1

    # Aggregate: for each input bit, average change probability across all output bits
    print(f"SAC – SHA-256 ({SAMPLES} próbek, {INPUT_BITS}-bitowe wejście)\n")
    print(f"{'Bit wejścia':<14} {'Śr. P(zmiana bitu wyjścia)':<30} {'Min P':<12} {'Max P'}")
    print("-" * 70)

    all_probs = []
    for i in range(INPUT_BITS):
        probs = [change_counts[i][j] / SAMPLES for j in range(DIGEST_BITS)]
        avg = sum(probs) / len(probs)
        all_probs.extend(probs)
        print(f"{i:<14} {avg:<30.4f} {min(probs):<12.4f} {max(probs):.4f}")

    global_avg = sum(all_probs) / len(all_probs)
    deviation = (sum((p - 0.5) ** 2 for p in all_probs) / len(all_probs)) ** 0.5
    print(f"\nGlobalna średnia P(zmiana): {global_avg:.4f}  (ideał: 0.5000)")
    print(f"Odchylenie std od ideału:   {deviation:.4f}  (im bliżej 0, tym lepiej)")

    # Histogram buckets
    buckets = [0] * 10
    for p in all_probs:
        idx = min(int(p * 10), 9)
        buckets[idx] += 1
    total = len(all_probs)
    print("\nRozkład prawdopodobieństw zmiany bitów wyjściowych:")
    for k, cnt in enumerate(buckets):
        lo, hi = k / 10, (k + 1) / 10
        bar = "#" * (cnt * 40 // total)
        print(f"  [{lo:.1f}-{hi:.1f}): {bar} {cnt}")


if __name__ == "__main__":
    sac_analysis()
