import random
import sympy

def coprime(a, b):
    return sympy.gcd(a, b) == 1


def generate_bbs_bits(length=20000):
    while True:
        p = sympy.randprime(1000, 10000)
        q = sympy.randprime(1000, 10000)
        if p != q and p % 4 == 3 and q % 4 == 3:
            break

    n = p * q

    while True:
        seed = random.randrange(2, n)
        if coprime(seed, n):
            break

    x = pow(seed, 2, n)
    bits = []
    for _ in range(length):
        x = pow(x, 2, n)
        bits.append(x % 2)

    return p, q, n, seed, bits


def monobit_test(bits):
    ones = sum(bits)
    passed = 9725 < ones < 10275
    print(f"Monobit test: ones={ones} -> {'PASS' if passed else 'FAIL'}")
    return passed


def poker_test(bits):
    m = 4
    k = len(bits) // m
    counts = [0] * (2**m)

    for i in range(k):
        value = 0
        for bit in bits[i * m : (i + 1) * m]:
            value = (value << 1) | bit
        counts[value] += 1

    x = (16 / k) * sum(c * c for c in counts) - k
    passed = 2.16 < x < 46.17
    print(f"Poker test: X={x:.4f} -> {'PASS' if passed else 'FAIL'}")
    return passed


def series_test(bits):
    series_zero = {i: 0 for i in range(1, 7)}
    series_one = {i: 0 for i in range(1, 7)}

    current = bits[0]
    length = 1

    for bit in bits[1:]:
        if bit == current:
            length += 1
        else:
            bucket = length if length < 6 else 6
            if current == 0:
                series_zero[bucket] += 1
            else:
                series_one[bucket] += 1
            current = bit
            length = 1

    # Count the last run.
    bucket = length if length < 6 else 6
    if current == 0:
        series_zero[bucket] += 1
    else:
        series_one[bucket] += 1

    limits = {
        1: (2315, 2685),
        2: (1114, 1386),
        3: (527, 723),
        4: (240, 384),
        5: (103, 209),
        6: (103, 209),
    }

    passed = True
    for run_len, (low, high) in limits.items():
        z_ok = low < series_zero[run_len] < high
        o_ok = low < series_one[run_len] < high
        if not (z_ok and o_ok):
            passed = False

    print("Series test:")
    print("  zeros:", series_zero)
    print("  ones :", series_one)
    print(f"  result: {'PASS' if passed else 'FAIL'}")
    return passed


def long_run_test(bits):
    max_run = 1
    current_run = 1

    for i in range(1, len(bits)):
        if bits[i] == bits[i - 1]:
            current_run += 1
            if current_run > max_run:
                max_run = current_run
        else:
            current_run = 1

    passed = max_run < 26
    print(f"Long run test: max_run={max_run} -> {'PASS' if passed else 'FAIL'}")
    return passed


def run_fips_tests(bits):
    print("\nRunning 4 FIPS tests\n")
    results = {
        "monobit": monobit_test(bits),
        "long_run": long_run_test(bits),
        "series": series_test(bits),
        "poker": poker_test(bits),
    }

    print("\nResults:")
    for name, passed in results.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    p, q, n, seed, bits = generate_bbs_bits(20000)

    print("p:", p)
    print("q:", q)
    print("N:", n)
    print("seed:", seed)

    with open("BBS.txt", "w") as f:
        f.write("".join(map(str, bits)))

    run_fips_tests(bits)
