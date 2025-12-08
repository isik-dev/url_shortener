import string
from secrets import choice

ALPHABET = string.ascii_letters + string.digits # should be of len = 62

def generate_random_slug():
    slug = ""
    for _ in range(6):
       slug += choice(ALPHABET)
    return slug