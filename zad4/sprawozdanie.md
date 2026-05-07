# Sprawozdanie – Tryby pracy szyfrów blokowych

## 1. Pomiar czasów szyfrowania i deszyfrowania

### Kod źródłowy

```python
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
```

### Wyniki

```
Tryb   Rozmiar    Szyfr [ms]   Deszyfr [ms]
--------------------------------------------
ECB    1 KB            0.009          0.008
ECB    100 KB          0.025          0.023
ECB    10 MB           7.834          7.971

CBC    1 KB            0.028          0.029
CBC    100 KB          0.566          0.221
CBC    10 MB          20.750         23.153

OFB    1 KB            0.027          0.035
OFB    100 KB          0.329          0.322
OFB    10 MB          17.637         18.157

CFB    1 KB            0.030          0.026
CFB    100 KB          0.441          0.243
CFB    10 MB          21.206         20.762

CTR    1 KB            0.024          0.021
CTR    100 KB          0.090          0.086
CTR    10 MB           6.797          6.858
```

### Wnioski

- **ECB i CTR są zdecydowanie najszybsze** dla dużych plików (~7–8 ms na 10 MB). Obydwa tryby pozwalają na niezależne szyfrowanie/deszyfrowanie każdego bloku – biblioteka może korzystać z hardware'owych akceleratorów (AES-NI) w trybie wsadowym.
- **CBC, OFB i CFB są 2–3× wolniejsze** na dużych danych (~18–23 ms na 10 MB). Tryby te wymagają sekwencyjnego przetwarzania (każdy blok zależy od poprzedniego), co uniemożliwia pełną wektoryzację.
- Dla małych plików (1 KB) różnice są minimalne – dominuje narzut inicjalizacji obiektu szyfru, a nie sam czas szyfrowania danych.
- Mimo że CBC decrypt jest teoretycznie paralolelizowalne (szyfrogramy bloków są znane z góry), biblioteka pycryptodome nie wykorzystuje tej właściwości – czas deszyfrowania CBC jest zbliżony do szyfrowania.

---

## 2. Propagacja błędów

### Kod źródłowy

```python
#!/usr/bin/env python3
"""Zad. 2 - Analiza propagacji błędów w trybach AES."""

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
```

### Wyniki

```
Tekst jawny: 80 B (5 bloków po 16 B)
Błąd: bajt 23 szyfrogramu = blok nr 1

Tryb   Uszkodzone bloki  Opis propagacji
--------------------------------------------------------------
ECB                 [1]  (16 B uszkodzonych)
CBC              [1, 2]  (17 B uszkodzonych)
OFB                 [1]  (1 B uszkodzonych)
CFB              [1, 2]  (17 B uszkodzonych)
CTR                 [1]  (1 B uszkodzonych)
```

### Wnioski

| Tryb | Zakres uszkodzeń | Mechanizm |
|------|-----------------|-----------|
| ECB  | 1 blok (cały)  | Bloki niezależne – błąd izolowany |
| CBC  | 2 bloki        | C[i] używane jest jako XOR dla P[i] oraz jako wejście deszyfrowania C[i+1] |
| OFB  | 1 bajt         | Strumień klucza niezależny od szyfrogramu – flippowany bit przenosi się 1:1 |
| CFB  | 2 bloki        | C[i] podawane na wejście feedback – analogicznie do CBC |
| CTR  | 1 bajt         | Licznik niezależny od szyfrogramu – tak samo jak OFB |

- **OFB i CTR** wykazują propagację **bitową** (1:1): uszkodzony bit szyfrogramu powoduje uszkodzenie dokładnie jednego bitu tekstu jawnego. Reszta wiadomości pozostaje nieuszkodzona.
- **ECB** izoluje błąd do jednego bloku, ale każdy błąd niszczy cały blok (16 B).
- **CBC i CFB** mają propagację dwublokową: uszkodzony blok szyfrogramu powoduje całkowite zniszczenie odpowiadającego bloku tekstu jawnego (16 B) oraz propagację flippowanych bitów do kolejnego bloku (+1 B przy pojedynczym flipie bajtu).

---

## 3. Ręczna implementacja CBC przy użyciu ECB

### Kod źródłowy

```python
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
```

### Wynik działania

```
Wiadomość:           Testowa wiadomosc do weryfikacji implementacji CBC.
Szyfr (ręczny):      c83cec4de81ee55258211ee270f5e7c6e67e853bc64bfaa52ca3621affc86c7...
Szyfr (biblioteka):  c83cec4de81ee55258211ee270f5e7c6e67e853bc64bfaa52ca3621affc86c7...
Zgodność szyfrów:    True
Odszyfrowany tekst:  Testowa wiadomosc do weryfikacji implementacji CBC.
```

### Wnioski

Ręczna implementacja CBC wiernie odwzorowuje standard: szyfrowanie każdego bloku tekstu jawnego jest poprzedzone XOR z poprzednim blokiem szyfrogramu (lub IV dla pierwszego bloku), po czym blok jest szyfrowany trybem ECB. Wyniki są identyczne z wynikami biblioteki `pycryptodome` (`Zgodność szyfrów: True`), co potwierdza poprawność implementacji.

Implementacja CBC w oparciu o ECB jest naturalnym odzwierciedleniem definicji matematycznej trybu:

```
C[0] = ECB_Encrypt(P[0] XOR IV)
C[i] = ECB_Encrypt(P[i] XOR C[i-1])

P[0] = ECB_Decrypt(C[0]) XOR IV
P[i] = ECB_Decrypt(C[i]) XOR C[i-1]
```
