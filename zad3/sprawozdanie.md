# Sprawozdanie – Funkcje skrótu (hash)

## 1. Aplikacja do generowania skrótów

### Kod źródłowy

```python
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
```

### Wynik działania (wejście: `"cat"`)

```
Podaj tekst: cat

Wejście: 'cat'
--------------------------------------------------------------------------------
Algorytm       Długość (hex)    Skrót
--------------------------------------------------------------------------------
md5            32               d077f244def8a70e5ea758bd8352fcd8
sha1           40               9d989e8d27dc9e0ec3389fc855f142c3d40f0c50
sha224         56               3ec589d28a300699fc55cb8f0f8966e6e72e8105d24817ded2ad56f1
sha256         64               77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e
sha384         96               e7db74262dae60ad5a05a97fd0cd92ef25951e64aeaa762715c29f9d61ab25d6d6683e7172232619878790d8252e870a
sha512         128              4241b986a49591d445ebb840bc4b49c12b10b392b49222bc45dfd8b871cb3d0e742cdba152aa782e253026c7fc93fe8287b95c5fd0e22467e99c89501a502cd4
sha3_224       56               447c857980c93d613b8bd6897c05bfd0621245139f021aaa6b57830a
sha3_256       64               d616607d3e4ba96a74f323cffc5f20a3c78e7cab8ecbdbb03b13fa8ffc9bf644
sha3_384       96               9bb4adf3004b3ed61f76195321621eac835b6502db486a53b64fdb69c50ee1a8dbb05c950577db70be2bafed59f8891d
sha3_512       128              fe37dd66fa849ca98684160d542538b22c1edb576271d76b319ded4965d90143a0806fe1edf29b82b8740ec177880769629bdd1a0fb7cb97d7640e60c44833d3
```

---

## 2. Omówienie sposobu implementacji

Implementacja korzysta wyłącznie z modułu `hashlib` wbudowanego w bibliotekę standardową Pythona. Każdy algorytm jest wywoływany przez `hashlib.new(alg, data)`, co pozwala na zunifikowaną obsługę wszystkich funkcji skrótu.

**Uwzględnione algorytmy:**

| Rodzina | Warianty | Długość skrótu (bity) |
|---------|----------|----------------------|
| MD5     | md5      | 128                  |
| SHA-1   | sha1     | 160                  |
| SHA-2   | sha224, sha256, sha384, sha512 | 224, 256, 384, 512 |
| SHA-3   | sha3_224, sha3_256, sha3_384, sha3_512 | 224, 256, 384, 512 |

---

## 3. Rola soli w tworzeniu skrótów

**Sól** (ang. *salt*) to losowy ciąg bajtów dołączany do hasła przed obliczeniem skrótu: `hash(sól || hasło)`. Sól jest unikalna dla każdego użytkownika i przechowywana jawnie obok skrótu.

**Po co jest potrzebna?**

1. **Uniemożliwia ataki słownikowe na bazę hurtowo.** Bez soli każde (pojedyncze) hasło zawsze daje ten sam skrót – atakujący łamie wszystkich użytkowników z tym hasłem jednym trafieniem.
2. **Niweluje rainbow tables.** Tęczowe tablice to wstępnie obliczone pary `(hasło → skrót)`. Sól sprawia, że tabela musiałaby obejmować miliardy kombinacji `(hasło + losowa_sól)`, co jest praktycznie niemożliwe do obliczenia.
3. **Zapobiega identyfikacji identycznych haseł.** Dwóch użytkowników z tym samym hasłem będzie miało różne skróty, jeśli sól jest różna.

**Przykład (Python):**

```python
import hashlib, os

password = "cat"
salt = os.urandom(16)                        # 128 bitów losowości
hashed = hashlib.sha256(salt + password.encode()).hexdigest()
# Przechowuj: (salt.hex(), hashed)
```

W praktyce do haszowania haseł używa się dedykowanych funkcji (bcrypt, Argon2, scrypt) – są celowo **wolne**, co utrudnia ataki brute-force.

---

## 4. Bezpieczeństwo MD5 – czy MD5 jest funkcją bezpieczną?

### Odpowiedź: Nie – MD5 jest złamane kryptograficznie.

