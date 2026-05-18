#!"C:\Python314\python.exe"

from random import randint

def pytaj_int(komunikat, wartosc_domyslna):
    odp = input(komunikat).strip()
    if odp == '':
        print(f'Automatycznie wybrano: "{wartosc_domyslna}"')
        return wartosc_domyslna
    try:
        return int(odp)
    except ValueError:
        print(f'Niepoprawna wartość "{odp}". Automatycznie wybrano: "{wartosc_domyslna}"')
        return wartosc_domyslna

def losuj_wspolczynniki(t):
    wspolczynniki = []
    for _ in range(t-1):
        wspolczynniki.append(randint(1,10))
    return wspolczynniki

def oblicz_f(wspolczynniki, x):
    f = 0
    for i in range(len(wspolczynniki)):
        f += x**i * wspolczynniki[-i]
    return f

def odtworz_sekret(odszyfrowujace_udzialy, p):
    odtworzony_sekret = 0
    punkty = list(odszyfrowujace_udzialy.items())
    for j in range(len(punkty)):
        xj, yj = punkty[j]
        licznik = 1
        mianownik = 1
        for m in range(len(punkty)):
            if m == j:
                continue
            xm = punkty[m][0]
            licznik = (licznik * (-xm)) % p
            mianownik = (mianownik * (xj - xm)) % p
        odtworzony_sekret = (odtworzony_sekret + yj * licznik * pow(mianownik, -1, p)) % p
    return odtworzony_sekret

def oblicz_udzialy(wspolczynniki, sekret, p, liczba_udzialow):
    udzialy = {}
    while len(udzialy) < liczba_udzialow:
        x = randint(-100, 100)
        if x == 0 or x in udzialy:
            continue
        udzialy[x] = (sekret + oblicz_f(wspolczynniki, x)) % p
    return udzialy

if __name__ == "__main__":
    liczba_udzialow = pytaj_int('Wybierz całkowitą liczbę udziałów: ', 7)
    wymagana_do_odtw = pytaj_int('Wybierz liczbę udziałów wymaganą do odtworzenia sekretu: ', 5)
    sekret = pytaj_int('Wybierz sekret: ', 64)
    pierwsza = pytaj_int('Wybierz liczbe pierwsza: ', 19)

    print(f'Wybrane wartości:\nLiczba udziałów: \t\t\t{liczba_udzialow}\nWymagana liczba do odtworzenia: \t{wymagana_do_odtw}\nSekret: \t\t\t\t{sekret}\nLiczba pierwsza: \t\t\t{pierwsza}\n')

    wspolczynniki = losuj_wspolczynniki(wymagana_do_odtw)
    print(f'Współczynniki: {wspolczynniki}')

    udzialy = oblicz_udzialy(wspolczynniki, sekret, pierwsza, liczba_udzialow)
    print(f'Udziały: {udzialy}')

    ile_odszyfrowujacych_udzialy = pytaj_int(f'Ile udziałowców chciałbyś podać?: ', wymagana_do_odtw)
    odszyfrowujace_udzialy = {}
    for i in range(ile_odszyfrowujacych_udzialy):
        x = pytaj_int(f'Podaj x udziału {i+1}: ', 0)
        y = pytaj_int(f'Podaj y udziału {i+1}: ', 0)
        odszyfrowujace_udzialy[x] = y

    print(f'Podane udziały: {odszyfrowujace_udzialy}')

    odtworzony_sekret = odtworz_sekret(odszyfrowujace_udzialy, pierwsza)
    print(f'Odtworzony sekret: {odtworzony_sekret}')

