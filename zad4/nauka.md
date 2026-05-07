# Tryby pracy szyfrów blokowych – materiał edukacyjny

## Czym jest szyfr blokowy?

Szyfr blokowy (np. AES) przyjmuje na wejściu dokładnie **n bitów** tekstu jawnego i klucz, a zwraca **n bitów** szyfrogramu. AES ma rozmiar bloku 128 bitów (16 bajtów). Problem polega na tym, że prawdziwe wiadomości są dłuższe niż jeden blok – stąd potrzeba **trybów pracy**, które definiują, jak szyfrować sekwencję bloków.

---

## Tryb ECB (Electronic Code Book)

### Jak działa?

```
P[0] → [AES_E(K)] → C[0]
P[1] → [AES_E(K)] → C[1]
P[2] → [AES_E(K)] → C[2]
```

Każdy blok szyfrowany niezależnie tym samym kluczem. Nie ma żadnej zależności między blokami.

### Wzory

```
Szyfrowanie:  C[i] = AES_E(K, P[i])
Deszyfrowanie: P[i] = AES_D(K, C[i])
```

### Dlaczego ECB jest słaby?

Identyczne bloki tekstu jawnego dają **identyczne bloki szyfrogramu**. To oznacza, że struktury w danych są widoczne w szyfrogramie. Klasyczny przykład to bitmapa z pingwinem Tux – po zaszyfrowaniu ECB kontury zwierzęcia pozostają widoczne.

### Propagacja błędów

Błąd w C[i] niszczy tylko P[i] (16 bajtów). Pozostałe bloki są nienaruszone.

### Kiedy używać?

Tylko gdy szyfrowana jest dokładnie jedna porcja danych nie dłuższa niż jeden blok (np. szyfrowanie klucza sesyjnego). Nigdy do szyfrowania dłuższych wiadomości.

---

## Tryb CBC (Cipher Block Chaining)

### Jak działa?

Każdy blok tekstu jawnego jest najpierw XOR-owany z poprzednim blokiem szyfrogramu, a dopiero potem szyfrowany. Dla pierwszego bloku używany jest **wektor inicjalizujący IV** (Initialization Vector).

```
         IV
          ↓
P[0] → [XOR] → [AES_E(K)] → C[0]
                                ↘
P[1] →      → [XOR] → [AES_E(K)] → C[1]
                                       ↘
P[2] →           → [XOR] → [AES_E(K)] → C[2]
```

### Wzory

```
Szyfrowanie:  C[0] = AES_E(K, P[0] XOR IV)
              C[i] = AES_E(K, P[i] XOR C[i-1])

Deszyfrowanie: P[0] = AES_D(K, C[0]) XOR IV
               P[i] = AES_D(K, C[i]) XOR C[i-1]
```

### Właściwości

- Identyczne bloki tekstu jawnego → różne bloki szyfrogramu (IV i łańcuch zapewniają zróżnicowanie).
- **IV musi być losowy i nieprzewidywalny** dla każdej wiadomości; nie musi być tajny.
- Szyfrowanie jest **sekwencyjne** – nie można zrównoleglić (C[i] zależy od C[i-1]).
- Deszyfrowanie można zrównoleglić (wszystkie C[i] są znane).
- Wymaga dopełnienia (padding) do wielokrotności rozmiaru bloku.

### Propagacja błędów