**MD5 nie nadaje się do żadnego zastosowania wymagającego odporności na kolizje.**

#### Udokumentowane złamania:

| Rok  | Zdarzenie |
|------|-----------|
| 1996 | Hans Dobbertin demonstrował słabości w strukturze wewnętrznej |
| 2004 | Wang i Yu opublikowali metodę znajdowania kolizji MD5 w czasie **krótszym niż godzina** na zwykłym komputerze |
| 2005 | Wykazano możliwość tworzenia kolizji z różnymi prefiksami (chosen-prefix collisions) |
| 2008 | Badacze stworzyli fałszywe **certyfikaty SSL X.509** zaufane przez przeglądarki, korzystając z kolizji MD5 – był to atak praktyczny na infrastrukturę PKI |
| 2012 | Malware **Flame** używał wybranego-prefiksu kolizji MD5 do podpisania złośliwego kodu certyfikatem Microsoftu |

#### Kiedy MD5 jest jeszcze „używalny"?

- Sumy kontrolne plików (nieintencjonalne błędy, nie manipulacja) – o ile atakujący nie ma możliwości zmodyfikowania pliku
- Szybki hashing wewnętrzny (np. cache-key, nie bezpieczeństwo)

**Do przechowywania haseł, podpisów cyfrowych, certyfikatów, MAC – MD5 jest całkowicie zdyskwalifikowane.**

---

## 5. Porównanie szybkości i długości skrótów (Zadanie 2)

### Kod źródłowy

```python
import hashlib, time, os

ALGORITHMS = [
    "md5", "sha1",
    "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
]
INPUT_SIZES = [10, 100, 1_000, 10_000, 100_000, 1_000_000]
ITERATIONS  = 200

for alg in ALGORITHMS:
    bits = hashlib.new(alg, b"x").digest_size * 8
    for size in INPUT_SIZES:
        data  = os.urandom(size)
        start = time.perf_counter()
        for _ in range(ITERATIONS):
            hashlib.new(alg, data).digest()
        ms = (time.perf_counter() - start) / ITERATIONS * 1000
        # wypisz ms
```

### Wyniki (czas w ms/wywołanie)

```
Algorytm       Długość skrótu (bity)       10B       100B      1000B     10000B    100000B   1000000B
------------------------------------------------------------------------------------------------------
md5            128                      0.0012ms  0.0012ms  0.0029ms  0.0201ms  0.1884ms  1.9782ms
sha1           160                      0.0011ms  0.0011ms  0.0017ms  0.0084ms  0.0745ms  0.7423ms
sha224         224                      0.0011ms  0.0011ms  0.0017ms  0.0090ms  0.0847ms  0.9266ms
sha256         256                      0.0012ms  0.0011ms  0.0017ms  0.0111ms  0.0971ms  0.8347ms
sha384         384                      0.0015ms  0.0013ms  0.0029ms  0.0196ms  0.1865ms  1.9382ms
sha512         512                      0.0013ms  0.0013ms  0.0029ms  0.0199ms  0.2086ms  1.9582ms
sha3_224       224                      0.0017ms  0.0017ms  0.0037ms  0.0260ms  0.2830ms  2.5779ms
sha3_256       256                      0.0015ms  0.0016ms  0.0039ms  0.0272ms  0.2732ms  2.7100ms
sha3_384       384                      0.0015ms  0.0014ms  0.0046ms  0.0353ms  0.3797ms  3.6827ms
sha3_512       512                      0.0015ms  0.0018ms  0.0060ms  0.0532ms  0.5214ms  5.0314ms
```

### Wniosek

- **SHA-1 i SHA-256 są najszybsze** w praktycznie każdej kategorii rozmiaru wejścia – korzystają z natywnych optymalizacji CPU (instrukcje SHA-NI na x86).
bezpieczeństwo kosztem wydajności i rozmiaru.

---

## 6. Skróty krótkich haseł (Zadanie 3)

### Kod i wyniki

```python
import hashlib

words = ["cat", "dog", "1234", "pass"]
for w in words:
    print(f"{w:<8} {hashlib.md5(w.encode()).hexdigest()}")
```

