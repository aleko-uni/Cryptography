import random


# TODO - choose p, q
p = 7411
q = 4261
n = p * q
phi = (p - 1) * (q - 1)
# TODO - e is relatively prime to phi
e = 9497
# TODO - e*d przystaje do 1 mod phi
k = 1
while (k * phi + 1) % e != 0:
    k += 1

d = (k * phi + 1) // e

print("public key")
print(f"e: {e}\tn: {n}")
print("private key")
print(f"d: {d}\tn: {n}")