Błąd w C[i]:
- P[i] zostaje całkowicie zniszczony (AES_D(C[i]') daje losowy wynik → XOR z C[i-1] → 16 B śmieci).
- P[i+1] = AES_D(C[i+1]) XOR C[i]' – dokładnie te bity z P[i+1] są zniszczone, które są inne w C[i]' vs C[i].
- P[i+2], P[i+3], … są prawidłowe (C[i+1] jest nienaruszony).

**Podsumowanie: 2 bloki uszkodzone, w tym jeden całkowicie.**

---

## Tryb OFB (Output Feedback)

### Jak działa?

Generuje **strumień klucza (keystream)** niezależny od tekstu jawnego, a następnie XOR-uje go z danymi. Szyfr blokowy używany jest tylko do generowania keystroamu.

```
IV → [AES_E(K)] → O[0] → [AES_E(K)] → O[1] → [AES_E(K)] → O[2]
                    ↓                    ↓                    ↓
          P[0] → [XOR] → C[0]  P[1] → [XOR] → C[1]  P[2] → [XOR] → C[2]
```

### Wzory

```
Generowanie strumienia:
  O[0] = AES_E(K, IV)
  O[i] = AES_E(K, O[i-1])

Szyfrowanie:   C[i] = P[i] XOR O[i]
Deszyfrowanie: P[i] = C[i] XOR O[i]
```

### Właściwości

- Działa jak **synchroniczny szyfr strumieniowy** – keystream nie zależy od szyfrogramu.
- Szyfrowanie = deszyfrowanie (ta sama operacja XOR).
- Nie wymaga paddingu – można szyfrować dane o dowolnej długości.
- Generowanie keystroamu jest **sekwencyjne** (O[i] zależy od O[i-1]).
- Wadą jest wrażliwość na ponowne użycie (IV, klucz) – ta sama para (IV, K) generuje ten sam keystream, co ujawnia XOR dwóch tekstów jawnych.

### Propagacja błędów

Błąd w C[i] → dokładnie te same bity są zniszczone w P[i] (operacja XOR). Keystream O jest niezależny od szyfrogramu, więc **żadna zmiana w C[i] nie wpływa na O[i+1], O[i+2], …** – pozostałe bloki tekstu jawnego są nieuszkodzone.

**Podsumowanie: propagacja bitowa, tylko zmienione bity w jednym bloku.**

---

## Tryb CFB (Cipher Feedback)

### Jak działa?

Podobny do OFB, ale keystream generowany jest z poprzedniego **szyfrogramu** (nie z keystroamu). W wariancie CFB128 (pełnoblokowym):

```
IV → [AES_E(K)] → XOR → C[0] → [AES_E(K)] → XOR → C[1]
                   ↑                           ↑
                  P[0]                        P[1]
```

### Wzory (CFB128)

```
Szyfrowanie:  C[0] = AES_E(K, IV) XOR P[0]
              C[i] = AES_E(K, C[i-1]) XOR P[i]

Deszyfrowanie: P[0] = AES_E(K, IV) XOR C[0]
               P[i] = AES_E(K, C[i-1]) XOR C[i]
```

Uwaga: deszyfrowanie używa **AES_E** (szyfrowania), nie AES_D – to wyróżnik CFB.

### Właściwości

- Nie wymaga paddingu.
- Szyfrowanie sekwencyjne (C[i] zależy od C[i-1]).
- Deszyfrowanie można zrównoleglić (wszystkie C[i-1] znane z góry).
- Istnieją warianty CFB8, CFB64, CFB128 różniące się rozmiarem segmentu feedback.

### Propagacja błędów

Błąd w C[i]:
- P[i] zostaje uszkodzony (XOR z błędnym AES_E(K, C[i-1]) jest poprawny, ale C[i] jest błędny → zniszczone bity 1:1).
- P[i+1] = AES_E(K, C[i]') XOR C[i+1] – AES_E(K, C[i]') daje losowy wynik → cały blok P[i+1] jest zniszczony.
- P[i+2] = AES_E(K, C[i+1]) XOR C[i+2] – C[i+1] jest nienaruszony → P[i+2] jest poprawny.

**Podsumowanie: 2 bloki uszkodzone, analogicznie do CBC.**

---

## Tryb CTR (Counter)

### Jak działa?

Generuje keystream przez szyfrowanie kolejnych wartości licznika. Licznik to konkatenacja nonce (jednorazowej wartości) i rosnącej wartości całkowitej.

```
[nonce||0] → [AES_E(K)] → O[0]
[nonce||1] → [AES_E(K)] → O[1]
[nonce||2] → [AES_E(K)] → O[2]
                ↓              ↓              ↓
      P[0] → [XOR] → C[0]  P[1] → [XOR] → C[1]  ...
```

### Wzory

```
O[i] = AES_E(K, nonce || i)
C[i] = P[i] XOR O[i]
P[i] = C[i] XOR O[i]
```

### Właściwości

- **Całkowita paralolelizacja** – każdy blok keystroamu niezależny → idealne do sprzętowej akceleracji.
- Szyfrowanie = deszyfrowanie.
- Nie wymaga paddingu.
- Umożliwia **losowy dostęp** do dowolnego bloku bez deszyfrowania całości.
- Nonce musi być unikalny dla każdej wiadomości przy tym samym kluczu.

### Propagacja błędów

Taka sama jak OFB – błąd w C[i] niszczy dokładnie zmienione bity w P[i], reszta jest nienaruszona.

**Podsumowanie: propagacja bitowa, tylko zmienione bity w jednym bloku.**

---

## Porównanie wszystkich trybów

| Cecha                     | ECB | CBC | OFB | CFB | CTR |
|---------------------------|-----|-----|-----|-----|-----|
| Potrzebuje IV/nonce       | nie | tak | tak | tak | tak |
| Wymaga paddingu           | tak | tak | nie | nie | nie |
| Szyfrowanie sekwencyjne   | nie | tak | tak | tak | nie |
| Deszyfrowanie równoległe  | tak | tak | nie | tak | tak |
| Propagacja błędu          | 1 blok | 2 bloki | 1 bajt | 2 bloki | 1 bajt |
| Bezpieczeństwo semantyczne| nie | tak | tak | tak | tak |
| Losowy dostęp             | tak | nie | nie | nie | tak |

---

## Padding (dopełnienie) – PKCS#7

Tryby ECB i CBC wymagają, by dane miały długość będącą wielokrotnością rozmiaru bloku. Standardem jest PKCS#7: brakujące bajty wypełnia się wartością równą liczbie brakujących bajtów.

```
Dane: [A][B][C]  (3 bajty, blok = 4 bajty)
Po paddingu: [A][B][C][01]

Dane: [A][B]     (2 bajty)
Po paddingu: [A][B][02][02]

Dane: [A][B][C][D]  (4 bajty, równo)
Po paddingu: [A][B][C][D][04][04][04][04]  ← zawsze dodajemy blok
```

Uwaga: jeśli dane mają już długość będącą wielokrotnością bloku, PKCS#7 dodaje **pełny dodatkowy blok** (żeby odróżnić dane od paddingu).

---

## Implementacja CBC na bazie ECB – krok po kroku

CBC szyfrowania to dokładnie:
1. Dopełnij tekst jawny do wielokrotności rozmiaru bloku.
2. Dla każdego bloku P[i]:
   - XOR P[i] z poprzednim szyfrogramem C[i-1] (lub IV dla i=0).
   - Zaszyfruj wynik trybem ECB → to jest C[i].

```
P[0] = b'Testowa wiadomosc'  (16 B)
IV   = losowe 16 B

krok 1: blok = P[0] XOR IV
krok 2: C[0] = AES_ECB_Encrypt(key, blok)

krok 1: blok = P[1] XOR C[0]
krok 2: C[1] = AES_ECB_Encrypt(key, blok)
...
```

Deszyfrowanie jest symetrycznie odwrotne:
1. Dla każdego bloku C[i]:
   - Odszyfruj C[i] trybem ECB → wynik pośredni.
   - XOR z C[i-1] (lub IV) → P[i].

---

## Wnioski

1. **Nigdy nie używaj ECB do szyfrowania danych dłuższych niż jeden blok** – brak dyfuzji między blokami ujawnia wzorce w tekście jawnym.

2. **CBC jest klasycznym wyborem**, ale szyfrowanie jest sekwencyjne i wymaga poprawnej obsługi IV (musi być losowy, nie może się powtarzać).

3. **CTR to najszybszy tryb z prawdziwą równoległością** – w benchmarku osiągnął czas zbliżony do ECB przy zachowaniu bezpieczeństwa semantycznego. Idealny do dużych wolumenów danych.

4. **OFB i CFB** są historyczne – CTR jest ich nowoczesnym zamiennikiem z lepszą paralolelizacją i prostszą implementacją.

5. **Tryby strumieniowe (OFB, CTR)** wykazują korzystniejszą propagację błędów (1 bajt) – utrata lub przekłamanie jednego bajtu szyfrogramu niszczy tylko ten bajt w tekście jawnym. W trybach blokowych z łańcuchem (CBC, CFB) błąd propaguje się na dwa bloki.

6. **Implementacja CBC przy użyciu ECB** doskonale ilustruje zasadę composability w kryptografii – złożone tryby można budować ze standardowych prymitywów.