```
Słowo    MD5
cat      d077f244def8a70e5ea758bd8352fcd8
dog      06d80eb0c50b49a509b49f2424e8c805
1234     81dc9bdb52d04dc20036dbd8313ed055
pass     1a1dc91c907325c69271ddf0c944bc72
```

### Weryfikacja

Wszystkie cztery powyższe skróty MD5 są **natychmiast rozpoznawalne** przez powszechnie dostępne narzędzia:

- [CrackStation.net](https://crackstation.net) – darmowa baza skrótów (ponad 15 miliardów haseł)
- Proste wyszukiwanie Google hasza `d077f244def8a70e5ea758bd8352fcd8` zwraca wynik `"cat"` natychmiast.
- Tablice MD5 online pokrywają dosłownie wszystkie słowa do ~6 znaków oraz popularne wzorce.

### Co to mówi o bezpieczeństwie?

Krótkie lub popularne hasła w bazach danych **chronione wyłącznie skrótem MD5 (lub SHA-1) bez soli są praktycznie jawne tekstowe** wobec osoby, która uzyska dostęp do bazy:

1. **Brak entropii** – 3-4 znakowe hasło z ASCII drukowanego ma co najwyżej \~26 bitów entropii. Przeszukanie całej przestrzeni (\~67 mln kombinacji) zajmuje poniżej sekundy.
2. **Rainbow Tables** – dla niezasolonych MD5 istnieją gotowe tablice pokrywające wszystkie hasła do 8 znaków alfanumerycznych.

---

## 7. Kolizje na pierwszych 12 bitach SHA-256 (Zadanie 5)

### Kod źródłowy

```python
import hashlib, os, time

def prefix_12(data: bytes) -> int:
    d = hashlib.sha256(data).digest()
    return (d[0] << 4) | (d[1] >> 4)   # pierwsze 12 bitów

seen = {}
for _ in range(10_000):
    data   = os.urandom(8)
    prefix = prefix_12(data)
    if prefix in seen and seen[prefix] != data:
        print("KOLIZJA:", seen[prefix].hex(), "vs", data.hex())
        # ...
    else:
        seen[prefix] = data
```

### Wyniki

```
Szukam 5 kolizji na pierwszych 12 bitach SHA-256...

Kolizja #1 (po 164 próbach):
  wejście 1 : fac5b5c2fb3f3a80
  wejście 2 : ad971d905c85966e
  sha256(1) : 31128aa0e0f0dbd1e111289a1181f79f4ca9394ad03c0d31ab46c4cf795766cd
  sha256(2) : 3117f78ffe7036cd2594b88ca5395145a2ad32d7d9067458780e17c9eb8ade13
  pierwsze 12 bitów: 001100010001

Kolizja #2 (po 30 próbach):
  wejście 1 : 7feb723ba3d4f0c9
  wejście 2 : 908624ae58965e05
  sha256(1) : f9450ee23a79620e34f9e0f5345b09641bf9b9de546ed6491d3918192ea31b1e
  sha256(2) : f94c0312a48b5587525243cae1b5b268b5314ba13f4d8a84feec874825247a3f
  pierwsze 12 bitów: 111110010100

Kolizja #3 (po 59 próbach):
  wejście 1 : b0bf971857005d40
  wejście 2 : 8b9c053b053ca7e6
  sha256(1) : bd8b092970c09617f73b0e08b9505931268681b8d95a9b2fb8fe8008c920a886
  sha256(2) : bd89fb453923c772b4712bc5ff05a3b6d791a952c0c82873639cb902a7118e49
  pierwsze 12 bitów: 101111011000

Kolizja #4 (po 122 próbach):
  wejście 1 : 1af12153ccc224c9
  wejście 2 : 0c7a9874c97aa1eb
  sha256(1) : c10db3d9272e2b0e683afd5bae7e2ec46db70ba0addc4485709cc107952f7b05
  sha256(2) : c10f4e685ca9794ac2fa11a9adfa3543fdd3bf7bd72c7238281e15c1820cdee3
  pierwsze 12 bitów: 110000010000

Kolizja #5 (po 72 próbach):
  wejście 1 : abd645329484d37d
  wejście 2 : 7846e52baa78ceee
  sha256(1) : 9d248dbed2ba85dda15d8a86437bf9b566e33e522239b03e289fb265664e9927
  sha256(2) : 9d2f06ae657edaa870759d9ede7af2a47bfdea3131c3a5f4bb1973d321e488e4
  pierwsze 12 bitów: 100111010010

Łączny czas: 0.001s
Oczekiwana liczba prób (birthday): ~64
```

### Wnioski

- **Paradoks urodzin**: dla przestrzeni 2¹² = 4096 możliwych prefiksów, kolizja jest oczekiwana już po **√4096 ≈ 64 próbach**. Wyniki eksperymentu (30–164 prób) są zgodne z teorią – losowość narzuca duże odchylenia między poszczególnymi przypadkami.
- **Obcięte skróty są słabsze**: 12-bitowy skrót z SHA-256 jest tak słaby jak 12-bitowa funkcja skrótu – mimo że SHA-256 jest kryptograficznie bezpieczny. Skróty nie powinny być obcinane poniżej ~128 bitów.
- Potwierdzono, że SHA-256 zachowuje się losowo – prefiks rozkłada się równomiernie, a kolizje pojawiają się zgodnie z modelem matematycznym.

---

## 8. Strict Avalanche Criteria (SAC) – SHA-256 (Zadanie 6)

### Kod źródłowy

```python
import hashlib, os

SAMPLES = 5000

def sha256_bits(data):
    d = hashlib.sha256(data).digest()
    return [(b >> (7 - i)) & 1 for b in d for i in range(8)]

def flip_bit(data, bit_pos):
    arr = bytearray(data)
    byte_idx, bit_idx = divmod(bit_pos, 8)
    arr[byte_idx] ^= 1 << (7 - bit_idx)
    return bytes(arr)

# Dla każdego bitu wejścia (64 bity = 8 bajtów):
# 1. Losuj wejście, oblicz skrót
# 2. Odwróć bit i, oblicz skrót
# 3. Zlicz, które bity wyjścia się zmieniły
```

### Wyniki

```
SAC – SHA-256 (5000 próbek, 64-bitowe wejście)

Bit wejścia    Śr. P(zmiana bitu wyjścia)     Min P        Max P
----------------------------------------------------------------------
0              0.5005                         0.4784       0.5184
1              0.5007                         0.4780       0.5278
2              0.4996                         0.4812       0.5216
...            ...                            ...          ...
63             0.4998                         0.4814       0.5232

Globalna średnia P(zmiana): 0.5000  (ideał: 0.5000)
Odchylenie std od ideału:   0.0071  (im bliżej 0, tym lepiej)

Rozkład prawdopodobieństw zmiany bitów wyjściowych:
  [0.0-0.1):  0
  [0.1-0.2):  0
  [0.2-0.3):  0
  [0.3-0.4):  0
  [0.4-0.5): ####################  8078
  [0.5-0.6): ####################  8306
  [0.6-0.7):  0
  [0.7-0.8):  0
  [0.8-0.9):  0
  [0.9-1.0):  0
```

### Wnioski – SAC dla SHA-256

- **SHA-256 spełnia SAC niemal idealnie.** Globalna średnia prawdopodobieństwa zmiany bitu wyjściowego wynosi **0.5000** przy odchyleniu standardowym **0.0071** – wartości te są statystycznie nieodróżnialne od idealnego rzutu monetą.
- **Efekt lawinowy jest silny i symetryczny.** Zmiana dowolnego pojedynczego bitu wejścia zmienia losowo i niezależnie każdy bit wyjścia z prawdopodobieństwem ~50%, co jest pożądaną własnością kryptograficzną.
- **Brak korelacji** – żaden bit wejściowy nie wyróżnia się: wartości min/max mieszczą się w wąskim przedziale [0.47, 0.53], czyli fluktuacje wynikają wyłącznie ze skończonej próby statystycznej.
- **Rozkład prawdopodobieństw** jest skoncentrowany wąsko wokół 0.5 – brak jakichkolwiek wartości ekstremalnych (<0.4 lub >0.6), co potwierdza brak stronniczo słabych pozycji bitowych.
- **Praktyczne znaczenie SAC:** Funkcja skrótu spełniająca SAC jest odporna na ataki różnicowe – atakujący nie może wnioskować o różnicach na wejściu na podstawie obserwacji różnic na wyjściu.
