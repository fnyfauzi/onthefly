import random, string

"""
print(random_char(5)) # fxkea
"""
def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for _ in range(y))
