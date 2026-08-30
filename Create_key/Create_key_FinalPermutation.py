import random

def generate_P_B(min_P=1, max_P=100, B_margin=100):
    P = random.randint(min_P, max_P)
    min_B_threshold = 15 + 225 * P
    B = min_B_threshold + random.randint(1, B_margin)
    return P, B


P, B = generate_P_B()
print(f"Giá trị P = {P}")
print(f"Giá trị B = {B}")
print(f"Ngưỡng tối thiểu (15 + 225*P) = {15 + 225 * P}")
print(f"Kiểm tra B > 15 + 225*P: {B > 15 + 225 * P}")