import random

def plus_or_minus(amount: int):
    return amount if random.random() <= .5 else -amount

def calculate_new_price(current_price: int):
    rand = random.random()
    if rand <= 0.0001:
        current_price += plus_or_minus(20)
    elif rand <= 0.001:
        current_price += plus_or_minus(5)
    else:
        current_price += plus_or_minus(random.randint(0, 1))
    
    current_price = 0 if current_price < 0 else current_price
    return current_price