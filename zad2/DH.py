import sympy

def shared_numbers():
    p = sympy.randprime(5000, 9999)
    g = sympy.randprime(2, 100)
    return p, g

def A_chooses(p, g):
    a = sympy.randprime(1000, 9999)
    A = pow(g, a, p)
    return a, A

def B_chooses(p, g):
    b = sympy.randprime(1000, 9999)
    B = pow(g, b, p)
    return b, B

def A_computes_shared_secret(B, a, p):
    return pow(B, a, p)

def B_computes_shared_secret(A, b, p):
    return pow(A, b, p)

if __name__ == "__main__":
    p, g = shared_numbers()
    print(f"Shared numbers: p={p}, g={g}")

    a, A = A_chooses(p, g)
    print(f"A chooses: a={a}, A={A}")

    b, B = B_chooses(p, g)
    print(f"B chooses: b={b}, B={B}")

    shared_secret_A = A_computes_shared_secret(B, a, p)
    shared_secret_B = B_computes_shared_secret(A, b, p)

    print(f"A computes shared secret: {shared_secret_A}")
    print(f"B computes shared secret: {shared_secret_B}")

    assert shared_secret_A == shared_secret_B, "Shared secrets do not match!"
    print("Shared secrets match. Key exchange successful.")
