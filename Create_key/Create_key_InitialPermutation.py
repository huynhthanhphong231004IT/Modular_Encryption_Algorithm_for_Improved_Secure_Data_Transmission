import sympy as sp
import numpy as np
import random

def is_primitive_root(g, p):
    if sp.gcd(g, p) != 1:
        return False
    phi = p - 1
    prime_factors = sp.primefactors(phi)
    for factor in prime_factors:
        if pow(g, phi // factor, p) == 1:
            return False
    return True

def find_primitive_root(p):
    for g in range(2, p):
        if is_primitive_root(g, p):
            return g
    return None

def generate_system_keys(min_p=256, max_p=1000):
    p = sp.randprime(min_p, max_p)
    g = find_primitive_root(p)
    while True:
        S_candidate = np.random.randint(0, p, size=(3, 3))
        det = int(round(np.linalg.det(S_candidate))) % p
        if det != 0:
            S = S_candidate
            break
    return p, g, S



p, g, S = generate_system_keys()
print(f"1. Số nguyên tố p = {p}")
print(f"2. Phần tử sinh g = {g}")
print("3. Ma trận khóa bí mật S (3x3):")
print(S)
det_S = int(round(np.linalg.det(S))) % p
print(f"-> det(S) mod {p} = {det_S}")